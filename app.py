import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 資料與設定
# ==========================================
FILE_NAME = 'ultrasound_log.csv'
DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"]
ALL_STAFF = DOCTORS + NPS
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
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    df = load_data()
    current_status = "可借用"
    last_idx = None
    
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_idx = df.index[-1]

    # --- 強效 CSS 注入 ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        h1 { text-align: center; font-weight: 900 !important; color: #000000; margin-bottom: 20px; }
        
        /* 資訊卡片修復 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .info-card {
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 25px 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .border-blue { border-top: 8px solid #60A5FA; }
        .border-red { border-top: 8px solid #F87171; }
        .label { font-size: 16px; color: #8E8E93; font-weight: 800; margin-bottom: 8px; display: block; }
        .value { font-size: 28px; font-weight: 900; color: #000000; display: block; }

        /* 全域按鈕基礎設定 */
        div.stButton > button {
            width: 100% !important;
            border-radius: 16px !important;
            padding: 20px 0 !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            color: #000000 !important; /* 強制黑字 */
            border: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🏥 內科超音波登記站</h1>", unsafe_allow_html=True)

    if current_status == "可借用":
        # 🟢 登記按鈕顏色控制
        st.markdown("<style>div.stButton > button { background-color: #60A5FA !important; }</style>", unsafe_allow_html=True)
        st.success("### ✅ 設備在位中")
        
        with st.form("borrow_form"):
            role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
            user = st.selectbox("借用人", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇..."] + UNIT_LIST)
            if st.form_submit_button("🚀 登記並推走設備"):
                if loc == "請選擇...":
                    st.error("請選擇單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role, "借用人": user, "借用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": "一般檢查", "所在位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()

    else:
        # 🔴 歸還按鈕顏色控制
        st.markdown("<style>div.stButton > button { background-color: #F87171 !important; }</style>", unsafe_allow_html=True)
        last_row = df.iloc[-1]
        
        st.error("### ⚠️ 設備使用中")

        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="info-card border-blue">
                <span class="label">👤 借用人</span>
                <span class="value">{last_row['借用人']}</span>
            </div>
            <div class="info-card border-red">
                <span class="label">📍 目前位置</span>
                <span class="value">{last_row['所在位置']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("return_form"):
            st.write(f"借出時間：{last_row['借用時間']}")
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            if st.form_submit_button("📦 確認歸還設備"):
                if not check:
                    st.warning("請勾選清潔項目")
                else:
                    now = get_taiwan_time()
                    df.at[last_idx, "狀態"] = "歸還"
                    df.at[last_idx, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    save_data(df)
                    st.rerun()

    # --- 歷史紀錄 ---
    with st.expander("📊 歷史紀錄"):
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
