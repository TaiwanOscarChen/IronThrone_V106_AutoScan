import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import pymongo
from FinMind.data import DataLoader
from datetime import datetime, timedelta
import requests
import feedparser

# ==========================================
# 0. 系統環境配置 (V108 全矩陣完全體)
# ==========================================
st.set_page_config(page_title="獅王戰神 V108 終極決策終端", layout="wide")

# FinMind 深度授權
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA"
fm = DataLoader()
fm.login_by_token(api_token=FINMIND_TOKEN)

# ==========================================
# 1. 核心宇宙庫 (86 檔全矩陣戰略清單)
# ==========================================
NAME_MAP = {
    "2330.TW":"台積電", "2317.TW":"鴻海", "2454.TW":"聯發科", "2382.TW":"廣達", 
    "3231.TW":"緯創", "6669.TW":"緯穎", "2356.TW":"英業達", "2376.TW":"技嘉", 
    "2324.TW":"仁寶", "2301.TW":"光寶科", "2395.TW":"研華", "3017.TW":"奇鋐", 
    "3324.TW":"雙鴻", "2421.TW":"建準", "3665.TW":"貿聯-KY", "2059.TW":"川湖", 
    "3533.TW":"嘉澤", "2308.TW":"台達電", "3443.TW":"創意", "3661.TW":"世芯-KY", 
    "3035.TW":"智原", "3034.TW":"聯詠", "2379.TW":"瑞昱", "4966.TW":"譜瑞-KY", 
    "3529.TWO":"力旺", "8016.TWO":"矽創", "6138.TW":"茂達", "5347.TWO":"世界先進", 
    "6770.TW":"力積電", "3363.TW":"上詮", "3450.TW":"聯鈞", "4979.TW":"華星光", 
    "3163.TWO":"波若威", "4908.TW":"前鼎", "6442.TW":"光聖", "3081.TW":"聯亞", 
    "2345.TW":"智邦", "5388.TWO":"中磊", "3062.TW":"建漢", "6285.TW":"啟碁", 
    "3704.TW":"合勤控", "2419.TW":"仲琦", "3596.TWO":"智易", "4906.TW":"正文", 
    "2359.TW":"所羅門", "2049.TW":"上銀", "2365.TW":"昆盈", "4562.TW":"穎漢", 
    "8374.TW":"羅昇", "6640.TW":"均華", "3680.TWO":"家登", "3019.TW":"亞光", 
    "1513.TW":"中興電", "1519.TW":"華城", "1503.TW":"士電", "1504.TW":"東元", 
    "1514.TW":"亞力", "6806.TW":"森崴能源", "9958.TW":"世紀鋼", "1605.TW":"華新", 
    "1609.TW":"大亞", "2408.TW":"南亞科", "2344.TW":"華邦電", "3481.TW":"群創", 
    "2409.TW":"友達", "3260.TWO":"威剛", "8299.TWO":"群聯", "6116.TW":"彩晶", 
    "2337.TW":"旺宏", "2303.TW":"聯電", "2603.TW":"長榮", "2609.TW":"陽明", 
    "2615.TW":"萬海", "1536.TW":"和大", "9921.TW":"巨大", "9914.TW":"美利達", 
    "2105.TW":"正新", "2106.TW":"建大", "6217.TWO":"中探針", "3003.TW":"健和興", 
    "6409.TW":"旭隼", "2474.TW":"可成", "6121.TWO":"新普", "2327.TW":"國巨", 
    "2492.TW":"華新科", "2881.TW":"富邦金"
}

# ==========================================
# 2. 數據獲取與戰術運算 (邏輯精華)
# ==========================================
@st.cache_data(ttl=900)
def run_lion_war_engine(ticker_list):
    summary_data = []
    for ticker in ticker_list:
        try:
            # A. 技術指標 (yfinance)
            df = yf.download(ticker, period="3mo", progress=False)
            if df.empty or len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close = df['Close'].iloc[-1]
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            vol_5ma = df['Volume'].rolling(5).mean().iloc[-1]
            vol_today = df['Volume'].iloc[-1]
            
            # B. 籌碼偵測 (FinMind)
            stock_id = ticker.split('.')[0]
            inst = fm.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=(datetime.now()-timedelta(days=5)).strftime("%Y-%m-%d"))
            inst_buy = inst[inst['name'].isin(['投信', '外資及陸資(不含外資自營商)'])]['buy_sell'].sum() // 1000
            
            # C. 戰略裁決
            status = "站穩 20MA" if close >= ma20 else "跌破 20MA"
            vol_signal = "🔥 爆量" if vol_today > vol_5ma * 1.5 else "➖ 平穩"
            
            if close < ma20:
                cmd = "🛑 物理隔離 (清倉)"
            elif close >= ma20 and inst_buy > 0:
                cmd = "🎯 右側強攻 (加碼)"
            else:
                cmd = "⏳ 觀望等待"
                
            summary_data.append({
                "代碼": stock_id, "標的": NAME_MAP[ticker], "收盤": round(close, 2),
                "20MA": round(ma20, 2), "法人連買(張)": inst_buy, "量能": vol_signal,
                "技術態勢": status, "戰略指令": cmd
            })
        except: continue
    return pd.DataFrame(summary_data)

# ==========================================
# 3. 網頁版面設計 (UI 控制中心)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/lion-head.png")
    st.title("🦁 獅王戰神 V108")
    st.markdown("---")
    st.header("🧠 操盤手核心鐵律")
    st.warning("**20MA 生死線**：跌破無條件變現")
    st.success("**停利紀律**：獲利 20% 強制減碼一半")
    st.error("**停損紀律**：虧損 5% 強制執行市價單")
    st.markdown("---")
    
    sector = st.selectbox("🎯 打擊防區選擇：", [
        "全部標的", "AI 與 伺服器", "散熱與網通", "電子與半導體", "傳產與金融"
    ])
    
    if st.button("🚀 啟動全矩陣掃描"):
        st.cache_data.clear()

st.title("🛡️ 獅王戰神 V108：終極全矩陣大一統終端")

# 宏觀指標
m_col1, m_col2, m_col3 = st.columns(3)
try:
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    tsm = yf.Ticker("TSM").history(period="1d")['Close'].iloc[-1]
    m_col1.metric("VIX 恐慌指數", f"{vix:.2f}", "🟢 穩定" if vix < 25 else "🚨 恐慌", delta_color="inverse")
    m_col2.metric("台積電 ADR", f"{tsm:.1f}")
    m_col3.metric("系統狀態", "V108.9 滿配運轉")
except:
    st.info("宏觀數據抓取中...")

# 主功能分頁
tab1, tab2, tab3 = st.tabs(["⚔️ 戰略決策矩陣", "📡 籌碼基本面掃描", "📰 市場多空情報"])

with tab1:
    with st.spinner('機台高頻運算中...'):
        # 過濾標的 (模擬 86 檔分流)
        targets = list(NAME_MAP.keys())
        if sector == "AI 與 伺服器": targets = targets[:10]
        elif sector == "散熱與網通": targets = targets[10:35]
        
        df_res = run_lion_war_engine(targets[:20]) # 限制 20 檔以維護免費機台速度
        
        def color_cmd(val):
            if "物理隔離" in str(val): return 'color: #ff4b4b; font-weight: bold;'
            if "強攻" in str(val): return 'color: #00eb93; font-weight: bold;'
            return ''
            
        st.dataframe(df_res.style.map(color_cmd, subset=['戰略指令']), use_container_width=True)

with tab2:
    st.subheader("🏛️ TWSE OpenAPI 官方估值矩陣")
    # 此處可加入 TWSE 官方數據展示邏輯
    st.info("模組二十二至二十四：FinMind 深度參數計算中...")

with tab3:
    st.subheader("📡 即時市場多空情緒雷達 (Yahoo RSS)")
    feed = feedparser.parse("https://tw.stock.yahoo.com/rss")
    for entry in feed.entries[:5]:
        with st.expander(f"📌 {entry.title}"):
            st.write(f"時間: {entry.published}")
            st.write(f"[連結]({entry.link})")
