#!/bin/bash

# GPX Viewer アプリケーション起動スクリプト

echo "GPX Viewer を起動しています..."
cd "$(dirname "$0")"

# 仮想環境をアクティベート
source .venv/bin/activate

# Streamlitアプリケーションを実行
streamlit run app.py
