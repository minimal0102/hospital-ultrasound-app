import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 核心雲端連線設定
# ==========================================
# 自動讀取 Secrets 中的 [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    # ttl=0 確保每次操作都抓取 Google Sheets 最新狀態
    return conn.read(worksheet="Sheet1", ttl=0)

# ==========================================
# 2. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    # 讀取資料
    df = load_data()
    
    current_status = "可借用"
    last_row = None
    if not df.empty:
        # 判斷最後一筆是否為借出狀態
        if str(df.iloc[-1]["狀態"]).strip() == "借出":
            current_status = "使用中"
            last_row = df.iloc[-1]

    # --- CSS 樣式 (維持你的黑框與美化設計) ---
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }
        div[data-baseweb="select"] > div { border: 2px solid #000000 !important; border-radius: 10px !important; }
        .info-card { border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 10px 0px; background-color: #FEE2E2; border: 2px solid #EF4444; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center; font-weight:900;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    # --- 邏輯 A: 設備在位 ---
    if current_status == "借出":
        # 顯示借出狀態卡片
        st.error(f"### ⚠️ 設備目前由 {last_row['使用人']} 使用中")
        st.markdown(f"""
            <div class="info-card">
                <span style="font-size: 20px; font-weight: 900; color: #7F1D1D;">📍 目前位置：{last_row['目前位置']}</span><br>
                <span style="font-size: 16px; color: #7F1D1D; opacity: 0.8;">🕒 借出時間：{last_row['使用時間']}</span>
            </div>
        """, unsafe_allow_html=True)

        with st.form("return_form"):
            st.write("🔧 歸還確認：")
            check = st.checkbox("探頭已清潔 / 線材已收納 / 功能正常")
            if st.form_submit_button("📦 確認歸還回位", use_container_width=True):
                if not check:
                    st.warning("⚠️ 請先勾選確認項目")
                else:
                    now = get_taiwan_time()
                    # 更新最後一筆紀錄
                    df.loc[df.index[-1], "狀態"] = "歸還"
                    df.loc[df.index[-1], "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    # 計算持續時間
                    start_t = datetime.strptime(str(last_row['使用時間']), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                    df.loc[df.index[-1], "持續時間(分)"] = round((now - start_t).total_seconds() / 60, 1)
                    
                    conn.update(worksheet="Sheet1", data=df)
                    st.toast("👍 歸還成功！資料已永久保存至雲端。", icon="👍")
                    st.rerun()

    # --- 邏輯 B: 可借用 ---
    else:
        st.success("### ✅ 設備目前在位 (可登記)")
        role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)

        with st.form("borrow_form"):
            user = st.selectbox("2. 使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("3. 前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("4. 使用部位", BODY_PARTS)
            
            if st.form_submit_button("✅ 登記推走設備", use_container_width=True):
                if loc == "請選擇單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    new_rec = pd.DataFrame([{
                        "狀態": "借出", "職稱": role, "使用人": user, 
                        "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), 
                        "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0
                    }])
                    df_updated = pd.concat([df, new_rec], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=df_updated)
                    st.toast(f"👌 {user} 登記成功！資料已同步至雲端。", icon="👌")
                    st.rerun()

    # --- 歷史紀錄與下載備份 ---
    st.write("---")
    with st.expander("📊 查看紀錄與下載備份"):
        if not df.empty:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 下載備份 CSV", csv, "ultrasound_backup.csv", "text/csv")

if __name__ == "__main__":
    main()
