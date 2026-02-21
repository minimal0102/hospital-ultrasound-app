import streamlit as st
from streamlit_gsheets import GSheetsConnection # 換成雲端連線套件
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 資料與設定 (保留你原始的所有名單)
# ==========================================
# 這是你的 Google 試算表正確網址
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1u8KVq46vpgYh9mIdtsVFGvRynOE_hiGbTNIgnr6mrv4/edit"

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

# 初始化雲端連線
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. 核心功能 (將 CSV 改為 Google Sheets)
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data_fresh():
    """強制從雲端讀取並修復標題空格"""
    try:
        df = conn.read(spreadsheet=GSHEET_URL, worksheet="Sheet1", ttl=0)
        if not df.empty:
            # ✨ 新增這行：自動刪除試算表標題裡多出來的空格
            df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame(columns=["狀態", "職稱", "使用人", "使用時間", "使用部位", "目前位置", "歸還人", "歸還時間", "持續時間(分)"])

def save_data(df):
    """將 DataFrame 更新回 Google Sheets"""
    conn.update(spreadsheet=GSHEET_URL, worksheet="Sheet1", data=df)

# ==========================================
# 3. 主程式介面 (完全保留你原始的 UI 與 CSS)
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    # 每次重整畫面都重新讀取雲端資料，解決多人連線 Bug
    df = load_data_fresh()
    
    # 判斷狀態邏輯
    current_status = "可借用"
    last_idx = None
    if not df.empty:
        # 去除字串空格並判斷最後一筆
        last_record = df.iloc[-1]
        if str(last_record["狀態"]).strip() == "借出":
            current_status = "使用中"
            last_idx = df.index[-1]

    # --- 保留你原始的所有 CSS 樣式 ---
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        div[data-baseweb="select"] > div { border: 1.5px solid #000000 !important; border-radius: 8px !important; }
        div[data-baseweb="popover"] { margin-top: 4px !important; top: auto !important; }
        div[data-baseweb="select"] input { inputmode: none !important; caret-color: transparent !important; }
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0px; }
        .info-card { border-radius: 20px; padding: 30px 10px; text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.1); color: #000 !important; }
        .status-blue { background-color: #60A5FA !important; }
        .status-red { background-color: #F87171 !important; }
        .card-label { font-size: 18px; font-weight: 900; opacity: 0.8; }
        .card-value { font-size: 42px; font-weight: 900; display: block; margin-top: 5px; }
        .borrow-section div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important; height: 75px !important;
            background-color: #60A5FA !important; color: #000 !important;
            border-radius: 12px !important; font-size: 24px !important;
            font-weight: 900 !important; border: none !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        .return-section div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important; height: 75px !important;
            background-color: #F87171 !important; color: #000 !important;
            border-radius: 12px !important; font-size: 24px !important;
            font-weight: 900 !important; border: none !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        div[data-testid="stFormSubmitButton"] button p { color: #000 !important; font-size: 24px !important; font-weight: 900 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center; font-weight:900;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    if current_status == "可借用":
        st.success("### ✅ 設備在位 (可登記使用)")
        role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)

        st.markdown('<div class="borrow-section">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            user = st.selectbox("2. 使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("3. 前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("4. 使用部位", BODY_PARTS)
            if st.form_submit_button("✅ 登記推走設備"):
                if loc == "請選擇單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    new_rec = pd.DataFrame([{
    "狀態": "借出", 
    "職稱": role, 
    "使用人": user, 
    "使用時間": now_str, 
    "使用部位": part, 
    "目前位置": loc, 
    "歸還人": "", 
    "歸還時間": "", 
    "持續時間(分)": 0
}])
                    # 雲端更新邏輯
                    df_latest = load_data_fresh()
                    df_updated = pd.concat([df_latest, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df_updated)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        last_row = df.iloc[-1]
        st.error("### ⚠️ 設備目前使用中")

        st.markdown(f"""
            <div class="dashboard-grid">
                <div class="info-card status-blue">
                    <span class="card-label">👤 使用人</span>
                    <span class="card-value">{last_row['使用人']}</span>
                </div>
                <div class="info-card status-red">
                    <span class="card-label">📍 目前位置</span>
                    <span class="card-value">{last_row['目前位置']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="return-section">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.info(f"🕒 借出時間：{last_row['使用時間']}")
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            if st.form_submit_button("📦 歸還設備"):
                if not check:
                    st.warning("⚠️ 請先勾選確認項目")
                else:
                    now = get_taiwan_time()
                    # 計算持續時間
                    try:
                        start_t = datetime.strptime(str(last_row['使用時間']), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                        dur = round((now - start_t).total_seconds() / 60, 1)
                    except:
                        dur = 0
                    
                    # 雲端歸還邏輯
                    df_latest = load_data_fresh()
                    if not df_latest.empty:
                        last_idx_fresh = df_latest.index[-1]
                        df_latest.at[last_idx_fresh, "狀態"] = "歸還"
                        df_latest.at[last_idx_fresh, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        df_latest.at[last_idx_fresh, "持續時間(分)"] = dur
                        save_data(df_latest)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not df.empty:
        with st.expander("📊 查看紀錄"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
