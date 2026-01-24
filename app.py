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
ALL_STAFF = DOCTORS + NPS
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]

# ==========================================
# 2. 核心功能
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["狀態", "職稱", "使用人", "使用時間", "使用部位", "所在位置", "歸還人", "歸還時間", "持續時間(分)"])
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

    # --- 視覺強化版 CSS ---
    st.markdown("""
        <style>
        /* 全域字體 */
        html, body, [class*="css"] {
            font-family: "Microsoft JhengHei", "PingFang TC", sans-serif !important;
        }

        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        header, [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        
        .main-title { text-align: center; font-weight: 900; font-size: 2.2rem; color: #000; margin-bottom: 25px; }

        /* 狀態條 */
        .status-bar {
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            font-size: 22px;
            font-weight: 900;
            margin-bottom: 20px;
        }

        /* 儀表板方塊：背景色滿版修正 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0px; }
        .info-card {
            border-radius: 20px;
            padding: 25px 5px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        /* 借用人滿版亮藍色背景 */
        .bg-blue { background-color: #60A5FA !important; }
        /* 目前位置滿版亮紅色背景 */
        .bg-red { background-color: #F87171 !important; }
        
        /* 標籤文字 (借用人/目前位置) */
        .label-text { font-size: 16px; color: #000; font-weight: 900; margin-bottom: 10px; opacity: 0.8; }
        /* 數值文字 (姓名/地點) - 置中放大 */
        .value-text { font-size: 42px; font-weight: 900; color: #000; }

        /* 按鈕樣式：強制亮色、20px、純黑極粗 */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            border-radius: 16px !important;
            padding: 24px 0 !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            color: #000 !important;
            border: none !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.12) !important;
        }

        .borrow-btn div[data-testid="stFormSubmitButton"] > button { background-color: #60A5FA !important; }
        .return-btn div[data-testid="stFormSubmitButton"] > button { background-color: #F87171 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🏥 內科超音波登記站</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 借出模式 (可借用)
    # ------------------------------------------
    if current_status == "可借用":
        st.markdown('<div class="status-bar" style="background-color:#D1FAE5; color:#065F46; border:2px solid #6EE7B7;">✅ 設備在位中 (可登記)</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="borrow-btn">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
            user = st.selectbox("借用人", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇前往單位..."] + UNIT_LIST)
            part = st.selectbox("使用部位", BODY_PARTS)
            if st.form_submit_button("登記推走設備"):
                if loc == "請選擇前往單位...":
                    st.error("⚠️ 請選擇單位")
                else:
                    new_rec = {"狀態": "借出", "職稱": role, "借用人": user, "借用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "所在位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 歸還模式 (使用中)
    # ------------------------------------------
    else:
        last_row = df.iloc[-1]
        st.markdown('<div class="status-bar" style="background-color:#FFEBEC; color:#B91C1C; border:2px solid #FCA5A5;">⚠️ 設備使用中</div>', unsafe_allow_html=True)

        # 儀表板 (滿版底色修正版)
        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="info-card bg-blue">
                <span class="label-text">👤 借用人</span>
                <span class="value-text">{last_row['借用人']}</span>
            </div>
            <div class="info-card bg-red">
                <span class="label-text">📍 目前位置</span>
                <span class="value-text">{last_row['所在位置']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="return-btn">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.info(f"借出時間：{last_row['借用時間']}")
            check = st.checkbox("探頭清潔 / 線材收納 / 功能正常", value=False)
            if st.form_submit_button("確認歸還設備"):
                if not check:
                    st.warning("⚠️ 請勾選確認檢查")
                else:
                    now = get_taiwan_time()
                    start_t = datetime.strptime(last_row['借用時間'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                    dur = round((now - start_t).total_seconds() / 60, 1)
                    df.at[last_idx, "狀態"] = "歸還"
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
