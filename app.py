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
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]

# ==========================================
# 2. 核心功能函數
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["狀態", "職稱", "借用人", "借用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"])
        df.to_csv(FILE_NAME, index=False)
        return df
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ==========================================
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    df = load_data()
    current_status = "可借用"
    last_record_index = None
    
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_record_index = df.index[-1]

    # --- 全局 Apple 風格 CSS ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; font-family: -apple-system, sans-serif; }
        h1 { text-align: center; font-weight: 800; }
        .apple-card { background-color: #FFFFFF; padding: 24px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 20px; }
        
        /* 資訊儀表板方塊 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .dashboard-box { background-color: #E5E7EB; border-radius: 12px; padding: 20px 10px; text-align: center; border: 1px solid #D1D5DB; }
        .dashboard-label { font-size: 13px; color: #6B7280; font-weight: 600; }
        .dashboard-value { font-size: 24px; font-weight: 800; color: #000; }

        /* 按鈕基礎強制設定：滿版、粗體黑字 */
        div.stButton > button {
            width: 100% !important;
            display: block !important;
            border-radius: 12px !important;
            padding: 18px 0 !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            color: #000000 !important;
            border: 2px solid rgba(0,0,0,0.1) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>內科超音波 登記站</h1>", unsafe_allow_html=True)

    # ==========================================
    # 狀態 A：可借用 (藍按鈕)
    # ==========================================
    if current_status == "可借用":
        # 注入登記專用藍色 CSS
        st.markdown("<style>div.stButton > button { background-color: #60A5FA !important; }</style>", unsafe_allow_html=True)
        
        st.markdown('<div style="background-color:#D1FAE5; color:#065F46; padding:15px; border-radius:12px; text-align:center; font-size:24px; font-weight:800; border:2px solid #6EE7B7; margin-bottom:20px;">🟢 可借用</div>', unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        role_select = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            c1, c2 = st.columns(2)
            with c1: user = st.selectbox("借用人", current_name_list)
            with c2: reason = st.selectbox("使用部位", BODY_PARTS)
            location = st.selectbox("移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            
            submit = st.form_submit_button("🚀 登記推走設備") # 藍底黑字
            
            if submit:
                if location == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role_select, "借用人": user, "借用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": reason, "所在位置": location, "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 狀態 B：使用中 (紅按鈕)
    # ==========================================
    else:
        # 注入歸還專用紅色 CSS
        st.markdown("<style>div.stButton > button { background-color: #F87171 !important; }</style>", unsafe_allow_html=True)
        
        last = df.iloc[-1]
        st.markdown('<div style="background-color:#FEE2E2; color:#991B1B; padding:15px; border-radius:12px; text-align:center; font-size:24px; font-weight:800; border:2px solid #FCA5A5; margin-bottom:20px;">🔴 使用中</div>', unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        # 資訊儀表板方塊
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-box"><div class="dashboard-label">👤 使用者</div><div class="dashboard-value">{last['借用人']}</div></div>
            <div class="dashboard-box"><div class="dashboard-label">📍 目前位置</div><div class="dashboard-value" style="font-size:32px;">{last['所在位置']}</div></div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("return_form"):
            returner = st.selectbox("歸還人", ALL_STAFF, index=ALL_STAFF.index(last['借用人']) if last['借用人'] in ALL_STAFF else 0)
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            submit_ret = st.form_submit_button("📦 確認歸還設備") # 紅底黑字
            
            if submit_ret:
                if not check:
                    st.error("⚠️ 請確認設備完整性")
                else:
                    now = get_taiwan_time()
                    start = datetime.strptime(last["借用時間"], "%Y-%m-%d %H:%M:%S")
                    dur = round((now.replace(tzinfo=None) - start).total_seconds() / 60, 1)
                    df.at[last_record_index, "狀態"] = "歸還"
                    df.at[last_record_index, "歸還人"] = returner
                    df.at[last_record_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_record_index, "持續時間(分)"] = dur
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
