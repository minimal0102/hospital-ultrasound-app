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

    # 資料初始化與清空
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

    # --- 萬能 CSS 覆蓋方案：強制變更按鈕外觀 ---
    st.markdown("""
        <style>
        /* 全域字體 */
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif !important; }

        /* 移除按鈕所在的預設限制，讓它能展開 */
        div[data-testid="stForm"] { border: 1px solid #ddd; border-radius: 15px; padding: 20px; }
        
        /* 強制按鈕容器滿版 */
        div[data-testid="stFormSubmitButton"] {
            display: block !important;
            width: 100% !important;
            text-align: center !important;
        }

        /* 核心按鈕樣式：鎖定所有 stFormSubmitButton 內部的按鈕 */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            height: 80px !important;  /* 強制高度變成長方體 */
            border-radius: 12px !important;
            font-size: 26px !important;
            font-weight: 900 !important;
            border: none !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
            cursor: pointer !important;
            margin: 10px 0px !important;
        }

        /* 亮藍色登記按鈕 (透過借用標記 class) */
        .borrow-area button {
            background-color: #60A5FA !important;
            color: #000000 !important;
        }

        /* 亮紅色歸還按鈕 (透過歸還標記 class) */
        .return-area button {
            background-color: #F87171 !important;
            color: #000000 !important;
        }

        /* 讓按鈕內的文字強制置中 */
        div[data-testid="stFormSubmitButton"] button p {
            font-size: 26px !important;
            font-weight: 900 !important;
            color: #000000 !important;
            margin: 0 auto !important;
            text-align: center !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align:center;">🏥 內科超音波登記站</h1>', unsafe_allow_html=True)

    if current_status == "可借用":
        st.success("### ✅ 設備在位 (請登記使用)")
        role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
        
        # 使用 div 標記區域，讓 CSS 抓取顏色
        st.markdown('<div class="borrow-area">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            user = st.selectbox("使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("使用部位", BODY_PARTS)
            if st.form_submit_button("🚀 登記推走設備"):
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
        
        # 狀態顯示欄位
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"👤 使用人：**{last_row['使用人']}**")
        with col2:
            st.warning(f"📍 位置：**{last_row['目前位置']}**")

        st.markdown('<div class="return-area">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.write(f"🕒 借出時間：{last_row['使用時間']}")
            check = st.checkbox("✅ 探頭清潔 / 線材收納 / 功能正常")
            if st.form_submit_button("📦 歸還設備"):
                if not check:
                    st.warning("⚠️ 請先勾選確認項目")
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
        with st.expander("📊 查看歷史紀錄"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
