import streamlit as st
import pymongo
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- 系統配置與 HMI 介面初始化 ---
st.set_page_config(page_title="獅王戰神 V106.60 戰情室", layout="wide")

# --- 資料庫連線模組 (使用 Streamlit Secrets 確保資安) ---
@st.cache_resource
def init_connection():
    # 讀取 Secrets 中的連線字串，避免密碼外洩
    return pymongo.MongoClient(st.secrets["mongo"]["connection_string"])

client = init_connection()
db = client["crawler_db"]
collection = db["scraped_articles"]

# --- 核心邏輯：獲取個股技術面數據 ---
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        if df.empty: return None
        
        current_price = df['Close'].iloc[-1]
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        dist_to_ma20 = ((current_price - ma20) / ma20) * 100
        
        return {
            "現價": round(current_price, 2),
            "20MA": round(ma20, 2),
            "乖離率%": round(dist_to_ma20, 2),
            "狀態": "✅ 站穩月線" if current_price >= ma20 else "⚠️ 跌破月線"
        }
    except:
        return None

# --- 側邊欄：手動進料控管 ---
with st.sidebar:
    st.title("🛡️ 戰略指揮部")
    st.subheader("產線狀態：全自動運轉")
    if st.button("🔄 強制重新整理數據"):
        st.cache_data.clear()
        st.rerun()

# --- 主網頁：個股數據戰情看板 ---
st.title("🦁 獅王戰神 V106.60：個股多空決策終端")

# 1. 讀取 MongoDB 中的情緒數據
data = list(collection.find().sort("crawled_at", -1).limit(100))
if data:
    intel_df = pd.DataFrame(data)
    
    # 2. 數據清洗：過濾無效標題與雜訊 (前端防呆)
    intel_df = intel_df[intel_df['title'].str.len() > 3]
    
    # 3. 戰略標的篩選 (假設我們只關注 Positive/Negative 的個股)
    st.subheader("📍 核心監控標的：技術面 x 情緒面")
    
    # 這裡我們模擬從新聞中萃取出股票名稱 (此處以 NAME_MAP 的邏輯進行)
    # 為了展示效果，我們建立一個動態呈現清單
    display_list = []
    unique_stocks = ["2330.TW", "2317.TW", "2454.TW", "2382.TW", "3017.TW"] # 優先監控權值股
    
    for ticker in unique_stocks:
        tech_info = get_stock_data(ticker)
        if tech_info:
            # 找尋該標的在資料庫中的最新情緒
            # (邏輯：標題若包含該股名則關聯)
            display_list.append({
                "代碼": ticker,
                "現價": tech_info["現價"],
                "20MA": tech_info["20MA"],
                "乖離率%": tech_info["乖離率%"],
                "技術面": tech_info["狀態"],
                "偵測情緒": "Positive" if ticker == "2330.TW" else "Neutral" # 範例邏輯
            })

    result_df = pd.DataFrame(display_list)
    
    # UI 呈現：使用 DataFrame 加上顏色標註
    def highlight_status(val):
        color = 'background-color: #2e7d32' if "✅" in str(val) else 'background-color: #c62828' if "⚠️" in str(val) else ''
        return color

   st.table(result_df.style.applymap(highlight_status, subset=['技術面']))

    # 4. 詳細情報明細
    st.divider()
    st.subheader("📋 原始情報追蹤 (Raw Data)")
    st.dataframe(intel_df[['crawled_at', 'title', 'impact']], use_container_width=True)
else:
    st.info("目前資料庫倉庫為空，請確認 GitHub Actions 進料狀況。")
