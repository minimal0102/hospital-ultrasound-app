import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 資料與設定 
# ==========================================
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1u8KVq46vpgYh9mIdtsVFGvRynOE_hiGbTNIgnr6mrv4/edit"

DOCTORS = ["朱戈靖", "王國勳", "張書軒", "陳翰興", "吳令治", "石振昌", "王志弘", "鄭穆良", "蔡均埏", "楊振杰", "趙令瑞", "許智凱", "林純全", "孫宏傑", "繆偉傑", "陳翌真", "卓俊宏", "林斈府", "葉俊麟", "莊永鑣", "李坤峰", "何承恩", "沈治華", "PGY醫師", "_____(自行填入)"]
NPS = ["侯束靜", "詹美足", "林聖芬", "林忻潔", "徐志娟", "葉思瑀", "曾筑嬛", "黃嘉鈴", "蘇柔如", "劉玉涵", "林明珠", "顏辰芳", "陳雅惠", "王珠莉", "林心蓓", "金雪珍", "邱銨", "黃千盈", "許瑩瑄", "張宛琪"]
UNIT_LIST = ["3A", "3B", "5A", "5B", "6A", "6B", "7A", "7B", "RCC", "6D", "6F", "檢查室"]
BODY_PARTS = ["胸腔 (Thoracic)", "心臟 (Cardiac)", "腹部 (Abdominal)", "膀胱 (Bladder)", "下肢 (Lower Limb)", "靜脈留置 (IV insertion)"]

# 初始化雲端連線
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. 核心功能 
# ==========================================
def get_taiwan_time():
    return datetime.now(timezone(timedelta(hours=8)))

def load_data_fresh():
    try:
        df = conn.read(spreadsheet=GSHEET_URL, worksheet="Sheet1", ttl=0)
        if not df.empty:
            df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame(columns=["狀態", "職稱", "使用人", "使用時間", "使用部位", "目前位置", "歸還人", "歸還時間", "持續時間(分)"])

def save_data(df):
    conn.update(spreadsheet=GSHEET_URL, worksheet="Sheet1", data=df)

# ==========================================
# 3. 主程式介面
# ==========================================
def main():
    st.set_page_config(page_title="內科超音波登記站", page_icon="🏥", layout="centered")

    df = load_data_fresh()
    
    current_status = "可借用"
    last_idx = None
    if not df.empty:
        last_record = df.iloc[-1]
        if str(last_record["狀態"]).strip() == "借出":
            current_status = "使用中"
            last_idx = df.index[-1]

    # ✨ CSS 樣式 (包含修復按鈕背景的設定)
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-family: "Microsoft JhengHei", "PingFang TC", sans-serif !important; }
        [data-testid="stAppViewContainer"] { background-color: #F8FAFC !important; }
        .block-container { max-width: 650px !important; padding-top: 2rem !important; }
        div[data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
        div[data-baseweb="select"] > div, input { border-radius: 10px !important; border: 1.5px solid #E2E8F0 !important; }
        div[data-baseweb="select"] > div:focus-within, input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 1px #3B82F6 !important; }
        .status-banner { padding: 20px; border-radius: 16px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .banner-available { background: linear-gradient(135deg, #10B981, #059669); }
        .banner-in-use { background: linear-gradient(135deg, #EF4444, #DC2626); }
        .banner-title { font-size: 28px; font-weight: 900; margin: 0; letter-spacing: 1px;}
        .info-card-container { display: flex; gap: 15px; margin-bottom: 25px; }
        .info-card { flex: 1; background: white; padding: 20px 15px; border-radius: 16px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #F1F5F9; }
        .info-label { color: #64748B; font-size: 14px; font-weight: bold; margin-bottom: 5px; display: block; }
        .info-value { color: #0F172A; font-size: 26px; font-weight: 900; margin: 0; }
        
        /* 表單按鈕共用基礎樣式 */
        div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important; height: 70px !important;
            border-radius: 16px !important; border: none !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stFormSubmitButton"] button p { 
            font-size: 22px !important; font-weight: 900 !important; color: white !important; 
        }
        div[data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-3px) !important; filter: brightness(1.1); }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h2 style="text-align:center; font-weight:900; color:#1E293B; margin-bottom: 20px;">🏥 內科超音波登記站</h2>', unsafe_allow_html=True)

    if current_status == "可借用":
        # 動態注入：借用狀態專屬的藍色按鈕樣式
        st.markdown("""
            <style>
            div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
                box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3) !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="status-banner banner-available">
                <p class="banner-title">✅ 設備在位 (可借用)</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            role = st.radio("1. 登記身分", ["醫師", "專科護理師"], horizontal=True)

            with st.form("borrow_form"):
                st.markdown("##### 📝 填寫借用資訊")
                user_select = st.selectbox("2. 使用人姓名", DOCTORS if role == "醫師" else NPS)
                
                custom_user = st.text_input("2-1. 補充姓名 (⚠️ 上方選「自行填入」時才需填寫，其餘請留空)", placeholder="請輸入姓名...")
                
                col1, col2 = st.columns(2)
                with col1:
                    loc = st.selectbox("3. 前往單位", ["請選擇..."] + UNIT_LIST)
                with col2:
                    part = st.selectbox("4. 使用部位", BODY_PARTS)
                
                st.markdown("<br>", unsafe_allow_html=True) 
                
                if st.form_submit_button("登記推走設備"):
                    final_user = custom_user.strip() if user_select == "_____(自行填入)" else user_select
                    
                    if user_select == "_____(自行填入)" and not final_user:
                        st.error("⚠️ 請在「2-1. 補充姓名」欄位輸入醫師姓名")
                    elif loc == "請選擇...":
                        st.error("⚠️ 請務必選擇目的地單位")
                    else:
                        now_str = get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S")
                        
                        new_rec = pd.DataFrame([{
                            "狀態": "借出", "職稱": role, "使用人": final_user, 
                            "使用時間": now_str, "使用部位": part, "目前位置": loc, 
                            "歸還人": "", "歸還時間": "", "持續時間(分)": 0
                        }])
                        
                        df_latest = load_data_fresh()
                        df_updated = pd.concat([df_latest, new_rec], ignore_index=True)
                        save_data(df_updated)
                        st.rerun()

    else:
        last_row = df.iloc[-1]
        
        # 動態注入：歸還狀態專屬的橘色按鈕樣式
        st.markdown("""
            <style>
            div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(135deg, #F59E0B, #D97706) !important;
                box-shadow: 0 6px 15px rgba(245, 158, 11, 0.3) !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="status-banner banner-in-use">
                <p class="banner-title">⚠️ 設備使用中</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="info-card-container">
                <div class="info-card">
                    <span class="info-label">👤 使用人</span>
                    <p class="info-value">{last_row['使用人']}</p>
                </div>
                <div class="info-card">
                    <span class="info-label">📍 目前位置</span>
                    <p class="info-value">{last_row['目前位置']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("return_form"):
            st.info(f"🕒 借出時間：{last_row['使用時間']}")
            st.markdown("##### ✅ 歸還確認清單")
            check = st.checkbox("我確認：探頭已清潔 / 線材已收納 / 功能皆正常", value=False)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("確認歸還設備"):
                if not check:
                    st.warning("⚠️ 請先勾選上方的確認項目")
                else:
                    now = get_taiwan_time()
                    try:
                        start_t = datetime.strptime(str(last_row['使用時間']), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=8)))
                        total_mins = (now - start_t).total_seconds() / 60
                        
                        if total_mins > 60:
                            dur = f"{round(total_mins / 60, 1)}小時"
                        else:
                            dur = f"{round(total_mins, 1)}分鐘"
                    except:
                        dur = "0分鐘"
                    
                    df_latest = load_data_fresh()
                    if not df_latest.empty:
                        last_idx_fresh = df_latest.index[-1]
                        df_latest.at[last_idx_fresh, "狀態"] = "歸還"
                        df_latest.at[last_idx_fresh, "歸還時間"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # ✨ 修復 TypeError：強制轉為字串以相容「分鐘/小時」的中文字
                        df_latest['持續時間(分)'] = df_latest['持續時間(分)'].astype(str)
                        df_latest.at[last_idx_fresh, "持續時間(分)"] = dur
                        
                        save_data(df_latest)
                    st.rerun()

    # ==========================================
    # 4. 查看紀錄與統計圖表 (僅顯示當月)
    # ==========================================
    if not df.empty:
        st.divider()
        with st.expander("📊 查看與統計 (當月紀錄)"):
            df_display = df.copy()
            df_display.columns = df_display.columns.str.strip()
            
            df_display['時間解析'] = pd.to_datetime(df_display['使用時間'], errors='coerce')
            now = get_taiwan_time()
            
            mask = (df_display['時間解析'].dt.year == now.year) & (df_display['時間解析'].dt.month == now.month)
            df_current_month = df_display[mask].copy()
            
            if not df_current_month.empty:
                st.markdown("#### 📈 當月統計圖表")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**👤 依使用人次數**")
                    user_counts = df_current_month['使用人'].value_counts()
                    st.bar_chart(user_counts, color="#3B82F6") 
                    
                with col2:
                    st.markdown("**📍 依使用部位次數**")
                    part_counts = df_current_month['使用部位'].value_counts()
                    st.bar_chart(part_counts, color="#10B981") 
                
                st.markdown("#### 📋 當月詳細紀錄")
                df_current_month = df_current_month.drop(columns=['時間解析'])
                st.dataframe(df_current_month.sort_index(ascending=False), use_container_width=True)
            else:
                st.info("📅 跨月已更新：本月目前尚無使用紀錄。")

if __name__ == "__main__":
    main()
