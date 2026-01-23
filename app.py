import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. 頁面基礎設定 (必須在第一行) ---
st.set_page_config(
    page_title="內科超音波登記",
    page_icon="🩺",
    layout="centered"
)

# 檔案名稱
FILE_NAME = "ultrasound_records.csv"

# --- 2. 注入 Apple 風格 CSS (魔法都在這裡) ---
def local_css():
    st.markdown("""
        <style>
        /* 全局背景色：Apple 經典淺灰 */
        .stApp {
            background-color: #F5F5F7;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* 隱藏預設選單和 footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* 卡片式容器設計 */
        .css-card {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
            margin-bottom: 20px;
        }

        /* 標題樣式 */
        h1 {
            color: #1D1D1F;
            font-weight: 700;
            letter-spacing: -0.5px;
            padding-bottom: 10px;
        }
        h3 {
            color: #86868B;
            font-weight: 500;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 輸入框美化 - 圓角與柔和邊框 */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
            background-color: #F5F5F7;
            border: 1px solid #E5E5EA;
            border-radius: 12px;
            color: #1D1D1F;
            padding: 10px; 
        }
        
        /* 按鈕美化 - iOS 藍色風格 */
        .stButton button {
            background-color: #0071E3;
            color: white;
            font-weight: 600;
            border-radius: 980px; /* 膠囊狀 */
            border: none;
            padding: 12px 24px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
        }
        .stButton button:hover {
            background-color: #0077ED;
            transform: scale(1.02);
            box-shadow: 0 6px 16px rgba(0, 113, 227, 0.4);
        }
        
        /* 表格美化 */
        [data-testid="stDataFrame"] {
            border: 1px solid #E5E5EA;
            border-radius: 16px;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True)

local_css()

# --- 3. 讀取資料邏輯 ---
if os.path.exists(FILE_NAME):
    try:
        df = pd.read_csv(FILE_NAME)
    except:
        df = pd.DataFrame(columns=["登記時間", "病歷號", "姓名", "檢查項目", "備註"])
else:
    df = pd.DataFrame(columns=["登記時間", "病歷號", "姓名", "檢查項目", "備註"])

# --- 4. 介面佈局 ---

# 標題區
st.markdown("<h1 style='text-align: center;'>Internal Medicine Ultrasound</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #86868B; margin-top: -15px; margin-bottom: 30px;'>內科超音波登記站</p>", unsafe_allow_html=True)

# 顯示今日統計數據 (類似 iOS Widget)
today_str = datetime.now().strftime("%Y-%m-%d")
# 篩選今天的資料
try:
    today_count = len(df[df['登記時間'].str.contains(today_str)])
except:
    today_count = 0

# 使用 columns 稍微置中數據
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown(f"""
    <div style="background: white; border-radius: 20px; padding: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px;">
        <span style="color: #86868B; font-size: 14px;">今日已檢查人數</span><br>
        <span style="color: #0071E3; font-size: 36px; font-weight: 700;">{today_count}</span>
    </div>
    """, unsafe_allow_html=True)

# --- 輸入表單區 (模擬卡片視覺) ---
st.markdown("<h3>New Entry</h3>", unsafe_allow_html=True)

with st.container():
    # 這裡雖然看不到 css-card class，但因為 Streamlit 結構限制，我們靠上面的 CSS 全域渲染
    # 我們用 st.form 來包裝
    with st.form("apple_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            mrn = st.text_input("病歷號 (MRN)", placeholder="例如: 12345678")
        with col2:
            name = st.text_input("姓名 (Name)", placeholder="請輸入姓名")
            
        exam_type = st.selectbox("檢查項目 (Type)", ["腹部超音波 (Abdomen)", "甲狀腺 (Thyroid)", "軟組織 (Soft Tissue)", "都卜勒 (Doppler)", "其他 (Others)"])
        note = st.text_area("備註 (Note)", height=80, placeholder="選填...")
        
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("＋ 加入登記")

    if submitted:
        if not mrn or not name:
            st.error("⚠️ 請填寫完整的「病歷號」與「姓名」")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame([{
                "登記時間": timestamp,
                "病歷號": mrn,
                "姓名": name,
                "檢查項目": exam_type,
                "備註": note
            }])
            
            # 合併並存檔
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            
            # 成功的微互動 (Toast)
            st.toast(f"✅ 已完成登記：{name}", icon="🎉")
            
            # 強制重新整理以更新數據顯示 (Rerun)
            st.rerun()

# --- 列表顯示區 ---
st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
st.markdown("<h3>Recent Records</h3>", unsafe_allow_html=True)

if not df.empty:
    # 讓表格看起來比較漂亮，隱藏索引，把最新的放上面
    display_df = df.sort_index(ascending=False)
    
    st.dataframe(
        display_df,
        column_config={
            "登記時間": st.column_config.TextColumn("Time", width="medium"),
            "病歷號": "MRN",
            "姓名": "Name",
            "檢查項目": st.column_config.TextColumn("Type", width="medium"),
            "備註": "Note"
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 下載按鈕
    st.download_button(
        label="📥 下載 Excel 報表",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f'ultrasound_list_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
else:
    st.markdown("""
    <div style='text-align: center; color: #86868B; padding: 40px; background: white; border-radius: 16px;'>
        目前還沒有資料，請輸入第一筆登記。
    </div>
    """, unsafe_allow_html=True)
