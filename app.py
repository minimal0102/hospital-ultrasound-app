import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 資料與設定
# ==========================================

FILE_NAME = 'ultrasound_log.csv'

# 名單資料
DOCTORS = [
    "朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", 
    "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", 
    "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", 
    "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", 
    "李坤峰", "何承恩", "沈治華", "PGY醫師"
]

NPS = [
    "侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", 
    "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", 
    "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", 
    "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"
]

ALL_STAFF = DOCTORS + NPS

BODY_PARTS = [
    "胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", 
    "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"
]

UNIT_LIST = [
    "3A", "3B", "5A", "5B", "6A", "6B", 
    "7A", "7B", "RCC", "6D", "6F", "檢查室"
]

# ==========================================
# 2. 核心功能函數
# ==========================================

def get_taiwan_time():
    utc_dt = datetime.now(timezone.utc)
    tw_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return tw_dt

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "狀態", "職稱", "借用人", "借用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"
        ])
        df.to_csv(FILE_NAME, index=False)
        return df
    df = pd.read_csv(FILE_NAME)
    if "職稱" not in df.columns: df["職稱"] = "未分類" 
    return df

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ==========================================
# 3. 主程式介面
# ==========================================

def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    # 讀取資料
    df = load_data()
    
    current_status = "可借用"
    last_record_index = None
    
    if not df.empty:
        last_row = df.iloc[-1]
        if last_row["狀態"] == "借出":
            current_status = "使用中"
            last_record_index = df.index[-1]

    # ==========================================
    # 🔥 CSS 全局基礎設定 🔥
    # ==========================================
    st.markdown("""
        <style>
        /* 1. iOS 背景色 */
        [data-testid="stAppViewContainer"] {
            background-color: #F2F2F7 !important;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* 2. 文字顏色 */
        h1, h2, h3, p, div, span, label {
            color: #1C1C1E;
        }

        /* 3. 卡片容器 (White Card) */
        .apple-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            margin-bottom: 20px;
        }

        /* 4. 輸入框與選單優化 */
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: #F2F2F7 !important;
            border: none !important;
            border-radius: 10px !important;
            color: #1C1C1E !important;
            font-size: 16px !important;
        }
        
        /* 5. 狀態標籤 */
        .status-badge {
            padding: 15px;
            border-radius: 12px;
            font-size: 24px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* 6. 資訊儀表板 (歸還頁面專用) */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .dashboard-box {
            background-color: #E5E7EB; /* 淺灰底 */
            border-radius: 12px;
            padding: 20px 10px;
            text-align: center;
            border: 1px solid #D1D5DB;
        }
        .dashboard-label {
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .dashboard-value {
            font-size: 22px;
            font-weight: 800;
            color: #000000;
            line-height: 1.2;
        }
        .dashboard-value-large {
            font-size: 32px; /* 位置字體超大 */
            font-weight: 900;
            color: #000000;
            line-height: 1.2;
        }

        /* 隱藏預設 */
        #MainMenu, footer, header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    # 頁面標題
    st.markdown("<h1 style='text-align:center; font-weight:800; margin-bottom:10px;'>內科超音波 登記站</h1>", unsafe_allow_html=True)

    # ==========================================
    # 情境 A：借出模式 (藍色系)
    # ==========================================
    if current_status == "可借用":
        # ===
