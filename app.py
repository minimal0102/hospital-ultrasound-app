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
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["狀態", "職稱", "借用人", "借用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"])
        df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
        return df
    try:
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        return df
    except:
        return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')

# ==========================================
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    df = load_data()
    current_status = "可借用"
    last_record_index = None
    
    if not df.empty:
        last_row = df.iloc[-1]
        if last_row["狀態"] == "借出":
            current_status = "使用中"
            last_record_index = df.index[-1]

    # --- 高對比 CSS 注入 ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        
        /* 標題加粗置中 */
        h1 { text-align: center; font-weight: 900 !important; color: #000000; font-size: 2.2rem; margin-bottom: 25px; }

        /* 卡片設計 */
        .apple-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* 儀表板方塊 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px; }
        .dashboard-box { 
            border-radius: 16px; 
            padding: 20px 10px; 
            text-align: center; 
        }
        .box-blue { background-color: #E1EFFF; border: 1px solid #60A5FA; }
        .box-red { background-color: #FFEBEE; border: 1px solid #F87171; }
        
        .dashboard-label { font-size: 14px; color: #48484A; font-weight: 700; margin-bottom: 5px; }
        .dashboard-value { font-size: 24px; font-weight: 900; color: #000000; }
        
        /* 按鈕核心樣式：置中放大、極粗純黑字 */
        div.stButton > button {
            width: 100% !important;
            border-radius: 14px !important;
            padding: 20px 0 !important;
            font-size: 24px !important;  /* 字體放大 */
            font-weight: 900 !important; /* 極粗體 */
            color: #000000 !important;   /* 純黑字 */
            border: none !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
            transition: all 0.1s ease;
        }
        
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🏥 內科超音波 登記站</h1>", unsafe_allow_html=True)

    # ==========================================
    # 情境 A：借出模式
    # ==========================================
    if current_status == "可借用":
        # 登記按鈕顏色：亮藍色底 (#60A5FA)
        st.markdown("<style>div.stButton > button { background-color: #60A5FA !important; }</style>", unsafe_allow_html=True)
        
        st.markdown('<div style="background-color:#EBFBEE; color:#28CD41; padding:15px; border-radius:12px; text-align:center; font-size:20px; font-weight:900; border:1px solid #D3F4D8; margin-bottom:20px;">🟢 設備在位中 (可借用)</div>', unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        role_select = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            c1, c2 = st.columns(2)
            with c1:
                user = st.selectbox("借用人", current_name_list)
            with c2:
                reason = st.selectbox("使用部位", BODY_PARTS)
            
            location = st.selectbox("移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            st.write("")
            submit = st.form_submit_button("🚀 登記推走設備")
            
            if submit:
                if location == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位")
                else:
                    tw_now = get_taiwan_time()
                    new_rec = {"狀態": "借出", "職稱": role_select, "借用人": user, "借用時間": tw_now.strftime("%Y-%m-%d %H:%M:%S"), "使用部位": reason, "所在位置": location, "歸還人": None, "歸還時間": None, "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 情境 B：歸還模式
    # ==========================================
    else:
        # 歸還按鈕顏色：亮紅色底 (#F87171)
        st.markdown("<style>div.stButton > button { background-color: #F87171 !important; }</style>", unsafe_allow_html=True)
        
        last_user = df.iloc[-1]["借用人"]
        last_loc = df.iloc[-1]["所在位置"]
        last_time = df.iloc[-1]["借用時間"]

        st.markdown('<div style="background-color:#FFF5F5; color:#FF3B30; padding:15px; border-radius:12px; text-align:center; font-size:20px; font-weight:900; border:1px solid #FFD1D3; margin-bottom:20px;">🔴 設備使用中</div>', unsafe_allow_html=True)

        # 資訊儀表板 (左邊使用者，右邊位置)
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-box box-blue">
                <div class="dashboard-label">👤 借用人</div>
                <div class="dashboard-value">{last_user}</div>
            </div>
            <div class="dashboard-box box-red">
                <div class="dashboard-label">📍 目前位置</div>
                <div class="dashboard-value" style="font-size:32px;">{last_loc}</div>
            </div>
        </div>
        <div style="text-align:center; color:#8E8E93; font-size:13px; margin-bottom:15px;">借出時間：{last_time}</div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        with st.form("return_form"):
            returner = st.selectbox("歸還人", ALL_STAFF, index=ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0)
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常", value=False)
            st.write("")
            submit_ret = st.form_submit_button("📦 確認歸還設備")
            
            if submit_ret:
                if not check:
                    st.error("⚠️ 請勾選確認檢查設備")
                else:
                    now = get_taiwan_time()
                    start = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                    dur = round((now.replace(tzinfo=None) - start).total_seconds() / 60, 1)
                    df.at[last_record_index, "狀態"] = "歸還"
                    df.at[last_record_index, "歸還人"] = returner
                    df.at[last_record_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_record_index, "持續時間(分)"] = dur
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 歷史統計 ---
    if not df.empty:
        with st.expander("📊 查看紀錄統計"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            st.download_button("📥 下載 CSV 備份", df.to_csv(index=False).encode('utf-8-sig'), "ultrasound_backup.csv", "text/csv")

if __name__ == "__main__":
    main()
