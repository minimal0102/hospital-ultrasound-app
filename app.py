import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
import os

# ==========================================
# 1. 設定檔
# ==========================================

FILE_NAME = 'ultrasound_log.csv'

DOCTORS = [
    "朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治",
    "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰",
    "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑",
    "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣",
    "李坤峰", "何承恩", "沈治華", "PGY醫師"
]

NPS = [
    "侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟",
    "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵",
    "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓",
    "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛期"
]

ALL_STAFF = DOCTORS + NPS

BODY_PARTS = [
    "胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)",
    "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"
]

UNIT_LIST = [
    "3A", "3B", "5A", "5B", "6A", "6B",
    "7A", "7B", "RCC", "6D", "6F", "檢查室"
]

# ==========================================
# 2. 功能函數
# ==========================================

def get_taiwan_time():
    utc_dt = datetime.now(timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8)))

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "狀態", "職稱", "借用人", "借用時間",
            "使用部位", "所在位置",
            "歸還人", "歸還時間", "持續時間(分)"
        ])
        df.to_csv(FILE_NAME, index=False)
        return df
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# ==========================================
# 3. 主程式
# ==========================================

def main():
    st.set_page_config(
        page_title="內科超音波",
        page_icon="🏥",
        layout="centered"
    )

    # ===== Apple 風格 CSS =====
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #F5F5F7;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    h1 {
        font-weight: 700;
    }
    .status-card {
        background-color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }
    .status-available {
        background-color: #E9F8EF;
        color: #1C7C54;
    }
    .status-using {
        background-color: #FDEDED;
        color: #8B0000;
    }
    .status-title {
        font-size: 0.9rem;
        color: #8E8E93;
        margin-bottom: 6px;
    }
    .status-text {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .form-card {
        background-color: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }
    .stButton button {
        background-color: #007AFF;
        color: white;
        border-radius: 14px;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
        border: none;
    }
    div[role='radiogroup'] label {
        background-color: #F2F2F7;
        padding: 10px 16px;
        border-radius: 12px;
        margin-right: 8px;
    }
    #MainMenu, footer, header {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    df = load_data()

    current_status = "可借用"
    last_index = None

    if not df.empty and df.iloc[-1]["狀態"] == "借出":
        current_status = "使用中"
        last_index = df.index[-1]

    st.title("🏥 內科超音波 登記站")

    # ===== 狀態卡 =====
    if current_status == "可借用":
        st.markdown("""
        <div class="status-card status-available">
            <div class="status-title">目前狀況</div>
            <div class="status-text">🟢 可借用</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)

        with st.form("borrow_form"):
            role = st.radio("借用人身分", ["醫師", "專科護理師"], horizontal=True)
            name_list = DOCTORS if role == "醫師" else NPS
            user = st.selectbox("借用人", name_list)
            part = st.selectbox("使用部位", BODY_PARTS)
            unit = st.selectbox("移動至單位", ["請選擇前往單位..."] + UNIT_LIST)
            submit = st.form_submit_button("登記並取走設備")

            if submit:
                if unit == "請選擇前往單位...":
                    st.error("請選擇單位")
                else:
                    now = get_taiwan_time()
                    new_row = {
                        "狀態": "借出",
                        "職稱": role,
                        "借用人": user,
                        "借用時間": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "使用部位": part,
                        "所在位置": unit,
                        "歸還人": None,
                        "歸還時間": None,
                        "持續時間(分)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success("登記完成")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        last = df.iloc[-1]

        st.markdown("""
        <div class="status-card status-using">
            <div class="status-title">目前狀況</div>
            <div class="status-text">🔴 使用中</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)

        st.metric("使用者", last["借用人"])
        st.metric("目前位置", last["所在位置"])
        st.caption(f"借出時間：{last['借用時間']}")

        with st.form("return_form"):
            default_idx = ALL_STAFF.index(last["借用人"]) if last["借用人"] in ALL_STAFF else 0
            returner = st.selectbox("歸還人", ALL_STAFF, index=default_idx)
            check = st.checkbox("我已確認設備完整")
            submit = st.form_submit_button("確認歸還")

            if submit:
                if not check:
                    st.error("請確認設備完整")
                else:
                    now = get_taiwan_time()
                    start = datetime.strptime(last["借用時間"], "%Y-%m-%d %H:%M:%S")
                    duration = round((now.replace(tzinfo=None) - start).total_seconds() / 60, 1)
                    df.at[last_index, "狀態"] = "歸還"
                    df.at[last_index, "歸還人"] = returner
                    df.at[last_index, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    df.at[last_index, "持續時間(分)"] = duration
                    save_data(df)
                    st.success("歸還完成")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== 統計區 =====
    st.markdown("---")
    st.subheader("📊 使用統計")

    if not df.empty:
        tab1, tab2 = st.tabs(["📋 紀錄", "📈 分析"])

        with tab1:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

        with tab2:
            fig = px.pie(df, names="職稱", title="使用者職稱比例", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
