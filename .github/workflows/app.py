import streamlit as st
import pandas as pd
import yfinance as yf
from FinMind.data import DataLoader
from supabase import create_client, Client
from datetime import datetime, timedelta

# ==========================================
# 0. HMI 戰情室介面優化
# ==========================================
st.set_page_config(page_title="獅王戰神 V108 終極終端", layout="wide")

# Supabase 配置 (請在 Secrets 填入)
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.sidebar.error("⚠️ Supabase 金鑰未掛載")

# ==========================================
# 1. 核心 86 檔標的名單 (戰略打擊群)
# ==========================================
NAME_MAP = {
    "2330.TW":"台積電", "2317.TW":"鴻海", "2454.TW":"聯發科", "2382.TW":"廣達", "3231.TW":"緯創", "6669.TW":"緯穎", "2356.TW":"英業達", "2376.TW":"技嘉", "2324.TW":"仁寶", "2301.TW":"光寶科", "2395.TW":"研華", "3017.TW":"奇鋐", "3324.TW":"雙鴻", "2421.TW":"建準", "3665.TW":"貿聯-KY", "2059.TW":"川湖", "3533.TW":"嘉澤", "2308.TW":"台達電", "2379.TW":"瑞昱", "3035.TW":"智原", "4966.TW":"譜瑞-KY", "3443.TW":"創意", "3661.TW":"世芯-KY", "3529.TWO":"力旺", "8016.TWO":"矽創", "6138.TW":"茂達", "5347.TWO":"世界先進", "6770.TW":"力積電", "3363.TW":"上詮", "3450.TW":"聯鈞", "4979.TW":"華星光", "3163.TWO":"波若威", "4908.TW":"前鼎", "6442.TW":"光聖", "3081.TW":"聯亞", "2345.TW":"智邦", "5388.TWO":"中磊", "3062.TW":"建漢", "6285.TW":"啟碁", "3704.TW":"合勤控", "2419.TW":"仲琦", "3596.TWO":"智易", "4906.TW":"正文", "2359.TW":"所羅門", "2049.TW":"上銀", "2365.TW":"昆盈", "4562.TW":"穎漢", "8374.TW":"羅昇", "6640.TW":"均華", "3680.TWO":"家登", "3019.TW":"亞光", "1513.TW":"中興電", "1519.TW":"華城", "1503.TW":"士電", "1504.TW":"東元", "1514.TW":"亞力", "6806.TW":"森崴能源", "9958.TW":"世紀鋼", "1605.TW":"華新", "1609.TW":"大亞", "1536.TW":"和大", "6217.TWO":"中探針", "3003.TW":"健和興", "9921.TW":"巨大", "9914.TW":"美利達", "2105.TW":"正新", "2106.TW":"建大", "2603.TW":"長榮", "2609.TW":"陽明", "2615.TW":"萬海", "2408.TW":"南亞科", "2344.TW":"華邦電", "3481.TW":"群創", "2409.TW":"友達", "3260.TWO":"威剛", "8299.TWO":"群聯", "6116.TW":"彩晶", "8046.TWO":"南電", "3037.TW":"欣興", "3189.TW":"景碩", "8069.TWO":"元太", "2337.TW":"旺宏", "3105.TWO":"穩懋", "6409.TW":"旭隼", "2474.TW":"可成", "6121.TWO":"新普", "2327.TW":"國巨", "2492.TW":"華新科", "2881.TW":"富邦金"
}

# ==========================================
# 2. 數據運算引擎 (量價+籌碼)
# ==========================================
@st.cache_data(ttl=600)
def run_strategy(tickers):
    results = []
    fm = DataLoader()
    fm.login_by_token(api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMy0zMSAyMjo0NzozMCIsInVzZXJfaWQiOiJjaGVucWlhbmhhbyIsImlwIjoiMjExLjczLjE3My4xNDUiLCJleHAiOjE3NzU1NzMyNTB9.kCR8cu4M8RpBT6iPFwoywy7G0kkifW2LDu5qS0JO-qA")
    
    for symbol in tickers:
        try:
            # 技術面 (yfinance)
            df = yf.download(symbol, period="3mo", progress=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
            
            close = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            
            # 籌碼面 (FinMind)
            stock_id = symbol.split('.')[0]
            chip = fm.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=(datetime.now()-timedelta(days=7)).strftime("%Y-%m-%d"))
            net_buy = chip['buy_sell'].tail(3).sum() // 1000 if not chip.empty else 0

            # 決策判斷
            if close < ma20:
                cmd, color = "🛑 物理隔離", "#ff4b4b"
            elif close >= ma20 and net_buy > 0:
                cmd, color = "🎯 右側強攻", "#00eb93"
            else:
                cmd, color = "⏳ 觀望等待", "#8b949e"

            results.append({
                "代碼": stock_id, "標的": NAME_MAP[symbol], "收盤": round(close, 2),
                "20MA": round(ma20, 2), "法人買超(張)": net_buy, "最終指令": cmd, "_color": color
            })
        except: continue
    return pd.DataFrame(results)

# ==========================================
# 3. 網頁版面設計
# ==========================================
st.title("🦁 獅王戰神 V108 終極決策終端")
st.sidebar.title("🛡️ 戰略區域控制")
sector = st.sidebar.selectbox("選擇防區：", ["AI伺服器", "散熱/網通", "電子/權值", "傳產/金融"])

# 分流處理以維持運算效能
all_stocks = list(NAME_MAP.keys())
targets = all_stocks[:20] # 依 sector 切換

with st.spinner('機台高頻運算中...'):
    df_res = run_strategy(targets)
    
    if not df_res.empty:
        # KPI 顯示區
        c1, c2, c3 = st.columns(3)
        c1.metric("今日監控標的", f"{len(df_res)} 檔")
        c2.metric("強攻標的", len(df_res[df_res['最終指令']=='🎯 右側強攻']))
        c3.metric("停損標的", len(df_res[df_res['最終指令']=='🛑 物理隔離']))
        
        # 核心數據表
        def style_cmd(row):
            return [f'color: {row["_color"]}; font-weight: bold;' if col == '最終指令' else '' for col in row.index]
        
        st.dataframe(df_res.drop(columns=['_color']).style.apply(style_cmd, axis=1), use_container_width=True)
    else:
        st.error("API 擷取延遲，請稍後再試。")

st.divider()
st.info("💡 **操盤紀律：** 跌破 20MA 無條件變現，獲利 20% 強制減碼一半。")
