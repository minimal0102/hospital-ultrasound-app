import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 核心雲端連線與常數設定
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# 你的 Google 試算表正確網址
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1u8KVq46vpgYh9mIdtsVFGvRynOE_hiGbTNIgnr6mrv4/edit"

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    """從 Google Sheets 讀取資料 (已修正縮進與語法結構)"""
    try:
        # 嘗試讀取網址中名為 Sheet1 的分頁
        return conn.read(spreadsheet=GSHEET_URL, worksheet="Sheet1", ttl=0)
    except Exception as e:
        # 如果失敗，顯示提示但不崩潰
        st.error("❌ 讀取失敗。請確認 Secrets 中的私鑰格式正確（建議使用三引號）。")
        st.info(f"技術錯誤訊息: {e}")
        return pd.DataFrame()

# ==========================================
# 2. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    df = load_data()
    
    # 判斷設備狀態
    current_status = "可借用"
    last_row = None
    if not df.empty:
        df['狀態'] = df['狀態'].astype(str).str.strip()
        if (df['狀態'] == "借出").any():
            current_status = "使用中"
            last_row = df[df['狀態'] == "借出"].iloc[-1]

    # --- CSS 樣式 ---
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }
        div[data-baseweb="select"] > div { border: 2px solid #000000 !important; border-radius: 10px !important; }
        .info-card { border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 10px 0px; background-color: #FEE2E2; border: 2px solid #EF4444; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center; font-weight:900;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    if current_status == "使用中":
        st.error(f"### ⚠️ 設備目前由 {last_row['使用人']} 使用中")
        st.markdown(f'<div class="info-card">📍 目前位置：{last_row["目前位置"]}</div>', unsafe_allow_html=True)

        with st.form("return_form"):
            if st.form_submit_button("📦 確認歸還回位", use_container_width=True):
                target_idx = df[df['狀態'] == "借出"].index[-1]
                df.at[target_idx, "狀態"] = "歸還"
                df.at[target_idx, "歸還時間"] = get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S")
                conn.update(spreadsheet=GSHEET_URL, worksheet="Sheet1", data=df)
                st.toast("👍 歸還成功！", icon="👍")
                st.rerun()

    else:
        st.success("### ✅ 設備目前在位 (可登記)")
        role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)

        with st.form("borrow_form"):
            user = st.selectbox("使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("使用部位", BODY_PARTS)
            
            if st.form_submit_button("✅ 登記推走設備", use_container_width=True):
                if loc == "請選擇單位...":
                    st.error("⚠️ 請選擇目的地單位")
                else:
                    new_rec = pd.DataFrame([{"狀態": "借出", "職稱": role, "使用人": user, "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "目前位置": loc}])
                    df_updated = pd.concat([df, new_rec], ignore_index=True)
                    conn.update(spreadsheet=GSHEET_URL, worksheet="Sheet1", data=df_updated)
                    st.toast(f"👌 {user} 登記成功！", icon="👌")
                    st.rerun()

    st.write("---")
    with st.expander("📊 查看紀錄"):
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
