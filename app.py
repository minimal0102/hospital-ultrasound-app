import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 資料與設定
# ==========================================
FILE_NAME = 'ultrasound_log.csv'
DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"]
ALL_STAFF = DOCTORS + NPS
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

# ==========================================
# 2. 核心功能
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
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
    
    df = load_data()
    current_status = "可借用"
    last_idx = None
    
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_idx = df.index[-1]

    # --- 高對比 滿版視覺 CSS ---
    st.markdown("""
        <style>
        /* 全域繁體中文優化 */
        html, body, [class*="css"] {
            font-family: "Microsoft JhengHei", "PingFang TC", sans-serif !important;
        }

        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        header, [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        
        .main-title { text-align: center; font-weight: 900; font-size: 2.5rem; color: #000; margin-bottom: 25px; }

        /* 儀表板：色塊背景滿版修復 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0px; }
        .info-card {
            border-radius: 24px;
            padding: 30px 5px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .bg-blue { background-color: #60A5FA !important; }
        .bg-red { background-color: #F87171 !important; }
        
        .label-text { font-size: 18px; color: #000; font-weight: 900; margin-bottom: 12px; opacity: 0.8; }
        .value-text { font-size: 42px; font-weight: 900; color: #000; letter-spacing: 1px; }

        /* 按鈕優化：純黑、20px、極粗、亮底 */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            border-radius: 18px !important;
            padding: 24px 0 !important;
            font-size: 22px !important;
            font-weight: 900 !important;
            color: #000 !important; /* 強制純黑 */
            border: none !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
        }

        .borrow-btn div[data-testid="stFormSubmitButton"] > button { background-color: #60A5FA !important; }
        .return-btn div[data-testid="stFormSubmitButton"] > button { background-color: #F87171 !important; }

        /* 修正登記身分類別橫排 */
        div[role="radiogroup"] { 
            display: flex !important; flex-direction: row !important; gap: 20px !important; 
        }
        div[role="radiogroup"] label { font-size: 18px !important; font-weight: 800 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🏥 內科超音波登記站</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 借出模式 (可登記)
    # ------------------------------------------
    if current_status == "可借用":
        st.success("### ✅ 設備在位中 (請登記)")
        
        # 身分選擇放在 Form 外以便連動
        role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
        
        st.markdown('<div class="borrow-btn">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            user = st.selectbox("借用人", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇前往單位..."] + UNIT_LIST)
            part = st.selectbox("使用部位", BODY_PARTS)
            
            st.write("")
            if st.form_submit_button("🚀 登記推走設備"):
                if loc == "請選擇前往單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role, "使用人": user, "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 歸還模式 (使用中)
    # ------------------------------------------
    else:
        last_row = df.iloc[-1]
        st.error("### ⚠️ 設備使用中")

        # 儀表板：滿版色塊修正版
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="info-card bg-blue">
                <span class="label-text">👤 使用人</span>
                <span class="value-text">{last_row['使用人']}</span>
            </div>
            <div class="info-card bg-red">
                <span class="label-text">📍 目前位置</span>
                <span class="value-text">{last_row['所在位置']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="return-btn">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.info(f"🕒 使出時間：{last_row['使用時間']}")
            # 預設歸還人為原使用人
            returner = st.selectbox("歸還確認人", ALL_STAFF, index=ALL_STAFF.index(last_row['使用人']) if last_row['使用人'] in ALL_STAFF else 0)
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常", value=False)
            
            st.write("")
            if st.form_submit_button("📦 確認歸還設備"):
                if not check:
                    st.warning("⚠️ 請先勾選確認檢查項目")
                else:
                    now = get_taiwan_time()
                    start_t = datetime.strptime(last_row['使用時間'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                    dur = round((now - start_t).total_seconds() / 60, 1)
                    df.at[last_idx, "狀態"] = "歸還"
                    df.at[last_idx, "歸還人"] = returner
                    df.at[last_idx, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_idx, "持續時間(分)"] = dur
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not df.empty:
        with st.expander("📊 查看紀錄"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
