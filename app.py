import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 資料與設定 (完全保留原本內容)
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
# 3. 主程式介面 (視覺復刻版)
# ==========================================

def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")
    
    # ==========================================
    # 🔥 CSS 魔法區：100% 還原截圖風格 🔥
    # ==========================================
    st.markdown("""
        <style>
        /* 1. 全局背景：iOS 淺灰 */
        [data-testid="stAppViewContainer"] {
            background-color: #F2F2F7 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }
        
        /* 2. 標題與文字顏色 */
        h1 {
            color: #1C1C1E !important;
            font-weight: 700 !important;
            text-align: center !important;
            font-size: 28px !important;
            margin-bottom: 5px !important;
        }
        p, label, span, div {
            color: #1C1C1E;
        }
        
        /* 3. 卡片式容器 (White Card) */
        .apple-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }

        /* 4. 狀態指示燈 (綠色/紅色區塊) */
        .status-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .status-header {
            font-size: 14px;
            color: #8E8E93;
            margin-bottom: 8px;
        }
        .status-badge-green {
            background-color: #E8F5E9; /* 淺綠底 */
            color: #2E7D32; /* 深綠字 */
            padding: 15px 0;
            border-radius: 12px;
            font-size: 22px;
            font-weight: 700;
            border: 1px solid #C8E6C9;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        .status-badge-red {
            background-color: #FFEBEE;
            color: #C62828;
            padding: 15px 0;
            border-radius: 12px;
            font-size: 22px;
            font-weight: 700;
            border: 1px solid #FFCDD2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }

        /* 5. 輸入框優化 */
        /* 下拉選單與輸入框背景改為淺灰，類似 iOS 欄位 */
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: #F2F2F7 !important;
            border: none !important;
            border-radius: 10px !important;
            color: #1C1C1E !important;
        }
        /* Radio Button 優化 */
        [role="radiogroup"] {
            background-color: transparent;
            padding: 0;
        }
        
        /* 6. 按鈕優化：復刻截圖中的「藍色滿版按鈕」 */
        .stButton {
            margin-top: 10px;
        }
        .stButton button {
            background-color: #3b82f6 !important; /* iOS Blue 亮藍色 */
            color: white !important;
            border: none !important;
            border-radius: 12px !important; /* 稍微方一點的圓角 */
            padding: 12px 0 !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            width: 100% !important; /* 滿版寬度 */
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2) !important;
            transition: opacity 0.2s;
        }
        .stButton button:active {
            opacity: 0.7;
        }

        /* 隱藏預設元素 */
        #MainMenu, footer, header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    # 讀取資料
    df = load_data()
    
    current_status = "可借用"
    last_record_index = None
    
    if not df.empty:
        last_row = df.iloc[-1]
        if last_row["狀態"] == "借出":
            current_status = "使用中"
            last_record_index = df.index[-1]

    # --- 頁面標題 ---
    st.markdown("<h1>內科超音波 登記站</h1>", unsafe_allow_html=True)

    # ==========================================
    # 介面 A：借出模式 (復刻截圖)
    # ==========================================
    if current_status == "可借用":
        # 狀態顯示區
        st.markdown("""
            <div class="status-container">
                <div class="status-header">目前狀況</div>
                <div class="status-badge-green">🟢 可借用</div>
            </div>
        """, unsafe_allow_html=True)

        # === 白色卡片開始 ===
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        
        st.markdown("<h3 style='margin-top:0; font-size:18px; font-weight:600;'>借用人身分</h3>", unsafe_allow_html=True)
        
        # 身分選擇 (Radio Buttons)
        role_select = st.radio("身分選擇", ["醫師", "專科護理師"], horizontal=True, label_visibility="collapsed")
        
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        # 表單內容
        with st.form("borrow_form"):
            # 為了排版好看，使用 st.write 加一些間距或標籤
            st.markdown(f"<p style='margin-bottom:4px; font-weight:500; font-size:14px; color:#666;'>{role_select}</p>", unsafe_allow_html=True)
            user = st.selectbox(f"選擇{role_select}姓名", current_name_list, label_visibility="collapsed")
            
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True) # 間距

            st.markdown("<p style='margin-bottom:4px; font-weight:500; font-size:14px; color:#666;'>使用部位</p>", unsafe_allow_html=True)
            reason = st.selectbox("使用部位", BODY_PARTS, label_visibility="collapsed")
            
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True) # 間距

            st.markdown("<p style='margin-bottom:4px; font-weight:500; font-size:14px; color:#666;'>移動至單位</p>", unsafe_allow_html=True)
            location_options = ["請選擇前往單位..."] + UNIT_LIST
            location = st.selectbox("前往單位", location_options, label_visibility="collapsed")
            
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True) # 按鈕前間距

            # 藍色滿版按鈕
            submit = st.form_submit_button("登記並取走設備")
            
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
        # === 白色卡片結束 ===

    # ==========================================
    # 介面 B：歸還模式 (保持一致風格)
    # ==========================================
    else:
        last_user = df.iloc[-1]["借用人"]
        last_loc = df.iloc[-1]["所在位置"]
        last_time = df.iloc[-1]["借用時間"]
        
        # 狀態顯示區
        st.markdown("""
            <div class="status-container">
                <div class="status-header">目前狀況</div>
                <div class="status-badge-red">🔴 使用中</div>
            </div>
        """, unsafe_allow_html=True)

        # === 白色卡片開始 ===
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        
        # 資訊顯示
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p style='font-size:12px; color:#8E8E93; margin-bottom:0;'>使用者</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:18px; font-weight:600;'>{last_user}</p>", unsafe_allow_html=True)
        with col2:
            st.markdown("<p style='font-size:12px; color:#8E8E93; margin-bottom:0;'>目前位置</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:18px; font-weight:600;'>{last_loc}</p>", unsafe_allow_html=True)
            
        st.markdown(f"<p style='font-size:12px; color:#8E8E93; text-align:center;'>借出時間：{last_time}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #E5E5EA;'>", unsafe_allow_html=True)

        # 歸還表單
        with st.form("return_form"):
            st.markdown("<p style='margin-bottom:4px; font-weight:500; font-size:14px; color:#666;'>歸還人</p>", unsafe_allow_html=True)
            default_idx = ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx, label_visibility="collapsed")
            
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            
            check_integrity = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # 藍色滿版按鈕
            submit_return = st.form_submit_button("確認歸還設備")
            
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
        # === 白色卡片結束 ===

    # ==========================================
    # 統計區 (保留原有功能)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-size:16px; color:#8E8E93;'>紀錄與統計</h3>", unsafe_allow_html=True)
    
    if not df.empty:
        tab1, tab2 = st.tabs(["📋 詳細紀錄", "📊 圖表分析"])
        
        with tab1:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            # 下載按鈕
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下載備份 (CSV)", csv, "ultrasound_backup.csv", "text/csv")

        with tab2:
            if "職稱" in df.columns:
                fig = px.pie(df, names='職稱', title='使用者職稱比例', hole=0.5)
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
