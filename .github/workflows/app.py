import streamlit as st
import pandas as pd
import yfinance as yf
import pymongo
from FinMind.data import DataLoader
from datetime import datetime, timedelta

# ==========================================
# 1. 介面與資料庫設定
# ==========================================
st.set_page_config(page_title="獅王戰神 V108 終極面板", layout="wide", initial_sidebar_state="expanded")

# MongoDB 連線 (為確保首次上線成功，先採直接連線，後續請至 MongoDB 更改密碼並改用 Secrets)
MONGO_URI = "mongodb+srv://qianhao_chen:Aa0983770098@cluster0.gdnkemb.mongodb.net/?appName=Cluster0"

@st.cache_resource
def init_db():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        return client["crawler_db"]["scraped_articles"]
    except:
        return None

collection = init_db()

# ==========================================
# 2. 核心股票池 (精選高流動性標的)
# ==========================================
NAME_MAP = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "3017.TW": "奇鋐", "3324.TW": "雙鴻", "2308.TW": "台達電", 
    "2603.TW": "長榮", "1519.TW": "華城", "3443.TW": "創意", "3661.TW": "世芯-KY",
    "3034.TW": "聯詠", "2379.TW": "瑞昱", "3711.TW": "日月光投控", "2303.TW": "聯電"
}

# ==========================================
# 3. 量價結構與籌碼運算引擎 (原生 Pandas 運算，確保不當機)
# ==========================================
@st.cache_data(ttl=900)
def analyze_market_data(tickers):
    fm = DataLoader()
    # 填入你的 FinMind Token
    fm.login_by_token(api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA")
    
    results = []
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    for ticker in tickers:
        try:
            # A. 抓取價量
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty or len(df) < 26: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(window=20).mean().iloc[-1])
            
            # 原生 MACD 運算
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = float((macd_line - signal_line).iloc[-1])
            
            # B. 抓取籌碼 (處理 API 限制)
            stock_id = ticker.split('.')[0]
            inst_buy = 0
            try:
                inst_data = fm.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=start_date)
                if not inst_data.empty:
                    inst_buy = int(inst_data[inst_data['name'].isin(['投信', '外資及陸資(不含外資自營商)'])]['buy_sell'].tail(3).sum() // 1000)
            except:
                pass
            
            # C. 操盤紀律判定
            profit_margin = ((close - ma20) / ma20) * 100
            
            if close < ma20:
                action = "🛑 跌破 20MA (停損)"
                color = "#ff4b4b"
            elif profit_margin >= 20:
                action = "💰 獲利達 20% (減碼)"
                color = "#d29922"
            elif close >= ma20 and inst_buy > 0 and macd_hist > 0:
                action = "🎯 右側強攻 (進場)"
                color = "#00eb93"
            else:
                action = "⏳ 區間震盪 (觀望)"
                color = "#8b949e"
                
            results.append({
                "代碼": stock_id,
                "標的": NAME_MAP[ticker],
                "現價": round(close, 2),
                "20MA": round(ma20, 2),
                "乖離率(%)": round(profit_margin, 2),
                "MACD柱": round(macd_hist, 2),
                "法人連買(張)": inst_buy,
                "戰略指令": action,
                "_color": color
            })
        except:
            continue
            
    return pd.DataFrame(results)

# ==========================================
# 4. HMI 視覺化戰情面板
# ==========================================
st.sidebar.title("🦁 獅王戰神 V108")
st.sidebar.markdown("---")
st.sidebar.subheader("⚔️ 操盤鐵律")
st.sidebar.success("1. 股價站穩 20MA 方可佈局。")
st.sidebar.warning("2. 帳面獲利達 20% 強制減碼。")
st.sidebar.error("3. 實體跌破 20MA 無條件停損。")
st.sidebar.markdown("---")
if st.sidebar.button("🔄 重新載入盤勢"):
    st.cache_data.clear()

st.title("📊 量價結構與籌碼決策矩陣")

with st.spinner('連線中：執行量價與籌碼交叉比對...'):
    df_signals = analyze_market_data(list(NAME_MAP.keys()))
    
    if not df_signals.empty:
        # 動態 KPI
        col1, col2, col3 = st.columns(3)
        col1.metric("監控標的總數", f"{len(df_signals)} 檔")
        col2.metric("強攻進場標的", len(df_signals[df_signals['戰略指令'].str.contains('強攻')]))
        col3.metric("跌破停損標的", len(df_signals[df_signals['戰略指令'].str.contains('跌破')]))
        
        st.divider()
        
        # 隱藏顏色控制欄位，並將顏色映射到表格
        display_df = df_signals.drop(columns=['_color'])
        
        def highlight_actions(row):
            color = df_signals.loc[df_signals['代碼'] == row['代碼'], '_color'].values[0]
            return [f'color: {color}; font-weight: bold;' if col == '戰略指令' else '' for col in row.index]

        st.dataframe(display_df.style.apply(highlight_actions, axis=1), use_container_width=True)
    else:
        st.error("無法取得市場數據，請檢查網路連線或 API 狀態。")

st.divider()
st.subheader("📡 MongoDB 雲端情報庫 (即時收錄)")

if collection is not None:
    db_data = list(collection.find().sort("crawled_at", -1).limit(10))
    if db_data:
        news_df = pd.DataFrame(db_data)[['crawled_at', 'title', 'impact']]
        news_df.columns = ['時間', '市場情報', '情緒判定']
        
        def style_impact(val):
            color = '#ff4b4b' if val == 'Negative' else '#00eb93' if val == 'Positive' else '#8b949e'
            return f'color: {color}; font-weight: bold;'
            
        st.dataframe(news_df.style.map(style_impact, subset=['情緒判定']), use_container_width=True)
    else:
        st.info("資料庫目前無最新情報。")
else:
    st.error("MongoDB 連線失敗，請確認 Atlas Network Access 是否設定為 0.0.0.0/0。")
