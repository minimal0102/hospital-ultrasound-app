import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 資料與設定
# ==========================================
FILE_NAME = 'ultrasound_log.csv'
DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

# ==========================================
# 2. 核心功能
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data_fresh():
    """強制從硬碟讀取最新資料"""
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["狀態", "職稱", "使用人", "使用時間", "使用部位", "目前位置", "歸還人", "歸還時間", "持續時間(分)"])
        df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
        return df
    return pd.read_csv(FILE_NAME, encoding='utf-8-sig')

def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')

# ==========================================
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    # 讀取最新資料
    df = load_data_fresh()
    
    current_status = "可借用"
    if not df.empty:
        last_record = df.iloc[-1]
        if str(last_record["狀態"]).strip() == "借出":
            current_status = "使用中"

    # --- CSS 樣式區 ---
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        
        div[data-baseweb="select"] > div {
            border: 1.5px solid #000000 !important;
            border-radius: 8px !important;
        }
        
        .info-card {
            border-radius: 20px; padding: 30px 10px; text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1); color: #000 !important;
        }
        .status-blue { background-color: #60A5FA !important; }
        .status-red { background-color: #F87171 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center; font-weight:900;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    if current_status == "可借用":
        st.success("### ✅ 設備在位 (可登記使用)")
        role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)
        
        with st.form("borrow_form"):
            user = st.selectbox("2. 使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("3. 前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("4. 使用部位", BODY_PARTS)
            
            if st.form_submit_button("✅ 登記推走設備", use_container_width=True):
                if loc == "請選擇單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role, "使用人": user, "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df_latest = load_data_fresh()
                    df_latest = pd.concat([df_latest, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df_latest)
                    
                    # --- 👌 OK手勢回饋 ---
                    st.toast(f"👌 {user} 登記成功！前往 {loc}", icon="👌")
                    st.rerun()

    else:
        last_row = df.iloc[-1]
        st.error("### ⚠️ 設備目前使用中")
        
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0px;">
                <div class="info-card status-blue">
                    <span style="font-size: 18px; font-weight: 900; opacity: 0.8;">👤 使用人</span><br>
                    <span style="font-size: 36px; font-weight: 900;">{last_row['使用人']}</span>
                </div>
                <div class="info-card status-red">
                    <span style="font-size: 18px; font-weight: 900; opacity: 0.8;">📍 目前位置</span><br>
                    <span style="font-size: 36px; font-weight: 900;">{last_row['目前位置']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("return_form"):
            st.info(f"🕒 借出時間：{last_row['使用時間']}")
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常")
            if st.form_submit_button("📦 歸還設備", use_container_width=True):
                if not check:
                    st.warning("⚠️ 請先勾選確認項目")
                else:
                    now = get_taiwan_time()
                    start_t = datetime.strptime(str(last_row['使用時間']), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                    dur = round((now - start_t).total_seconds() / 60, 1)
                    
                    df_latest = load_data_fresh()
                    idx = df_latest.index[-1]
                    df_latest.at[idx, "狀態"] = "歸還"
                    df_latest.at[idx, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df_latest.at[idx, "持續時間(分)"] = dur
                    save_data(df_latest)
                    
                    # --- 👍 讚手勢回饋 ---
                    st.toast("👍 歸還成功！感謝您的收納與維護。", icon="👍")
                    st.rerun()

    # --- 紀錄區 (修正縮進問題) ---
    if not df.empty:
        st.write("---")
        with st.expander("📊 查看紀錄"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            # 定義下載用的 CSV 資料
            csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 下載目前 CSV 紀錄", csv_data, "ultrasound_log.csv", "text/csv")

    # 頁尾資訊
    st.caption("備註：本系統僅供內部設備追蹤使用。")

if __name__ == "__main__":
    main()
