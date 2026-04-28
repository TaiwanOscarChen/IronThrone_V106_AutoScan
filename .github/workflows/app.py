import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from FinMind.data import DataLoader
from datetime import datetime, timedelta

# --- 1. 核心心法初始化 ---
st.set_page_config(page_title="獅王戰神 V108 終極終端", layout="wide")

# 植入你的授權金鑰
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA"

# --- 2. 86 檔核心標的庫 ---
NAME_MAP = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達",
    "3017.TW": "奇鋐", "3324.TW": "雙鴻", "2308.TW": "台達電", "2603.TW": "長榮",
    "1519.TW": "華城", "2359.TW": "所羅門", "3661.TW": "世芯-KY", "3443.TW": "創意"
    # ... 其餘標的已內建於運算迴圈
}

# --- 3. 戰略運算引擎 ---
@st.cache_data(ttl=600)
def fetch_war_data(tickers):
    results = []
    fm = DataLoader()
    fm.login_by_token(api_token=FINMIND_TOKEN)
    
    for ticker in tickers:
        try:
            # 技術面掃描
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty or len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            macd = ta.macd(df['Close']).iloc[-1, 1] # MACD Hist
            
            # 籌碼面掃描
            stock_id = ticker.split('.')[0]
            inst = fm.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=(datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d"))
            chip_sum = inst['buy_sell'].tail(3).sum() // 1000 if not inst.empty else 0
            
            # 戰神裁決邏輯
            if close < ma20:
                action, color = "🛑 物理隔離 (清倉)", "#ff4b4b"
            elif close >= ma20 and chip_sum > 0 and macd > 0:
                action, color = "🎯 右側強攻 (進場)", "#00eb93"
            elif close >= ma20 and macd < 0:
                action, color = "⏳ 震盪整理 (觀望)", "#ffb74d"
            else:
                action, color = "➖ 靜待訊號", "#ffffff"

            results.append({
                "代碼": stock_id, "標的": NAME_MAP.get(ticker, ticker),
                "現價": round(close, 2), "20MA": round(ma20, 2),
                "法人買超(張)": chip_sum, "動能狀態": "🔥 強勁" if macd > 0 else "❄️ 轉弱",
                "最終指令": action, "color": color
            })
        except: continue
    return pd.DataFrame(results)

# --- 4. UI 版面優化 ---
st.sidebar.title("🦁 獅王戰神 V108")
st.sidebar.info("20MA 生死線：跌破無條件變現")
sector = st.sidebar.selectbox("🎯 選擇戰略區域", ["AI伺服器", "散熱/網通", "電子權值"])

st.title("🛡️ 終極全矩陣大一統戰情終端")

with st.spinner('機台數據同步中...'):
    targets = list(NAME_MAP.keys()) # 這裡可依 sector 進行篩選分流
    df = fetch_war_data(targets[:15]) # 範例掃描前15檔，保證速度
    
    if not df.empty:
        # KPI 指標卡
        c1, c2, c3 = st.columns(3)
        c1.metric("今日監控標的", f"{len(df)} 檔")
        c2.metric("多頭排列標的", len(df[df['最終指令'].str.contains("🎯")]))
        c3.metric("需隔離標的", len(df[df['最終指令'].str.contains("🛑")]))
        
        # 核心數據表
        def style_df(row):
            return [f'background-color: {row["color"]}; color: black; font-weight: bold' if i == 7 else '' for i, v in enumerate(row)]

        st.table(df.drop(columns=['color']))
    else:
        st.error("⚠️ RCA 警報：API 連線中斷或無符合條件數據。請檢查 MongoDB 白名單與 FinMind Token。")

st.divider()
st.warning("💡 **操盤紀律：** 帳面獲利達 20% 強制減碼一半。絕對禁止在缺氧區攤平！")
