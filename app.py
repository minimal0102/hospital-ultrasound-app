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
    # 🔥 CSS 全局基礎設定 (Apple 風格) 🔥
    # ==========================================
    st.markdown("""
        <style>
        /* 1. iOS 背景色 */
        [data-testid="stAppViewContainer"] {
            background-color: #F2F2F7 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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
        # 🔥🔥🔥 強制注入：藍色按鈕 CSS (修正版) 🔥🔥🔥
        # 這裡的代碼只會在「可借用」時執行，保證按鈕變藍
        st.markdown("""
        <style>
        /* 針對表單內的按鈕進行強制樣式覆蓋 */
        div[data-testid="stForm"] button {
            background-color: #60A5FA !important; /* 亮藍色 */
            color: #000000 !important; /* 純黑字 */
            border: none !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            font-size: 20px !important;
            font-weight: 900 !important; /* 極粗 */
            text-align: center !important
            width: 100% !important; /* 滿版置中 */
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        div[data-testid="stForm"] button:hover {
            background-color: #3B82F6 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 狀態燈
        st.markdown("""
            <div style="text-align:center; color:#6B7280; font-size:14px; margin-bottom:5px; font-weight:600;">目前狀況</div>
            <div class="status-badge" style="background-color:#D1FAE5; color:#065F46; border:2px solid #6EE7B7;">
                🟢 可借用
            </div>
        """, unsafe_allow_html=True)

        # 卡片表單
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin:0 0 15px 0; font-weight:700;'>借用登記</h3>", unsafe_allow_html=True)
        
        # 身分選擇
        role_select = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<b>借用人</b>", unsafe_allow_html=True)
                user = st.selectbox("借用人", current_name_list, label_visibility="collapsed")
            with col2:
                st.markdown("<b>使用部位</b>", unsafe_allow_html=True)
                reason = st.selectbox("使用部位", BODY_PARTS, label_visibility="collapsed")
            
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            
            st.markdown("<b>移動至單位</b>", unsafe_allow_html=True)
            location_options = ["請選擇前往單位..."] + UNIT_LIST
            location = st.selectbox("前往單位", location_options, label_visibility="collapsed")
            
            st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)
            
            # 按鈕 (CSS 已設定為 藍底黑字)
            submit = st.form_submit_button("🚀 登記推走設備")
            
            if submit:
                if location == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位")
                else:
                    tw_now = get_taiwan_time()
                    new_record = {
                        "狀態": "借出",
                        "職稱": role_select,
                        "借用人": user,
                        "借用時間": tw_now.strftime("%Y-%m-%d %H:%M:%S"),
                        "使用部位": reason,
                        "所在位置": location,
                        "歸還人": None,
                        "歸還時間": None,
                        "持續時間(分)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                    save_data(df)
                    st.toast(f"登記成功！", icon="🎉")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 情境 B：歸還模式 (紅色系 + 儀表板)
    # ==========================================
    else:
        last_user = df.iloc[-1]["借用人"]
        last_loc = df.iloc[-1]["所在位置"]
        last_time = df.iloc[-1]["借用時間"]
        
        # 🔥🔥🔥 強制注入：紅色按鈕 CSS (修正版) 🔥🔥🔥
        # 這裡的代碼只會在「歸還」時執行，保證按鈕變紅
        st.markdown("""
        <style>
        /* 針對表單內的按鈕進行強制樣式覆蓋 */
        div[data-testid="stForm"] button {
            background-color: #F87171 !important; /* 亮紅色 */
            color: #000000 !important; /* 純黑字 */
            border: none !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            font-size: 20px !important;
            font-weight: 900 !important; /* 極粗 */
            text-align: center !important
            width: 100% !important; /* 滿版置中 */
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        div[data-testid="stForm"] button:hover {
            background-color: #EF4444 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 狀態燈
        st.markdown("""
            <div style="text-align:center; color:#6B7280; font-size:14px; margin-bottom:5px; font-weight:600;">目前狀況</div>
            <div class="status-badge" style="background-color:#FEE2E2; color:#991B1B; border:2px solid #FCA5A5;">
                🔴 使用中
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        
        # === 資訊儀表板 (填補空白專用) ===
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-box">
                <div class="dashboard-label">👤 使用者</div>
                <div class="dashboard-value">{last_user}</div>
            </div>
            <div class="dashboard-box">
                <div class="dashboard-label">📍 目前位置</div>
                <div class="dashboard-value-large">{last_loc}</div>
            </div>
        </div>
        <div style="text-align:center; font-size:13px; color:#6B7280; margin-bottom:20px;">
            借出時間：{last_time}
        </div>
        <hr style="border:0; border-top:1px solid #E5E7EB; margin-bottom:20px;">
        """, unsafe_allow_html=True)
        
        # 歸還表單
        with st.form("return_form"):
            st.markdown("<b>歸還人</b>", unsafe_allow_html=True)
            default_idx = ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx, label_visibility="collapsed")
            
            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            check_integrity = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            
            st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

            # 按鈕 (CSS 已設定為 紅底黑字)
            submit_return = st.form_submit_button("📦 確認歸還設備")
            
            if submit_return:
                if not check_integrity:
                    st.error("⚠️ 請確認設備完整性")
                else:
                    tw_return_now = get_taiwan_time()
                    borrow_time_obj = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                    duration = round((tw_return_now.replace(tzinfo=None) - borrow_time_obj).total_seconds() / 60, 1)
                    
                    df.at[last_record_index, "狀態"] = "歸還"
                    df.at[last_record_index, "歸還人"] = returner
                    df.at[last_record_index, "歸還時間"] = tw_return_now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_record_index, "持續時間(分)"] = duration
                    
                    save_data(df)
                    st.success("歸還成功！")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 統計區
    # ==========================================
    if not df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📊 查看紀錄與統計"):
            tab1, tab2 = st.tabs(["📋 詳細紀錄", "📈 圖表分析"])
            
            with tab1:
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                # 這裡的按鈕我們不強制覆蓋樣式，讓它保持預設，以免被紅/藍色影響
                st.download_button("📥 下載備份 (CSV)", csv, "ultrasound_backup.csv", "text/csv")

            with tab2:
                if "職稱" in df.columns:
                    fig = px.pie(df, names='職稱', title='職稱比例', hole=0.5)
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()   ext align center centers text horizontally within its container, typically done in web design with the CSS text-align: center; property or in applications via toolbar buttons (often with Ctrl+E or Cmd+E) to position text equidistant from left and right edges, creating a balanced look for headings, titles, or short blocks of text. 
