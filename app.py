import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 設定檔 (Configuration)
# ==========================================

FILE_NAME = 'ultrasound_log.csv'

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
# 2. 功能函數 (Helper Functions)
# ==========================================

def get_taiwan_time():
    """取得台灣目前的 datetime"""
    utc_dt = datetime.now(timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8)))

def load_data():
    """讀取 CSV 資料，若無則建立新檔"""
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "狀態", "職稱", "借用人", "借用時間",
            "使用部位", "所在位置",
            "歸還人", "歸還時間", "持續時間(分)"
        ])
        df.to_csv(FILE_NAME, index=False)
        return df
    return pd.read_csv(FILE_NAME)

def save_data(df):
    """存檔"""
    df.to_csv(FILE_NAME, index=False)

# ==========================================
# 3. 主程式 (Main App)
# ==========================================

def main():
    st.set_page_config(
        page_title="內科超音波",
        page_icon="🏥",
        layout="centered"
    )

    # ===== Apple 風格 CSS 美化 =====
    st.markdown("""
    <style>
    /* 全局背景與字體 */
    [data-testid="stAppViewContainer"] {
        background-color: #F5F5F7;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    
    /* 標題樣式 */
    h1 {
        font-weight: 700;
        color: #1D1D1F;
    }
    
    /* 卡片式設計 */
    .status-card {
        background-color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .form-card {
        background-color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 狀態顏色 */
    .status-available {
        background-color: #E9F8EF;
        color: #1C7C54;
        border: 1px solid #D1E7DD;
    }
    .status-using {
        background-color: #FDEDED;
        color: #C0392B;
        border: 1px solid #F5C6CB;
    }
    
    /* 狀態文字優化 */
    .status-title {
        font-size: 0.9rem;
        color: #6e6e73;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-text {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* 按鈕優化 (iOS Blue) */
    .stButton button {
        background-color: #0071E3;
        color: white;
        border-radius: 980px;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        background-color: #0077ED;
        transform: scale(1.01);
    }
    
    /* 隱藏預設選單 */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # 讀取資料
    df = load_data()

    # 判斷機器目前的狀態
    current_status = "可借用"
    last_index = None

    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_index = df.index[-1]

    # 頁面標題
    st.title("🏥 內科超音波 登記站")

    # ==========================================
    # 狀態 1: 機器在庫 (可借用)
    # ==========================================
    if current_status == "可借用":
        st.markdown("""
        <div class="status-card status-available">
            <div class="status-title">Current Status</div>
            <div class="status-text">🟢 可借用 (Available)</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("### 📋 借用登記")

        with st.form("borrow_form"):
            role = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
            name_list = DOCTORS if role == "醫師" else NPS
            
            col1, col2 = st.columns(2)
            with col1:
                user = st.selectbox("借用人", name_list)
            with col2:
                part = st.selectbox("使用部位", BODY_PARTS)
                
            unit = st.selectbox("移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            
            st.write("") # 空行
            submit = st.form_submit_button("🚀 登記並取走設備")

            if submit:
                if unit == "請選擇前往單位...":
                    st.error("⚠️ 請務必選擇「前往單位」！")
                else:
                    now = get_taiwan_time()
                    new_row = {
                        "狀態": "借出",
                        "職稱": role,
                        "借用人": user,
                        "借用時間": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "使用部位": part,
                        "所在位置": unit,
                        "歸還人": None,
                        "歸還時間": None,
                        "持續時間(分)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.toast(f"✅ 登記成功！{user} 醫師/專師 請取用。", icon="🎉")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 狀態 2: 機器借出中 (需歸還)
    # ==========================================
    else:
        last = df.iloc[-1]

        st.markdown("""
        <div class="status-card status-using">
            <div class="status-title">Current Status</div>
            <div class="status-text">🔴 使用中 (In Use)</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("### ↩️ 歸還登記")

        col1, col2 = st.columns(2)
        col1.metric("👤 目前使用者", last["借用人"])
        col2.metric("📍 目前位置", last["所在位置"])
        st.caption(f"🕒 借出時間：{last['借用時間']}")

        with st.form("return_form"):
            # 預設歸還人為借用人
            default_idx = ALL_STAFF.index(last["借用人"]) if last["借用人"] in ALL_STAFF else 0
            returner = st.selectbox("歸還人 (通常同借用人)", ALL_STAFF, index=default_idx)
            
            st.write("")
            check = st.checkbox("✅ 我已確認探頭清潔完畢，且設備功能正常")
            submit = st.form_submit_button("📥 確認歸還設備")

            if submit:
                if not check:
                    st.error("❌ 請勾選確認設備完整！")
                else:
                    now = get_taiwan_time()
                    start = datetime.strptime(last["借用時間"], "%Y-%m-%d %H:%M:%S")
                    # 計算分鐘數
                    duration = round((now.replace(tzinfo=None) - start).total_seconds() / 60, 1)
                    
                    # 更新最後一筆資料
                    df.at[last_index, "狀態"] = "歸還"
                    df.at[last_index, "歸還人"] = returner
                    df.at[last_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_index, "持續時間(分)"] = duration
                    
                    save_data(df)
                    st.toast("✅ 歸還成功！辛苦了。", icon="👍")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 4. 統計與紀錄區
    # ==========================================
    st.markdown("---")
    st.subheader("📊 紀錄與統計")

    if not df.empty:
        tab1, tab2 = st.tabs(["📋 詳細紀錄 (可下載)", "📈 圖表分析"])

        with tab1:
            # 將最新的資料排在最上面
            display_df = df.sort_index(ascending=False)
            st.dataframe(display_df, use_container_width=True)
            
            # --- 下載按鈕 (重要功能) ---
            csv = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載 Excel 報表 (CSV)",
                data=csv,
                file_name=f'ultrasound_backup_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="點擊下載完整的登記紀錄備份"
            )

        with tab2:
            # 簡單的圓餅圖分析
            if len(df) > 0:
                fig = px.pie(df, names="職稱", title="使用者職稱比例", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
                # 也可以加一個使用部位分析
                fig2 = px.bar(df, x="使用部位", title="檢查部位統計", color="使用部位")
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("目前尚無登記紀錄。")

if __name__ == "__main__":
    main()
