import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 設定檔
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
    "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"
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
    st.set_page_config(page_title="內科超音波動態", page_icon="🏥", layout="centered")
    
    # --- 介面優化 CSS ---
    # 1. 強制隱藏 Streamlit 的 Footer (Hosted with Streamlit) 和選單
    # 2. 加大手機版按鈕的高度，比較好按
    # 3. 調整 Radio Button 的樣式，讓它像卡片一樣
    st.markdown("""
        <style>
        /* 隱藏 Footer 和選單 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 優化手機按鈕大小 */
        .stButton button {
            height: 3em;
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        /* 優化選項卡片 */
        div[role='radiogroup'] > label {
            background-color: #f0f2f6;
            padding: 10px 20px;
            border-radius: 10px;
            margin-right: 10px;
            border: 1px solid #d1d5db;
        }
        div[role='radiogroup'] > label:hover {
            background-color: #e6e9ef;
        }
        
        /* 狀態看板樣式 */
        .status-card {
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
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

    st.title("🏥 內科超音波 登記站")

    # ==========================================
    # 介面 A：借出登記 (綠色)
    # ==========================================
    if current_status == "可借用":
        # 使用自訂的 HTML/CSS 來顯示更漂亮的狀態條
        st.markdown("""
            <div class="status-card" style="background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;">
                <h2 style="margin:0;">🟢 目前狀態：在庫可借</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("#### 1. 借用人身分")
        role_select = st.radio("請選擇職別：", ["醫師", "專科護理師"], horizontal=True)
        
        current_name_list = DOCTORS if role_select == "醫師" else NPS

        with st.form("borrow_form"):
            col1, col2 = st.columns(2)
            with col1:
                user = st.selectbox(f"選擇{role_select}姓名", current_name_list)
            with col2:
                reason = st.selectbox("使用部位", BODY_PARTS)
            
            location_options = ["請選擇前往單位..."] + UNIT_LIST
            location = st.selectbox("2. 機器移動前往單位", location_options)
            
            # 加大間距
            st.write("")
            submit = st.form_submit_button("✅ 登記並取走機器", use_container_width=True)
            
            if submit:
                if location == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位，以免機器遺失！")
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
                    st.toast(f"登記成功！", icon="🚀")
                    st.rerun()

    # ==========================================
    # 介面 B：歸還登記 (紅色)
    # ==========================================
    else:
        last_user = df.iloc[-1]["借用人"]
        last_role = df.iloc[-1].get("職稱", "未分類")
        last_time = df.iloc[-1]["借用時間"]
        last_loc = df.iloc[-1]["所在位置"]
        
        # 紅色狀態條
        st.markdown("""
            <div class="status-card" style="background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;">
                <h2 style="margin:0;">🔴 機器使用中</h2>
                <p style="margin:5px 0 0 0;">請掃描此處歸還</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👤 使用者", f"{last_user}")
            st.caption(f"({last_role})")
        with col2:
            st.metric("📍 目前位置", last_loc)
            
        st.info(f"⏰ 借出時間：{last_time}")
        
        with st.form("return_form"):
            st.write("#### 歸還確認")
            default_idx = ALL_STAFF.index(last_user) if last_user in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx)
            
            st.write("")
            submit_return = st.form_submit_button("↩️ 確認歸還 / 歸位", use_container_width=True)
            
            if submit_return:
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

    # ==========================================
    # 統計區
    # ==========================================
    st.markdown("---")
    st.subheader("📊 統計數據")
    
    if not df.empty:
        tab1, tab2, tab3, tab4 = st.tabs(["📋 詳細表", "🩺 職稱", "🏆 人員", "🔍 部位"])
        
        with tab1:
            st.dataframe(
                df[["借用時間", "職稱", "借用人", "所在位置", "使用部位", "歸還時間"]].sort_index(ascending=False), 
                use_container_width=True
            )
        with tab2:
            if "職稱" in df.columns:
                fig = px.pie(df, names='職稱', title='職稱比例', hole=0.4)
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
