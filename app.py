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
        return pd.read_csv(FILE_NAME, encoding='utf-8-sig')
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

    # --- Apple 高對比視覺 CSS ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        
        /* 標題設計 */
        h1 { text-align: center; font-weight: 900; color: #1C1C1E; margin-bottom: 20px; }

        /* 卡片設計 */
        .apple-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 20px;
        }

        /* 儀表板方塊 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
        .dashboard-box { 
            border-radius: 16px; 
            padding: 20px 10px; 
            text-align: center; 
            background-color: #F2F2F7;
        }
        .dashboard-label { font-size: 14px; color: #8E8E93; font-weight: 700; margin-bottom: 5px; }
        .dashboard-value { font-size: 24px; font-weight: 900; color: #000000; }
        
        /* 核心按鈕樣式修改 */
        div.stButton > button {
            width: 100% !important;
            border-radius: 14px !important;
            padding: 18px 0 !important;
            font-size: 20px !important;  /* 置中放大 20px */
            font-weight: 900 !important; /* 極粗視覺效果 */
            color: #000000 !important;   /* 純黑字體 */
            border: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        }

        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🏥 內科超音波 登記站</h1>", unsafe_allow_html=True)

    # ==========================================
    # 情境 A：借出模式
    # ==========================================
    if current_status == "可借用":
        # 登記按鈕樣式：亮藍色底 (#60A5FA)
        st.markdown("<style>div.stButton > button { background-color: #60A5FA !important; }</style>", unsafe_allow_html=True)
        
        st.markdown('<div style="background-color:#D1FAE5; color:#065F46; padding:15px; border-radius:12px; text-align:center; font-size:22px; font-weight:900; border:2px solid #6EE7B7; margin-bottom:20px;">🟢 可借用 (設備在位)</div>', unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        role_select = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            c1, c2 = st.columns(2)
            with c1:
                user = st.selectbox("借用人", current_name_list)
            with c2:
                reason = st.selectbox("使用部位", BODY_PARTS)
            
            location = st.selectbox("前往單位", ["請選擇單位..."] + UNIT_LIST)
            st.write("")
            submit = st.form_submit_button("🚀 登記推走設備")
            
            if submit:
                if location == "請選擇單位...":
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
        # 歸還按鈕樣式：亮紅色底 (#F87171)
        st.markdown("<style>div.stButton > button { background-color: #F87171 !important; }</style>", unsafe_allow_html=True)
        
        last_user = df.iloc[-1]["借用人"]
        last_loc = df.iloc[-1]["所在位置"]
        last_time = df.iloc[-1]["借用時間"]

        st.markdown('<div style="background-color:#FEE2E2; color:#991B1B; padding:15px; border-radius:12px; text-align:center; font-size:22px; font-weight:900; border:2px solid #FCA5A5; margin-bottom:20px;">🔴 使用中</div>', unsafe_allow_html=True)

        # 資訊儀表板：放大顯示使用者與位置
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-box" style="border-left: 6px solid #60A5FA;">
                <div class="dashboard-label">👤 借用人</div>
                <div class="dashboard-value">{last_user}</div>
            </div>
            <div class="dashboard-box" style="border-left: 6px solid #F87171;">
                <div class="dashboard-label">📍 目前位置</div>
                <div class="dashboard-value" style="font-size:32px;">{last_loc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.write(f"借出時間：{last_time}")
            returner = st.selectbox("歸還確認人", ALL_STAFF, index=ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0)
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常", value=False)
            st.write("")
            submit_ret = st.form_submit_button("📦 確認歸還設備")
            
            if submit_ret:
                if not check:
                    st.warning("⚠️ 請勾選確認設備已完成清潔檢查")
                else:
                    now = get_taiwan_time()
                    start = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                    dur = round((now - start).total_seconds() / 60, 1)
                    df.at[last_record_index, "狀態"] = "歸還"
                    df.at[last_record_index, "歸還人"] = returner
                    df.at[last_record_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_record_index, "持續時間(分)"] = dur
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 歷史紀錄統計 ---
    if not df.empty:
        with st.expander("📊 查看紀錄統計"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            st.download_button("📥 下載數據備份", df.to_csv(index=False).encode('utf-8-sig'), "ultrasound_backup.csv", "text/csv")

if __name__ == "__main__":
    main()
