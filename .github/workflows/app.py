import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="獅王戰神 V106.50 戰情室", layout="wide")

# --- 資料庫連線 (建議從 Secrets 讀取) ---
@st.cache_resource
def init_connection():
    # 這裡建議使用 Streamlit 的 Secrets 功能，不要把密碼直接寫在裡面
    return pymongo.MongoClient("你的 MongoDB 連線字串")

client = init_connection()
db = client["crawler_db"]
collection = db["scraped_articles"]

# --- UI 設計：側邊欄 (Sidebar) ---
with st.sidebar:
    st.title("🛡️ 戰略指揮部")
    st.info("目前系統監控中：80 檔核心標的")
    
    # 讓你可以手動輸入網址進行「即時進料」
    input_url = st.text_input("🔗 導入新戰略網址:")
    if st.button("執行掃描"):
        st.warning("機台連線中... (這部分可連結到 GitHub API 觸發抓取)")

# --- 主頁面設計 ---
st.title("🦁 獅王戰神：量化決策儀表板")

# 1. 核心數據摘要 (KPI Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("今日情報量", collection.count_documents({"crawled_at": {"$gte": datetime.now().replace(hour=0)}}))
with col2:
    st.metric("利多標的 (Positive)", "12 檔", delta="2 檔") # 這邊可以連動資料庫
with col3:
    st.metric("避雷標的 (Negative)", "3 檔", delta="-1 檔", delta_color="inverse")

st.divider()

# 2. 情報明細表
st.subheader("📋 最新市場情報明細")
data = list(collection.find().sort("crawled_at", -1).limit(50))
if data:
    df = pd.DataFrame(data)
    # 整理欄位
    df = df[['crawled_at', 'title', 'category', 'impact']]
    df.columns = ['發布時間', '情報標題', '來源分類', '情緒偵測']
    
    # UI 特效：根據情緒上色
    def color_impact(val):
        color = 'red' if val == 'Positive' else 'green' if val == 'Negative' else 'white'
        return f'color: {color}'

    st.dataframe(df.style.applymap(color_impact, subset=['情緒偵測']), use_container_width=True)
else:
    st.write("目前倉庫內無物料，請檢查機台運轉狀況。")

# 3. 操盤紀律提醒
st.warning("💡 **操盤紀律：** 若情報標的出現 **Negative** 且 K 線實體跌破 **20MA**，請毫不猶豫執行物理隔離（清倉）。")
