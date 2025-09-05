import streamlit as st
import folium
from streamlit_folium import st_folium
import gpxpy
import pandas as pd
import tempfile
import os

def parse_gpx_file(gpx_file):
    """GPXファイルを解析して、トラックポイントのリストを返す"""
    gpx = gpxpy.parse(gpx_file)
    
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time
                })
    
    return points

def create_map(points):
    """ポイントから地図を作成"""
    if not points:
        return None
    
    # 中心点を計算
    center_lat = sum(p['latitude'] for p in points) / len(points)
    center_lon = sum(p['longitude'] for p in points) / len(points)
    
    # 地図を作成
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # 経路をラインで描画
    coordinates = [[p['latitude'], p['longitude']] for p in points]
    
    folium.PolyLine(
        coordinates,
        weight=3,
        color='red',
        opacity=0.8,
        popup='GPX Route'
    ).add_to(m)
    
    # スタート地点にマーカーを追加
    if points:
        folium.Marker(
            [points[0]['latitude'], points[0]['longitude']],
            popup='スタート地点',
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # ゴール地点にマーカーを追加
        folium.Marker(
            [points[-1]['latitude'], points[-1]['longitude']],
            popup='ゴール地点',
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
    
    return m

def calculate_stats(points):
    """統計情報を計算"""
    if not points:
        return {}
    
    # 距離計算（簡易版）
    total_distance = 0
    for i in range(1, len(points)):
        lat1, lon1 = points[i-1]['latitude'], points[i-1]['longitude']
        lat2, lon2 = points[i]['latitude'], points[i]['longitude']
        
        # ハーバーサイン公式による距離計算
        import math
        R = 6371000  # 地球の半径（メートル）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        total_distance += distance
    
    # 標高データがある場合の統計
    elevations = [p['elevation'] for p in points if p['elevation'] is not None]
    
    stats = {
        'total_distance': total_distance / 1000,  # km
        'total_points': len(points),
    }
    
    if elevations:
        stats.update({
            'min_elevation': min(elevations),
            'max_elevation': max(elevations),
            'elevation_gain': max(elevations) - min(elevations)
        })
    
    # 時間データがある場合
    times = [p['time'] for p in points if p['time'] is not None]
    if len(times) > 1:
        duration = times[-1] - times[0]
        stats['duration'] = str(duration)
    
    return stats

def main():
    st.set_page_config(
        page_title="GPX Viewer",
        page_icon="🗺️",
        layout="wide"
    )
    
    st.title("🗺️ GPX File Viewer")
    st.markdown("GPXファイルをアップロードして、地図上で経路を表示します。")
    
    # サイドバーでファイルアップロード
    with st.sidebar:
        st.header("📁 ファイルアップロード")
        uploaded_file = st.file_uploader(
            "GPXファイルを選択してください",
            type=['gpx'],
            help="GPX形式のファイルのみサポートしています"
        )
        
        if uploaded_file is not None:
            st.success(f"ファイル '{uploaded_file.name}' がアップロードされました！")
    
    if uploaded_file is not None:
        try:
            # GPXファイルを解析
            with st.spinner("GPXファイルを解析中..."):
                points = parse_gpx_file(uploaded_file)
            
            if not points:
                st.error("GPXファイルに有効なトラックデータが見つかりません。")
                return
            
            # 統計情報を計算
            stats = calculate_stats(points)
            
            # メインエリアを2列に分割
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🗺️ 経路地図")
                
                # 地図を作成して表示
                map_obj = create_map(points)
                if map_obj:
                    st_folium(map_obj, width=700, height=500)
            
            with col2:
                st.subheader("📊 統計情報")
                
                # 統計情報を表示
                st.metric("総距離", f"{stats.get('total_distance', 0):.2f} km")
                st.metric("ポイント数", f"{stats.get('total_points', 0):,}")
                
                if 'min_elevation' in stats:
                    st.metric("最低標高", f"{stats['min_elevation']:.1f} m")
                    st.metric("最高標高", f"{stats['max_elevation']:.1f} m")
                    st.metric("標高差", f"{stats['elevation_gain']:.1f} m")
                
                if 'duration' in stats:
                    st.metric("所要時間", stats['duration'])
                
                # データテーブル（最初の10ポイント）
                st.subheader("📍 トラックポイント（最初の10ポイント）")
                df = pd.DataFrame(points[:10])
                if not df.empty:
                    # 時間列がある場合はフォーマット
                    if 'time' in df.columns and df['time'].notna().any():
                        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 数値列を小数点以下6桁に制限
                    for col in ['latitude', 'longitude']:
                        if col in df.columns:
                            df[col] = df[col].round(6)
                    
                    if 'elevation' in df.columns:
                        df['elevation'] = df['elevation'].round(1)
                    
                    st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("GPXファイルの形式を確認してください。")
    
    else:
        st.info("👆 サイドバーからGPXファイルをアップロードしてください。")
        
        # 使用方法の説明
        st.markdown("""
        ## 📖 使用方法
        
        1. 左のサイドバーから **GPXファイル** をアップロードします
        2. ファイルが解析され、地図上に経路が表示されます
        3. 右側のパネルで統計情報やトラックポイントの詳細を確認できます
        
        ### 📋 サポート機能
        - ✅ GPXファイルの解析と可視化
        - ✅ インタラクティブな地図表示
        - ✅ 距離、標高、時間の統計情報
        - ✅ スタート/ゴール地点のマーカー表示
        - ✅ トラックポイントのデータテーブル表示
        
        ### 📄 サポートファイル形式
        - **GPX** (.gpx) - GPS Exchange Format
        """)

if __name__ == "__main__":
    main()
