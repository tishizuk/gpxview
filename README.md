# GPX Viewer

PythonのStreamlitを使用したGPXファイルビューアアプリケーションです。GPXファイルをアップロードして、地図上で経路を表示し、統計情報を確認できます。

## 機能

- 📁 GPXファイルのアップロード
- 🗺️ インタラクティブな地図での経路表示
- 📊 統計情報（距離、標高、所要時間など）
- 📍 スタート/ゴール地点のマーカー表示
- 📋 トラックポイントのデータテーブル表示

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. アプリケーションの実行

```bash
streamlit run app.py
```

## 使用方法

1. ブラウザで `http://localhost:8501` にアクセス
2. サイドバーからGPXファイルをアップロード
3. 地図上で経路を確認
4. 統計情報とトラックポイントの詳細を確認

## サポートファイル形式

- **GPX** (.gpx) - GPS Exchange Format

## 依存関係

- streamlit - Webアプリケーションフレームワーク
- folium - インタラクティブマップライブラリ
- streamlit-folium - StreamlitとFoliumの統合
- gpxpy - GPXファイル解析ライブラリ
- pandas - データ操作ライブラリ

## ライセンス

MIT License
