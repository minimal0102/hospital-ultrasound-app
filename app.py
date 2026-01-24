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
    """刪除舊檔案並建立全新的資料結構"""
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

    # 確保資料清空：如果是第一次執行，重置資料
    if 'initialized' not in st.session_state:
        df = reset_and_load_data()
        st.session_state.initialized = True
    else:
        if os.path.exists(FILE_NAME):
            df = pd.read_csv(FILE_NAME, encoding='utf-8-sig')
        else:
            df = reset_and_load_data()

    current_status = "可借用"
    last_idx = None
    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_idx = df.index[-1]

    # --- 強力 CSS 修正：解決按鈕縮小問題 ---
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-family: "Microsoft JhengHei", sans-serif !important;
        }

        /* 標題與背景 */
        [data-testid="stAppViewContainer"] { background-color: #F2F2F7 !important; }
        .main-title { text-align: center; font-weight: 900; font-size: 2.5rem; color: #000; margin-bottom: 25px; }

        /* 儀表板卡片 */
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0px; }
        .info-card { border-radius: 25px; padding: 40px 10px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .bg-blue { background-color: #60A5FA !important; }
        .bg-red { background-color: #F87171 !important; }
        .value-text { font-size: 45px; font-weight: 900; color: #000; }

        /* 核心按鈕修正：強制取代白色方塊 */
        div[data-testid="stFormSubmitButton"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }

        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            min-height: 70px !important;
            border-radius: 15px !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
            transition: all 0.2s ease;
        }

        /* 根據父層 class 切換顏色 */
        .borrow-btn div[data-testid="stFormSubmitButton"] > button {
            background-color: #60A5FA !important; /* 亮藍色 */
        }
        .return-btn div[data-testid="stFormSubmitButton"] > button {
            background-color: #F87171 !important; /* 亮紅色 */
        }
        
        button:active { transform: scale(0.98); }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">🏥 內科超音波登記站</div>', unsafe_allow_html=True)

    # 1. 登記模式
    if current_status == "可借用":
        st.success("### ✅ 設備在位 (請登記使用)")
        role = st.radio("登記身分", ["醫師", "專科護理師"], horizontal=True)
        
        # 使用自定義容器包裹 Form
        st.markdown('<div class="borrow-btn">', unsafe_allow_html=True)
        with st.form("borrow_form"):
            user = st.selectbox("使用人姓名", DOCTORS if role == "醫師" else NPS)
            loc = st.selectbox("前往單位", ["請選擇單位..."] + UNIT_LIST)
            part = st.selectbox("使用部位", BODY_PARTS)
            
            # 按鈕
            submit = st.form_submit_button("🚀 登記設備")
            if submit:
                if loc == "請選擇單位...":
                    st.error("⚠️ 請務必選擇目的地單位")
                else:
                    new_rec = {
                        "狀態": "借出", "職稱": role, "使用人": user, 
                        "使用時間": get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S"), 
                        "使用部位": part, "目前位置": loc, "歸還人": "", "歸還時間": "", "持續時間(分)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_rec])], ignore_index=True)
                    save_data(df)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. 歸還模式
    else:
        last_row = df.iloc[-1]
        st.error("### ⚠️ 設備目前使用中")
        st.markdown(f"""
            <div class="dashboard-grid">
                <div class="info-card bg-blue">
                    <span style="font-size:18px; font-weight:900;">👤 使用人</span><br>
                    <span class="value-text">{last_row['使用人']}</span>
                </div>
                <div class="info-card bg-red">
                    <span style="font-size:18px; font-weight:900;">📍 目前位置</span><br>
                    <span class="value-text">{last_row['目前位置']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="return-btn">', unsafe_allow_html=True)
        with st.form("return_form"):
            st.info(f"🕒 借出時間：{last_row['使用時間']}")
            check = st.checkbox("✅ 探頭清潔 / 線材收納 / 功能正常", value=False)
            
            # 按鈕
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

    # 3. 顯示紀錄
    if not df.empty:
        with st.expander("📊 查看紀錄"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

if __name__ == "__main__":
    main()
