import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import pymongo
from FinMind.data import DataLoader
from datetime import datetime, timedelta
import requests

# ==========================================
# 0. 系統防護層與 HMI 初始化
# ==========================================
st.set_page_config(page_title="獅王戰神 V108 終極決策終端", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. 核心資料庫 (86 檔全矩陣戰略名單)
# ==========================================
NAME_MAP = {
    # 【權值與 AI 伺服器】
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2382.TW": "廣達", 
    "3231.TW": "緯創", "6669.TW": "緯穎", "2356.TW": "英業達", "2376.TW": "技嘉", 
    "2324.TW": "仁寶", "2395.TW": "研華", "3711.TW": "日月光投控",
    # 【散熱與零組件】
    "3017.TW": "奇鋐", "3324.TW": "雙鴻", "2421.TW": "建準", "3665.TW": "貿聯-KY", 
    "2059.TW": "川湖", "3533.TW": "嘉澤", "2308.TW": "台達電", "2301.TW": "光寶科", 
    "2327.TW": "國巨", "2492.TW": "華新科",
    # 【IC 設計與矽智財】
    "3443.TW": "創意", "3661.TW": "世芯-KY", "3035.TW": "智原", "3034.TW": "聯詠", 
    "2379.TW": "瑞昱", "4966.TW": "譜瑞-KY", "3529.TWO": "力旺", "8016.TWO": "矽創", 
    "6138.TW": "茂達",
    # 【晶圓代工與記憶體】
    "2303.TW": "聯電", "5347.TWO": "世界先進", "6770.TW": "力積電", "2408.TW": "南亞科", 
    "2344.TW": "華邦電", "2337.TW": "旺宏", "3260.TWO": "威剛", "8299.TWO": "群聯",
    # 【矽光子 CPO 與 網通】
    "3363.TW": "上詮", "3450.TW": "聯鈞", "4979.TW": "華星光", "3163.TWO": "波若威", 
    "4908.TW": "前鼎", "6442.TW": "光聖", "3081.TW": "聯亞", "2345.TW": "智邦", 
    "5388.TWO": "中磊", "3062.TW": "建漢", "6285.TW": "啟碁", "3704.TW": "合勤控", 
    "2419.TW": "仲琦", "3596.TWO": "智易", "4906.TW": "正文",
    # 【機器人與自動化設備】
    "2359.TW": "所羅門", "2049.TW": "上銀", "2365.TW": "昆盈", "4562.TW": "穎漢", 
    "8374.TW": "羅昇", "6640.TW": "均華", "3680.TWO": "家登", "3019.TW": "亞光",
    # 【重電與綠能基建】
    "1513.TW": "中興電", "1519.TW": "華城", "1503.TW": "士電", "1504.TW": "東元", 
    "1514.TW": "亞力", "6806.TW": "森崴能源", "9958.TW": "世紀鋼", "1605.TW": "華新", 
    "1609.TW": "大亞",
    # 【面板與載板】
    "3481.TW": "群創", "2409.TW": "友達", "6116.TW": "彩晶", "8046.TWO": "南電", 
    "3037.TW": "欣興", "3189.TW": "景碩", "8069.TWO": "元太", "3105.TWO": "穩懋",
    # 【傳產、航運與金融避險】
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海", "1536.TW": "和大", 
    "9921.TW": "巨大", "9914.TW": "美利達", "2105.TW": "正新", "2106.TW": "建大",
    "6217.TWO": "中探針", "3003.TW": "健和興", "6409.TW": "旭隼", "2474.TW": "可成", 
    "6121.TWO": "新普", "2881.TW": "富邦金", "2882.TW": "國泰金", "2891.TW": "中信金", 
    "2886.TW": "兆豐金", "5871.TW": "中租-KY"
}

# ==========================================
# 2. 雙核心連線模組 (MongoDB + FinMind)
# ==========================================
@st.cache_resource
def init_mongo():
    try:
        client = pymongo.MongoClient(st.secrets["mongo"]["connection_string"])
        return client["crawler_db"]["scraped_articles"]
    except:
        return None

@st.cache_resource
def init_finmind():
    fm = DataLoader()
    try:
        # V108 授權金鑰寫入
        fm.login_by_token(api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA")
        return fm
    except:
        return fm

collection = init_mongo()
fm = init_finmind()

# ==========================================
# 3. 量價與籌碼運算引擎 (V108 核心)
# ==========================================
@st.cache_data(ttl=900)  # 快取 15 分鐘防當機
def run_matrix_scan(selected_tickers):
    results = []
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    for symbol in selected_tickers:
        try:
            # 1. 取得技術面 (yfinance)
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty or len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close_px = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            vol_today = float(df['Volume'].iloc[-1])
            vol_5ma = float(df['Volume'].rolling(5).mean().iloc[-1])
            
            # 2. MACD 動能
            macd = ta.macd(df['Close'])
            macd_hist = float(macd.iloc[-1, 1]) # MACD Histogram
            
            # 3. 取得籌碼面 (FinMind)
            stock_id = symbol.split('.')[0]
            inst_data = fm.taiwan_stock_institutional_investors_buy_sell(stock_id=stock_id)
            trust_buy = 0
            if inst_data is not None and not inst_data.empty:
                daily_net = inst_data.groupby('date')['buy_sell'].sum()
                trust_buy = daily_net.tail(3).sum() // 1000 # 近三日三大法人合計(千張)

            # 4. 戰神決策邏輯
            ma_status = "✅ 站上" if close_px > ma20 else "🔴 跌破"
            vol_status = "🔥 帶量突破" if vol_today > vol_5ma * 1.5 else ("💧 凹洞量" if vol_today < vol_5ma * 0.6 else "➖ 平穩")
            
            if close_px < ma20:
                action = "🛑 物理隔離 (市價停損)"
            elif close_px > ma20 and trust_buy > 0 and macd_hist > 0:
                action = "🎯 右側強攻 (帶量上漲)"
            elif close_px > ma20 and "凹洞量" in vol_status:
                action = "🟡 左側潛伏 (量縮回踩)"
            else:
                action = "⏳ 觀望 / 嚴控資金"

            results.append({
                "代碼": stock_id,
                "名稱": NAME_MAP[symbol],
                "現價": round(close_px, 2),
                "20MA": round(ma20, 2),
                "乖離率%": round(((close_px - ma20)/ma20)*100, 2),
                "技術線型": ma_status,
                "量能結構": vol_status,
                "法人動向(3日)": trust_buy,
                "操盤指令": action
            })
        except:
            continue
            
    return pd.DataFrame(results)

# ==========================================
# 4. 前端儀表板 UI (移動戰情室)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bullish.png")
    st.title("🛡️ 獅王戰神 V108")
    st.caption("全矩陣量化巡檢終端")
    
    st.divider()
    st.subheader("⚙️ 產線掃描控管")
    # 防呆機制：將 86 檔分區掃描，避免 Streamlit 記憶體溢出
    sector_options = {
        "1️⃣ 權值與 AI 伺服器": list(NAME_MAP.keys())[0:11],
        "2️⃣ 散熱與零組件": list(NAME_MAP.keys())[11:21],
        "3️⃣ IC 設計與矽智財": list(NAME_MAP.keys())[21:30],
        "4️⃣ CPO 矽光子與網通": list(NAME_MAP.keys())[38:53],
        "5️⃣ 傳產航運與避險": list(NAME_MAP.keys())[69:86]
    }
    
    selected_sector = st.selectbox("選擇打擊防區：", list(sector_options.keys()))
    scan_targets = sector_options[selected_sector]
    
    if st.button("🚀 啟動深度雷達掃描"):
        st.cache_data.clear()

st.title("🦁 獅王戰神 V108：量價籌碼大一統儀表板")

# 宏觀指標 Metrics
st.subheader("🌍 宏觀風控中樞")
try:
    vix_df = yf.Ticker("^VIX").history(period="2d")
    twii_df = yf.Ticker("^TWII").history(period="2d")
    vix_now, vix_prev = vix_df['Close'].iloc[-1], vix_df['Close'].iloc[-2]
    twii_now, twii_prev = twii_df['Close'].iloc[-1], twii_df['Close'].iloc[-2]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("加權指數 (^TWII)", f"{twii_now:.0f}", f"{twii_now - twii_prev:.0f}")
    col2.metric("恐慌指數 (^VIX)", f"{vix_now:.2f}", f"{vix_now - vix_prev:.2f}", delta_color="inverse")
    
    if vix_now > 25:
        col3.error("🚨 系統性風險爆發！強制拉高現金水位。")
    else:
        col3.success("✅ 宏觀情緒穩定，維持波段多單部位。")
except:
    st.warning("宏觀數據連線中...")

st.divider()

# 主戰略面板 Tabs
tab1, tab2, tab3 = st.tabs(["🎯 個股量價決策", "📰 實戰情報庫 (MongoDB)", "📘 操盤手鐵律"])

with tab1:
    st.markdown(f"**目前掃描防區：{selected_sector}**")
    with st.spinner('機台高頻運算中，請稍候...'):
        df_result = run_matrix_scan(scan_targets)
        
        if not df_result.empty:
            # 依據操盤指令上色
            def style_action(val):
                if "物理隔離" in str(val): return 'color: #ff4b4b; font-weight: bold;'
                if "右側強攻" in str(val): return 'color: #00eb93; font-weight: bold;'
                if "左側潛伏" in str(val): return 'color: #ffb74d; font-weight: bold;'
                return ''
                
            st.dataframe(df_result.style.map(style_action, subset=['操盤指令']), use_container_width=True)
        else:
            st.error("API 擷取逾時，請重新點擊左側掃描按鈕。")

with tab2:
    st.subheader("📡 即時市場多空情緒雷達")
    if collection is not None:
        data = list(collection.find().sort("crawled_at", -1).limit(30))
        if data:
            intel_df = pd.DataFrame(data)[['crawled_at', 'title', 'category', 'impact']]
            intel_df.columns = ['發布時間', '情報標題', '來源分類', '情緒判定']
            
            def style_impact(val):
                color = '#ff4b4b' if val == 'Positive' else '#00eb93' if val == 'Negative' else 'white'
                return f'color: {color}'
                
            st.dataframe(intel_df.style.map(style_impact, subset=['情緒判定']), use_container_width=True)
        else:
            st.info("資料庫暫無最新快訊。")
    else:
        st.warning("MongoDB 尚未連線，請確認 Secrets 設定。")

with tab3:
    st.markdown("""
    ### 👑 老司機四字訣：【輪、空、殺、早】
    * **【輪】**：資金是流水席。PCB動了搶記憶體，妖股亂舞即準備結帳散場。
    * **【空】**：避開套牢泥沼。帶量突破真空區，上高速公路再飆車。
    * **【殺】**：莊家最愛殺散戶。散戶斷頭殺低時尋找低基期錯殺股。
    * **【早】**：買在擴產認證時，賣在營收創高日。
    
    **絕對紀律：** 股價跌破 20MA 無條件全數變現。獲利達 20% 立刻分批減碼一半。
    """)
