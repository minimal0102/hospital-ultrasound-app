import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 設定檔 (完全保留你的內容)
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
# 2. 核心功能函數 (不變)
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
    st.set_page_config(page_title="內科超音波動態", page_icon="🏥", layout="centered")
    
    # ==========================================
    # 🔥 CSS 重點優化區：Apple 原生風格 🔥
    # ==========================================
    st.markdown("""
        <style>
        /* 1️⃣ 基礎設定：字體與背景 */
        @import url(-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
        
        [data-testid="stAppViewContainer"] {
            background-color: #F5F5F7 !important; /* Apple 淺灰底 */
            font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
        }
        .stMarkdown, h1, h2, h3, h4, h5, h6, p, div, span, li, label {
            color: #1D1D1F !important; /* 深灰黑，比純黑更有質感 */
        }

        /* 2️⃣ 卡片式設計 (White Card) */
        /* 將表單區塊變成白色卡片 */
        div.block-container > div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            /* 這裡稍微 tricky，針對 Streamlit 結構做卡片化，若跑版可移除這段 */
        }
        
        /* 自定義卡片容器 class */
        .apple-card {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 24px; /* 更大的圓角 */
            box-shadow: 0 4px 20px rgba(0,0,0,0.04); /* 極輕柔陰影 */
            margin-bottom: 25px;
        }

        /* 3️⃣ 輸入框優化 (Input Fields) */
        /* 讓輸入框像 iOS 設定裡的灰色區塊 */
        .stTextInput > div > div, .stSelectbox > div > div {
            background-color: #F5F5F7 !important; /* 淺灰填滿 */
            border: none !important; /* 去除邊框 */
            border-radius: 12px !important;
            color: #1D1D1F !important;
            transition: all 0.2s ease;
        }
        /* Focus 狀態 */
        .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within {
            background-color: #FFFFFF !important;
            box-shadow: 0 0 0 2px #007AFF !important; /* iOS 藍光暈 */
        }
        
        /* 選單文字顏色 */
        div[data-baseweb="select"] span {
            color: #1D1D1F !important;
        }

        /* 4️⃣ 狀態看板 (Status Widget) */
        .status-header {
            font-size: 0.85rem;
            color: #86868B !important; /* 輔助說明灰 */
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            text-align: center;
        }
        
        .status-pill-green {
            background-color: #FFFFFF !important;
            color: #34C759 !important; /* iOS Green */
            padding: 15px;
            border-radius: 18px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(52, 199, 89, 0.15);
            margin-bottom: 25px;
            border: 1px solid rgba(52, 199, 89, 0.2);
        }

        .status-pill-red {
            background-color: #FFFFFF !important;
            color: #FF3B30 !important; /* iOS Red */
            padding: 15px;
            border-radius: 18px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(255, 59, 48, 0.15);
            margin-bottom: 25px;
            border: 1px solid rgba(255, 59, 48, 0.2);
        }

        /* 5️⃣ 按鈕 (Buttons) */
        /* 綠色主按鈕：置中、大、膠囊 */
        .stButton {
            text-align: center;
            margin-top: 20px;
        }
        .stButton button {
            background-color: #34C759 !important; /* iOS Green */
            color: white !important;
            border: none !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            border-radius: 999px !important; /* 膠囊狀 */
            padding: 16px 48px !important;
            box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3) !important;
            transition: transform 0.1s ease !important;
        }
        .stButton button:active {
            transform: scale(0.96) !important; /* 點擊縮放回饋 */
        }
        .stButton button:hover {
            opacity: 0.9;
        }

        /* 隱藏雜項 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    df = load_data()
    
    current_status = "可借用"
    last_record_index = None
    
    if not df.empty:
        last_row = df.iloc[-1]
        if last_row["狀態"] == "借出":
            current_status = "使用中"
            last_record_index = df.index[-1]

    # 標題區 (極簡化)
    st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>內科超音波</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #86868B; margin-bottom: 30px;'>登記站</p>", unsafe_allow_html=True)

    # ==========================================
    # 介面 A：借出登記 (邏輯不變)
    # ==========================================
    if current_status == "可借用":
        # 狀態顯示 (iOS Widget 風格)
        st.markdown("""
            <div class="status-header">CURRENT STATUS</div>
            <div class="status-pill-green">🟢 可借用 Available</div>
            """, unsafe_allow_html=True)
        
        # 使用自定義 HTML 容器包裹表單，創造白色卡片效果
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        
        # 表單邏輯開始
        st.caption("借用資訊")
        # 職別選擇 (改用 Radio 比較直覺，或維持 Selectbox)
        role_select = st.radio("身分", ["醫師", "專科護理師"], horizontal=True)
        
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            col1, col2 = st.columns(2)
            with col1:
                user = st.selectbox(f"{role_select}姓名", current_name_list)
            with col2:
                reason = st.selectbox("使用部位", BODY_PARTS)
            
            location_options = ["請選擇前往單位..."] + UNIT_LIST
            location = st.selectbox("前往單位", location_options)
            
            st.write("") # 留白
            # 這是你要的「置中、字體略大、綠底」按鈕
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
        
        st.markdown('</div>', unsafe_allow_html=True) # 結束卡片

    # ==========================================
    # 介面 B：歸還登記 (邏輯不變)
    # ==========================================
    else:
        last_user = df.iloc[-1]["借用人"]
        last_role = df.iloc[-1].get("職稱", "未分類")
        last_time = df.iloc[-1]["借用時間"]
        last_loc = df.iloc[-1]["所在位置"]
        
        st.markdown("""
            <div class="status-header">CURRENT STATUS</div>
            <div class="status-pill-red">🔴 使用中 In Use</div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("使用者", f"{last_user}")
            st.caption(f"{last_role}")
        with col2:
            st.metric("位置", last_loc)
            st.caption(f"自 {last_time} 借出")
            
        st.divider() # 極簡分隔線
        
        with st.form("return_form"):
            st.caption("歸還確認")
            default_idx = ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx)
            
            st.write("")
            check_integrity = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            
            st.write("")
            submit_return = st.form_submit_button("確認歸還")
            
            if submit_return:
                if not check_integrity:
                    st.error("⚠️ 請確認物品完整性")
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
    # 統計區 (邏輯不變)
    # ==========================================
    st.write("")
    st.subheader("紀錄與統計")
    
    # 這裡的介面保持原樣，因為 Streamlit 的 Tab 很難完全改造成 iOS 風格
    # 但會自動套用上面的字體與背景設定
    if not df.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["📋 詳細表", "🩺 職稱", "🏆 人員", "🔍 部位"])
        
        with tab1:
            st.dataframe(
                df[["借用時間", "職稱", "借用人", "所在位置", "使用部位", "歸還時間"]].sort_index(ascending=False), 
                use_container_width=True
            )
        with tab2:
            if "職稱" in df.columns:
                fig = px.pie(df, names='職稱', title='職稱比例', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
        with tab3:
            if "借用人" in df.columns:
                user_counts = df["借用人"].value_counts().reset_index()
                user_counts.columns = ["借用人", "次數"]
                fig = px.pie(user_counts, names='借用人', values='次數', title='同仁使用佔比')
                st.plotly_chart(fig, use_container_width=True)
        with tab4:
            if "使用部位" in df.columns:
                part_counts = df["使用部位"].value_counts().reset_index()
                part_counts.columns = ["使用部位", "次數"]
                fig = px.pie(part_counts, names='使用部位', values='次數', title='檢查部位佔比')
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
