import streamlit as st
import pandas as pd
import yfinance as yf
import pymongo
from FinMind.data import DataLoader
from datetime import datetime, timedelta

# ==========================================
# 0. 介面設定
# ==========================================
st.set_page_config(page_title="獅王戰神 V108 終極決策終端", layout="wide")

# ==========================================
# 1. 核心宇宙庫 (86 檔代號+名稱)
# ==========================================
NAME_MAP = {
    "2330.TW":"台積電", "2317.TW":"鴻海", "2454.TW":"聯發科", "2382.TW":"廣達", "3231.TW":"緯創", "6669.TW":"緯穎", "2356.TW":"英業達", "2376.TW":"技嘉", "2324.TW":"仁寶", "2301.TW":"光寶科", "2395.TW":"研華", "3017.TW":"奇鋐", "3324.TW":"雙鴻", "2421.TW":"建準", "3665.TW":"貿聯-KY", "2059.TW":"川湖", "3533.TW":"嘉澤", "2308.TW":"台達電", "3034.TW":"聯詠", "2379.TW":"瑞昱", "3035.TW":"智原", "4966.TW":"譜瑞-KY", "3443.TW":"創意", "3661.TW":"世芯-KY", "3529.TWO":"力旺", "8016.TWO":"矽創", "6138.TW":"茂達", "5347.TWO":"世界先進", "6770.TW":"力積電", "3363.TW":"上詮", "3450.TW":"聯鈞", "4979.TW":"華星光", "3163.TWO":"波若威", "4908.TW":"前鼎", "6442.TW":"光聖", "3081.TW":"聯亞", "2345.TW":"智邦", "5388.TWO":"中磊", "3062.TW":"建漢", "6285.TW":"啟碁", "3704.TW":"合勤控", "2419.TW":"仲琦", "3596.TWO":"智易", "4906.TW":"正文", "2359.TW":"所羅門", "2049.TW":"上銀", "2365.TW":"昆盈", "4562.TW":"穎漢", "8374.TW":"羅昇", "6640.TW":"均華", "3680.TWO":"家登", "3019.TW":"亞光", "1513.TW":"中興電", "1519.TW":"華城", "1503.TW":"士電", "1504.TW":"東元", "1514.TW":"亞力", "6806.TW":"森崴能源", "9958.TW":"世紀鋼", "1605.TW":"華新", "1609.TW":"大亞", "1536.TW":"和大", "6217.TWO":"中探針", "3003.TW":"健和興", "9921.TW":"巨大", "9914.TW":"美利達", "2105.TW":"正新", "2106.TW":"建大", "2603.TW":"長榮", "2609.TW":"陽明", "2615.TW":"萬海", "2408.TW":"南亞科", "2344.TW":"華邦電", "3481.TW":"群創", "2409.TW":"友達", "3260.TWO":"威剛", "8299.TWO":"群聯", "6116.TW":"彩晶", "8046.TWO":"南電", "3037.TW":"欣興", "3189.TW":"景碩", "8069.TWO":"元太", "2337.TW":"旺宏", "3105.TWO":"穩懋", "6409.TW":"旭隼", "2474.TW":"可成", "6121.TWO":"新普", "2327.TW":"國巨", "2492.TW":"華新科", "2881.TW":"富邦金"
}

# ==========================================
# 2. 數據運算引擎 (原生運算 MA20 & MACD)
# ==========================================
@st.cache_data(ttl=600)
def get_analysis(tickers):
    results = []
    fm = DataLoader()
    fm.login_by_token(api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA")
    
    for symbol in tickers:
        try:
            df = yf.download(symbol, period="3mo", progress=False)
            if df.empty or len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            
            # 原生運算 MACD
            exp12 = df['Close'].ewm(span=12, adjust=False).mean()
            exp26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9, adjust=False).mean()
            hist = float((macd - signal).iloc[-1])
            
            # 戰略判斷
            if close < ma20:
                action, color = "🛑 物理隔離", "#ff4b4b"
            elif close >= ma20 and hist > 0:
                action, color = "🎯 右側強攻", "#00eb93"
            else:
                action, color = "⏳ 觀望等待", "#8b949e"

            results.append({
                "代碼": symbol.split('.')[0], "標的": NAME_MAP[symbol],
                "現價": round(close, 2), "20MA": round(ma20, 2),
                "MACD": round(hist, 2), "操盤指令": action, "_color": color
            })
        except: continue
    return pd.DataFrame(results)

# ==========================================
# 3. UI 網頁設計
# ==========================================
st.title("🦁 獅王戰神 V108 指揮部")
st.sidebar.header("🛡️ 戰略區域控制")
sector = st.sidebar.selectbox("切換防區：", ["權值/AI伺服器", "矽光子/網通", "電子/記憶體", "傳產/金融"])

# 分流邏輯
all_stocks = list(NAME_MAP.keys())
if sector == "權值/AI伺服器": targets = all_stocks[:20]
elif sector == "矽光子/網通": targets = all_stocks[20:45]
elif sector == "電子/記憶體": targets = all_stocks[45:70]
else: targets = all_stocks[70:]

with st.spinner('機台數據同步中...'):
    df = get_analysis(targets)
    if not df.empty:
        # KPI 卡片
        c1, c2, c3 = st.columns(3)
        c1.metric("今日掃描標的", f"{len(df)} 檔")
        c2.metric("多頭排列", len(df[df['操盤指令'] == '🎯 右側強攻']))
        c3.metric("需隔離數", len(df[df['操盤指令'] == '🛑 物理隔離']))
        
        # 表格上色
        def highlight(row):
            return [f'color: {row["_color"]}; font-weight: bold' if col == '操盤指令' else '' for col in row.index]
        
        st.dataframe(df.drop(columns=['_color']).style.apply(highlight, axis=1), use_container_width=True)
    else:
        st.error("API 連線中斷，請點選左側重新載入。")

st.info("💡 **紀律：** 股價在 20MA 上才買，跌破 20MA 無條件全數變現。")
