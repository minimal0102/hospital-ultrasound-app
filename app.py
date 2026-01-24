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
# 2. 核心功能函數
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

    # --- 高對比 CSS 注入 ---
    st.markdown("""
        <style>
        /* 全域設定 */
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        .main-title { text-align: center; font-weight: 900; font-size: 2rem; color: #000000; margin-bottom: 25px; }

        /* 資訊卡片滿版設計 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .info-card {
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 30px 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .border-blue { border-top: 10px solid #60A5FA; }
        .border-red { border-top: 10px solid #F87171; }
        .label-text { font-size: 16px; color: #8E8E93; font-weight: 800; display: block; margin-bottom: 5px; }
        .value-text { font-size: 32px; font-weight: 900; color: #000000; display: block; }

        /* 按鈕基礎樣式：置中、20px、純黑粗體 900 */
        div[data-testid="stFormSubmitButton"] { text-align: center; }
        
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            border-radius: 16px !important;
            padding: 20px 0 !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transition: transform 0.1s ease;
        }
        div[data-testid="stFormSubmitButton"] > button:active { transform: scale(0.98); }

        /* 登記按鈕顏色控制 */
        .borrow-area div[data-testid="stFormSubmitButton"] > button {
            background-color: #60A5FA !important;
        }

        /* 歸還按鈕顏色控制 */
        .return-area div[data-testid="stFormSubmitButton"] > button {
            background-color: #F87171 !important;
        }
        
        /* 隱藏預設元件 */
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🏥 內科超音波登記站</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 情境 A：借出模式
    # ------------------------------------------
    if current_status == "可借用":
        st.success("### ✅ 設備在位中 (可借用)")
        
        # 使用 div 包裹以便 CSS 針對性控制按鈕顏色
        st.markdown('<div class="borrow-area">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
            user = st.selectbox("借用人", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            st.write("")
            if st.form_submit_button("🚀 登記並推走設備"):
                if loc == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role, "借用人": user, "借用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": "一般檢查", "所在位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 情境 B：歸還模式
    # ------------------------------------------
    else:
        last_row = df.iloc[-1]
        st.error("### ⚠️ 設備目前使用中")

        # 資訊儀表板：滿版置中
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="info-card border-blue">
                <span class="label-text">👤 借用人</span>
                <span class="value-text">{last_row['借用人']}</span>
            </div>
            <div class="info-card border-red">
                <span class="label-text">📍 目前位置</span>
                <span class="value-text">{last_row['所在位置']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="return-area">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.info(f"借出時間：{last_row['借用時間']}")
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常", value=False)
            st.write("")
            if st.form_submit_button("📦 確認歸還設備"):
                if not check:
                    st.warning("⚠️ 請勾選確認設備已檢查清消")
                else:
                    now = get_taiwan_time()
                    df.at[last_idx, "狀態"] = "歸還"
                    df.at[last_idx, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 歷史紀錄 ---
    if not df.empty:
        with st.expander("📊 查看歷史紀錄統計"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
