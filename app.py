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

def reset_and_load_data():
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    df = pd.DataFrame(columns=["狀態", "職稱", "使用人", "使用時間", "使用部位", "目前位置", "歸還人", "歸還時間", "持續時間(分)"])
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    return df

def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')

# ==========================================
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    if 'initialized' not in st.session_state:
        df = reset_and_load_data()
        st.session_state.initialized = True
    else:
        df = pd.read_csv(FILE_NAME, encoding='utf-8-sig') if os.path.exists(FILE_NAME) else reset_and_load_data()

    current_status = "可借用"
    last_idx = None
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_idx = df.index[-1]

    # --- 強力 CSS 修正：選單向下開啟、黑框線、按鈕與儀表板隔離 ---
    st.markdown("""
        <style>
        /* 1. 全域與選單框線：強制黑色框線 */
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }

        /* 修改下拉選單外框為黑色 */
        div[data-baseweb="select"] > div {
            border: 1.5px solid #000000 !important;
            border-radius: 8px !important;
        }

        /* 2. 強制下拉選單向下開啟 (避免跑到標題上面) */
        div[data-baseweb="popover"] {
            margin-top: 4px !important;
            top: auto !important;
        }

        /* 3. 阻擋手機鍵盤彈出 (針對 selectbox) */
        div[data-baseweb="select"] input {
            inputmode: none !important;
            caret-color: transparent !important;
        }

        /* 4. 上方資訊儀表板 (保留樣式) */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0px; }
        .info-card {
            border-radius: 20px;
            padding: 30px 10px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            color: #000 !important;
        }
        .status-blue { background-color: #60A5FA !important; }
        .status-red { background-color: #F87171 !important; }
        .card-label { font-size: 18px; font-weight: 900; opacity: 0.8; }
        .card-value { font-size: 42px; font-weight: 900; display: block; margin-top: 5px; }

        /* 5. 按鈕專屬樣式 (長方形、滿版、亮藍/紅) */
        .borrow-section div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            height: 70px !important;
            background-color: #60A5FA !important;
            color: #000000 !important;
            border-radius: 12px !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            border: none !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        .return-section div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            height: 70px !important;
            background-color: #F87171 !important;
            color: #000000 !important;
            border-radius: 12px !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            border: none !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        div[data-testid="stFormSubmitButton"] button p {
            color: #000000 !important;
            font-size: 24px !important;
            font-weight: 900 !important;
        }
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
                    new_rec = {"狀態": "借出", "職稱": role, "使用人": user, "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0}
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
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
                    st.warning("⚠️ 請先勾選確認清消項目")
                else:
                    now = get_taiwan_time()
                    start_t = datetime.strptime(last_row['使用時間'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
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
