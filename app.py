import streamlit as st
import pandas as pd
import plotly.express as px  # 新增：引入畫圓餅圖的工具
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 設定檔
# ==========================================

FILE_NAME = 'ultrasound_log.csv'

# 醫師名單
DOCTORS = [
    "朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", 
    "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", 
    "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", 
    "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", 
    "李坤峰", "何承恩", "沈治華", "PGY醫師"
]

# 專科護理師名單 (NP)
NPS = [
    "侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", 
    "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", 
    "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", 
    "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"
]

# 全體名單
ALL_STAFF = DOCTORS + NPS

# 使用部位
BODY_PARTS = [
    "胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", 
    "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"
]

# 單位名稱
UNIT_LIST = [
    "3A", "3B", "5A", "5B", "6A", "6B", 
    "7A", "7B", "RCC", "6D", "6F", "檢查室"
]

# ==========================================
# 2. 核心功能函數
# ==========================================

def get_taiwan_time():
    """取得台灣目前的 datetime 物件"""
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
    if "職稱" not in df.columns:
        df["職稱"] = "未分類" 
    return df

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ==========================================
# 3. 主程式介面
# ==========================================

def main():
    st.set_page_config(page_title="內科超音波動態", page_icon="🏥", layout="centered")
    
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stMetric {background-color: #f0f2f6; padding: 10px; border-radius: 5px;}
        div[role='radiogroup'] > label {
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 5px;
            margin-right: 10px;
            cursor: pointer;
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
    # 介面 A：借出登記
    # ==========================================
    if current_status == "可借用":
        st.success("### 🟢 目前狀態：在庫可借")
        
        st.write("#### 1. 借用人身分")
        role_select = st.radio("請選擇職別：", ["醫師", "專科護理師"], horizontal=True)
        
        if role_select == "醫師":
            current_name_list = DOCTORS
        else:
            current_name_list = NPS

        with st.form("borrow_form"):
            col1, col2 = st.columns(2)
            with col1:
                user = st.selectbox(f"選擇{role_select}姓名", current_name_list)
            with col2:
                reason = st.selectbox("使用部位", BODY_PARTS)
            
            location_options = ["請選擇前往單位..."] + UNIT_LIST
            location = st.selectbox("2. 機器移動前往單位", location_options)
            
            submit = st.form_submit_button("✅ 登記並取走機器", use_container_width=True)
            
            if submit:
                if location == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位，以免機器遺失！")
                else:
                    tw_now = get_taiwan_time()
                    tw_time_str = tw_now.strftime("%Y-%m-%d %H:%M:%S")

                    new_record = {
                        "狀態": "借出",
                        "職稱": role_select,
                        "借用人": user,
                        "借用時間": tw_time_str,
                        "使用部位": reason,
                        "所在位置": location,
                        "歸還人": None,
                        "歸還時間": None,
                        "持續時間(分)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                    save_data(df)
                    st.toast(f"登記成功！{user} {role_select} 請取用", icon="🚀")
                    st.rerun()

    # ==========================================
    # 介面 B：歸還登記
    # ==========================================
    else:
        last_user = df.iloc[-1]["借用人"]
        last_role = df.iloc[-1].get("職稱", "未分類")
        last_time = df.iloc[-1]["借用時間"]
        last_loc = df.iloc[-1]["所在位置"]
        
        st.error(f"### 🔴 機器使用中")
        
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
            
            submit_return = st.form_submit_button("↩️ 確認歸還 / 歸位", use_container_width=True)
            
            if submit_return:
                tw_return_now = get_taiwan_time()
                tw_return_str = tw_return_now.strftime("%Y-%m-%d %H:%M:%S")
                
                borrow_time_obj = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                duration = round((tw_return_now.replace(tzinfo=None) - borrow_time_obj).total_seconds() / 60, 1)
                
                df.at[last_record_index, "狀態"] = "歸還"
                df.at[last_record_index, "歸還人"] = returner
                df.at[last_record_index, "歸還時間"] = tw_return_str
                df.at[last_record_index, "持續時間(分)"] = duration
                
                save_data(df)
                st.success("歸還成功！")
                st.rerun()

    # ==========================================
    # 統計區 (更新：圓餅圖 + 新順序)
    # ==========================================
    st.markdown("---")
    st.subheader("📊 統計數據")
    
    if not df.empty:
        # 依照你的要求調整順序：詳細表 -> 職稱 -> 人員 -> 部位
        tab1, tab2, tab3, tab4 = st.tabs(["📋 詳細表", "🩺 職稱統計", "🏆 人員統計", "🔍 部位統計"])
        
        # 1. 詳細表 (Detail Table)
        with tab1:
            st.write("#### 歷史紀錄 (最新在最上)")
            st.dataframe(
                df[["借用時間", "職稱", "借用人", "所在位置", "使用部位", "歸還時間"]].sort_index(ascending=False), 
                use_container_width=True
            )

        # 2. 職稱統計 (Pie Chart)
        with tab2:
            if "職稱" in df.columns:
                fig = px.pie(df, names='職稱', title='職稱使用比例', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        # 3. 人員統計 (Pie Chart)
        with tab3:
            if "借用人" in df.columns:
                # 統計每個人借了幾次
                user_counts = df["借用人"].value_counts().reset_index()
                user_counts.columns = ["借用人", "次數"]
                fig = px.pie(user_counts, names='借用人', values='次數', title='同仁使用佔比')
                st.plotly_chart(fig, use_container_width=True)
                
        # 4. 部位統計 (Pie Chart)
        with tab4:
            if "使用部位" in df.columns:
                part_counts = df["使用部位"].value_counts().reset_index()
                part_counts.columns = ["使用部位", "次數"]
                fig = px.pie(part_counts, names='使用部位', values='次數', title='檢查部位佔比')
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
