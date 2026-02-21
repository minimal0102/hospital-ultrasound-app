import streamlit as st
import pandas as pd
from datetime import datetime

# --- 頁面設定 ---
st.set_page_config(page_title="內科超音波登記站", page_icon="📟")

# --- 模擬資料庫 (未來可換成 Google Sheets) ---
if 'records' not in st.session_state:
    st.session_state.records = []
if 'is_away' not in st.session_state:
    st.session_state.is_away = False
if 'last_user' not in st.session_state:
    st.session_state.last_user = ""

# --- 標題與設備狀態紅綠燈 ---
st.title("📟 內科超音波登記站")

if not st.session_state.is_away:
    st.success("### ✅ 設備在位 (可登記使用)")
else:
    st.error(f"### ⚠️ 設備使用中 (目前由 {st.session_state.last_user} 使用中)")

st.divider()

# --- 登記表單 ---
with st.container():
    # 1. 登記身分 (改成橫向按鈕)
    role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)
    
    # 2. 使用人姓名 (自動記住上次選擇)
    name_list = ["朱戈靖", "其他醫師A", "其他醫師B"] # 這裡可依需求修改
    name = st.selectbox("2. 使用人姓名", name_list)
    
    # 3. 前往單位 (增加快速按鈕區)
    st.write("3. 前往單位")
    unit_cols = st.columns(4)
    target_unit = st.text_input("或手動輸入單位", key="unit_input", placeholder="例如: 12B ICU")
    
    # 快速選擇功能
    if unit_cols[0].button("6B"): target_unit = "6B"
    if unit_cols[1].button("6A"): target_unit = "11G"
    if unit_cols[2].button("7A"): target_unit = "ER"
    if unit_cols[3].button("7B"): target_unit = "6G"

    # 4. 使用部位
    body_parts = ["胸腔 (Thoracic)", "腹部 (Abdomen)", "心臟 (Echo)", "血管 (Vascular)"]
    part = st.selectbox("4. 使用部位", body_parts)

    st.write("") # 留白
    
    # 5. 送出按鈕
    if st.button("✅ 確認登記並推走設備", use_container_width=True):
        if not target_unit:
            st.warning("請選擇或輸入前往單位！")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_record = {"時間": now, "身分": role, "姓名": name, "單位": target_unit, "部位": part}
            st.session_state.records.insert(0, new_record) # 新紀錄在最上面
            st.session_state.is_away = True
            st.session_state.last_user = name
            st.balloons()
            st.success(f"登記成功！設備已由 {name} 推往 {target_unit}")

    # 6. 歸還按鈕
    if st.session_state.is_away:
        if st.button("🔄 設備已歸還 (回位)", type="primary", use_container_width=True):
            st.session_state.is_away = False
            st.rerun()

st.divider()

# --- 歷史紀錄區 ---
st.subheader("📋 最近登記紀錄")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records).head(5)
    st.table(df) # 顯示最近五筆
else:
    st.info("目前尚無登記紀錄")

# --- 頁尾資訊 ---
st.caption("備註：本系統僅供內部設備追蹤使用。")
