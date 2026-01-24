import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 資料與設定
# ==========================================
FILE_NAME = 'ultrasound_log.csv'

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"]
ALL_STAFF = DOCTORS + NPS
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]

# ==========================================
# 2. 核心功能
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["狀態", "職稱", "借用人", "借用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"])
        df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
        return df
    return pd.read_csv(FILE_NAME, encoding='utf-8-sig')

def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')

# ==========================================
# 3. 主頁面介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    df = load_data()
    
    # 判斷狀態
    current_status = "可借用"
    last_idx = None
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_idx = df.index[-1]

    # Apple 風格 CSS
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        .apple-card { background: white; padding: 20px; border-radius: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h1 { font-weight: 800; text-align: center; color: #1C1C1E; }
        div.stButton > button { width: 100%; border-radius: 12px; height: 3em; font-size: 1.1rem; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🏥 超音波登記站</h1>", unsafe_allow_html=True)

    if current_status == "可借用":
        st.success("🟢 目前狀態：設備在位")
        with st.container():
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
            names = DOCTORS if role == "醫師" else NPS
            
            with st.form("borrow_form"):
                user = st.selectbox("借用人", names)
                part = st.selectbox("使用部位", BODY_PARTS)
                loc = st.selectbox("前往單位", ["請選擇..."] + UNIT_LIST)
                st.write("")
                st.markdown("<style>div.stButton > button { background-color: #007AFF !important; color: white !important; }</style>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 確認借出"):
                    if loc == "請選擇...":
                        st.error("請選擇單位")
                    else:
                        new_row = {"狀態": "借出", "職稱": role, "借用人": user, "借用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "所在位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        last_user = df.iloc[-1]["借用人"]
        st.error(f"🔴 目前狀態：{last_user} 使用中")
        with st.container():
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            st.write(f"📍 **位置**：{df.iloc[-1]['所在位置']}")
            st.write(f"⏰ **開始時間**：{df.iloc[-1]['借用時間']}")
            
            with st.form("return_form"):
                returner = st.selectbox("歸還確認人", ALL_STAFF, index=ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0)
                clean = st.checkbox("探頭已清潔且線材已收納")
                st.write("")
                st.markdown("<style>div.stButton > button { background-color: #FF3B30 !important; color: white !important; }</style>", unsafe_allow_html=True)
                if st.form_submit_button("📦 確認歸還"):
                    if not clean:
                        st.warning("請先完成清潔並勾選確認")
                    else:
                        now = get_taiwan_time()
                        start_t = datetime.strptime(df.iloc[-1]["借用時間"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                        dur = round((now - start_t).total_seconds() / 60, 1)
                        df.at[last_idx, "狀態"] = "歸還"
                        df.at[last_idx, "歸還人"] = returner
                        df.at[last_idx, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        df.at[last_idx, "持續時間(分)"] = dur
                        save_data(df)
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- 歷史統計紀錄 ---
    if not df.empty:
        with st.expander("📊 查看紀錄統計"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            st.download_button("📥 下載 CSV 備份", df.to_csv(index=False).encode('utf-8-sig'), "ultrasound_backup.csv", "text/csv")

if __name__ == "__main__":
    main()
