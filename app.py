import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
from streamlit_gsheets import GSheetsConnection # 引入連線工具

# ==========================================
# 1. 設定檔 (名單與選項)
# ==========================================

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
# 2. 核心功能函數 (Google Sheets 版本)
# ==========================================

def get_taiwan_time():
    """取得台灣時間"""
    utc_dt = datetime.now(timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8)))

def load_data():
    """從 Google Sheets 讀取資料"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0) # ttl=0 代表不快取，每次抓最新
    
    # 確保欄位存在 (防呆)
    expected_cols = ["狀態", "職稱", "借用人", "借用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"]
    
    if df.empty or len(df.columns) == 0:
        return pd.DataFrame(columns=expected_cols)
    
    # 補齊缺少的欄位
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            
    # 確保數值欄位格式正確
    df["持續時間(分)"] = pd.to_numeric(df["持續時間(分)"], errors='coerce').fillna(0)
    
    return df

def save_data(df):
    """將資料寫回 Google Sheets"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(data=df)

# ==========================================
# 3. 主程式介面 (保留你的 Apple Style CSS)
# ==========================================

def main():
    st.set_page_config(
        page_title="內科超音波",
        page_icon="🏥",
        layout="centered"
    )

    # ===== Apple 風格 CSS (你原本的設計) =====
    st.markdown("""
    <style>
    /* 全站背景 */
    [data-testid="stAppViewContainer"] {
        background-color: #F5F5F7;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    
    /* 標題優化 */
    h1 {
        font-weight: 700;
        color: #1d1d1f;
    }
    
    /* 卡片通用樣式 */
    .status-card, .form-card {
        background-color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* 稍微調整陰影更柔和 */
    }
    
    /* 狀態卡片 - 可借用 */
    .status-available {
        background-color: #E9F8EF;
        color: #1C7C54;
        border: 1px solid #c3e6cb;
    }
    
    /* 狀態卡片 - 使用中 */
    .status-using {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }
    
    .status-title {
        font-size: 0.9rem;
        color: #6e6e73; /* Apple 灰色 */
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-text {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* 按鈕優化 (Apple Blue) */
    .stButton button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #0062cc !important;
        transform: scale(1.01);
    }
    
    /* 選項按鈕優化 */
    div[role='radiogroup'] label {
        background-color: #F2F2F7 !important;
        padding: 12px 20px !important;
        border-radius: 12px !important;
        margin-right: 8px !important;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    div[role='radiogroup'] label:hover {
        background-color: #e5e5ea !important;
    }
    
    /* 隱藏預設選單 */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* 表格背景白底 */
    [data-testid="stTable"] {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # 讀取資料 (從 Google Sheets)
    try:
        df = load_data()
    except Exception as e:
        st.error(f"連線錯誤，請檢查 Secrets 設定。錯誤: {e}")
        return

    current_status = "可借用"
    last_index = None

    if not df.empty and str(df.iloc[-1]["狀態"]) == "借出":
        current_status = "使用中"
        last_index = df.index[-1]

    st.title("🏥 超音波使用登記")

    # ==========================================
    # 介面 A: 可借用 (綠色)
    # ==========================================
    if current_status == "可借用":
        st.markdown("""
        <div class="status-card status-available">
            <div class="status-title">Current Status</div>
            <div class="status-text">🟢 可借用</div>
            <div style="font-size: 0.9rem; margin-top: 5px;">設備應在存放位置</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("📝 借用登記")

        with st.form("borrow_form"):
            role = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
            name_list = DOCTORS if role == "醫師" else NPS
            
            col1, col2 = st.columns(2)
            with col1: user = st.selectbox("1. 借用人", name_list)
            with col2: part = st.selectbox("2. 使用部位", BODY_PARTS)
            
            unit = st.selectbox("3. 移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("登記並取走設備")

            if submit:
                if unit == "請選擇前往單位...":
                    st.error("⚠️ 請務必選擇前往單位！")
                else:
                    now = get_taiwan_time()
                    new_row = {
                        "狀態": "借出",
                        "職稱": role,
                        "借用人": user,
                        "借用時間": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "使用部位": part,
                        "所在位置": unit,
                        "歸還人": "",
                        "歸還時間": "",
                        "持續時間(分)": 0
                    }
                    # 轉成 DataFrame 並合併
                    new_df = pd.DataFrame([new_row])
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df) # 寫入 Google Sheets
                    st.toast("登記成功！", icon="✅")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 介面 B: 使用中 (紅色)
    # ==========================================
    else:
        last = df.iloc[-1]

        st.markdown("""
        <div class="status-card status-using">
            <div class="status-title">Current Status</div>
            <div class="status-text">🔴 使用中</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        # 顯示當前借用資訊
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👤 使用者", f"{last['借用人']}")
        with col2:
            st.metric("📍 目前位置", f"{last['所在位置']}")
            
        st.caption(f"🕒 借出時間：{last['借用時間']}")
        st.markdown("---")

        with st.form("return_form"):
            st.subheader("↩️ 歸還確認")
            default_idx = ALL_STAFF.index(last["借用人"]) if last["借用人"] in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx)
            
            # 黃色警告區塊
            st.warning("📦 請檢查：探頭清潔、線材收好、功能正常")
            check = st.checkbox("✅ 我已確認設備完整")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("確認歸還")

            if submit:
                if not check:
                    st.error("⚠️ 請勾選確認設備完整！")
                else:
                    now = get_taiwan_time()
                    start_str = str(last["借用時間"])
                    try:
                        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        # 防呆：如果格式跑掉
                        start = now.replace(tzinfo=None)

                    duration = round((now.replace(tzinfo=None) - start).total_seconds() / 60, 1)
                    
                    df.at[last_index, "狀態"] = "歸還"
                    df.at[last_index, "歸還人"] = returner
                    df.at[last_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_index, "持續時間(分)"] = duration
                    
                    save_data(df) # 寫入 Google Sheets
                    st.success("歸還完成！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 統計區
    # ==========================================
    st.markdown("---")
    st.subheader("📊 使用統計")

    if not df.empty:
        # 使用者可能會希望先看到最新的，所以我們把資料反轉
        display_df = df.sort_index(ascending=False).head(20) # 只顯示最新的20筆
        
        tab1, tab2, tab3 = st.tabs(["📋 最新紀錄", "📈 職稱分析", "🏆 使用者分析"])

        with tab1:
            # 簡單表格
            st.table(display_df[["借用時間", "借用人", "所在位置", "歸還時間"]])

        with tab2:
            if "職稱" in df.columns:
                fig = px.pie(df, names="職稱", title="使用者職稱比例", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if "借用人" in df.columns:
                user_counts = df["借用人"].value_counts().reset_index()
                user_counts.columns = ["借用人", "次數"]
                fig = px.bar(user_counts.head(10), x='借用人', y='次數', title="借用次數排行 (Top 10)")
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
