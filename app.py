import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, timezone

# --- 核心連線 ---
conn = st.connection("gsheets", type=GSheetsConnection)

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    # 因為你已經改名為 Sheet1，這裡就用 Sheet1
    return conn.read(worksheet="Sheet1", ttl=0)

def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥")
    
    # 讀取雲端資料
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ 連線失敗，請檢查 Secrets 中的網址與工作表名稱是否正確。錯誤資訊: {e}")
        return

    current_status = "可借用"
    if not df.empty:
        df['狀態'] = df['狀態'].astype(str).str.strip()
        if (df['狀態'] == "借出").any():
            current_status = "使用中"
            last_row = df[df['狀態'] == "借出"].iloc[-1]

    st.markdown('<h1 style="text-align:center; font-weight:900;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    if current_status == "可借用":
        st.success("### ✅ 設備目前在位")
        role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)
        with st.form("borrow_form"):
            user = st.selectbox("2. 使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("3. 前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("4. 使用部位", BODY_PARTS)
            
            if st.form_submit_button("✅ 登記推走設備", use_container_width=True):
                if loc == "請選擇單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    # 這就是你剛剛提供的那段邏輯
                    new_rec = pd.DataFrame([{
                        "狀態": "借出", "職稱": role, "使用人": user, 
                        "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), 
                        "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0
                    }])
                    df_updated = pd.concat([df, new_rec], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=df_updated)
                    st.toast(f"👌 {user} 登記成功！資料已同步至雲端。", icon="👌")
                    st.rerun()

    else:
        st.error(f"### ⚠️ 設備目前由 {last_row['使用人']} 使用中")
        # ... (顯示位置卡片與歸還表單) ...
        with st.form("return_form"):
            check = st.checkbox("探頭已清潔 / 線材已收納 / 功能正常")
            if st.form_submit_button("📦 確認歸還回位", use_container_width=True):
                if not check:
                    st.warning("⚠️ 請勾選確認項目")
                else:
                    df.loc[df[df['狀態'] == "借出"].index[-1], "狀態"] = "歸還"
                    df.loc[df.index[-1], "歸還時間"] = get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S")
                    conn.update(worksheet="Sheet1", data=df)
                    st.toast("👍 歸還成功！資料已更新至雲端。", icon="👍")
                    st.rerun()

    # 歷史紀錄
    with st.expander("📊 查看紀錄"):
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
