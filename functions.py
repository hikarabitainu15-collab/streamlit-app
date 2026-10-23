from pathlib import Path

import sqlite3
import streamlit as st
import json

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data"

#外部データ読み込み
@st.cache_data
def load_json(file_name):
    load_path = DATA_PATH / f"{file_name}"
    with open(load_path, "r", encoding="utf-8") as f:
        return json.load(f)

#技能リスト情報ファイルを読み込む
@st.cache_data
def load_skills_list_json(skill):
    load_path = DATA_PATH / "skills_list.json"
    with open(load_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data[skill]

#データベース接続関数
def get_connection():
    return sqlite3.connect("save_data.db")


