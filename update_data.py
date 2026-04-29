import yfinance as yf
import pandas as pd
import os
from supabase import create_client

# 1. 取得 GitHub Secrets 中的最高權限金鑰
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
sb = create_client(url, key)

# 2. 獅王戰神 V108 核心戰略股池 (整合 CPO、水冷、AI、重電)
NAME_MAP = {
    "2330.TW": ("台積電", "先進製程/CoWoS"),
    "2317.TW": ("鴻海", "AI伺服器組裝"),
    "2382.TW": ("廣達", "AI伺服器組裝"),
    "3231.TW": ("緯創", "AI伺服器組裝"),
    "3017.TW": ("奇鋐", "水冷散熱模組"),
    "3324.TW": ("雙鴻", "水冷散熱模組"),
    "6805.TW": ("富世達", "水冷快接頭"),
    "2308.TW": ("台達電", "高壓電源供應"),
    "2301.TW": ("光寶科", "高壓電源供應"),
    "3363.TW": ("上詮", "矽光子 CPO"),
    "4979.TW": ("華星光", "矽光子 CPO"),
    "3163.TWO": ("波若威", "光通訊元件"),
    "1519.TW": ("華城", "重電/基礎建設"),
    "2454.TW": ("聯發科", "ASIC/邊緣AI"),
    "3661.TW": ("世芯-KY", "ASIC 矽智財"),
    "3443.TW": ("創意", "ASIC 矽智財"),
    "2603.TW": ("長榮", "航運避險"),
    "0050.TW": ("元大台灣50", "市值型大盤"),
    "00919.TW": ("群益台灣精選高息", "高股息ETF")
}

print(f"🚀 啟動 V108 全矩陣量化巡檢，共 {len(NAME_MAP)} 檔標的...")

for ticker, info in NAME_MAP.items():
    name, sector = info
    try:
        # 獲取近 3 個月日K線
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 26: continue
        
        # 處理 yfinance 雙層索引問題
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = [c[0] for c in df.columns]
        
        close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        
        # 運算 MACD 柱狀體 (動能指標)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = float((macd_line - signal_line).iloc[-1])
        
        # 獅王戰神絕對紀律裁決
        if close < ma20:
            cmd = "🛑 物理隔離 (破月線停損)"
        elif close >= (ma20 * 1.2):
            cmd = "💰 獲利達20% (強制減碼)"
        elif close >= ma20 and macd_hist > 0:
            cmd = "🔥 右側強攻 (動能向上)"
        else:
            cmd = "⏳ 震盪整理 (站穩守穩)"
            
        # 寫入 Supabase 資料庫
        sb.table('lion_king_signals').upsert({
            "id": ticker.split('.')[0],
            "name": name,
            "sector": sector,
            "price": round(close, 2),
            "ma20": round(ma20, 2),
            "macd_hist": round(macd_hist, 2),
            "instruction": cmd
        }).execute()
        print(f"✅ {name} 運算寫入成功")
    except Exception as e:
        print(f"❌ {name} 異常跳過: {e}")

print("🏁 產線巡檢完畢！")
