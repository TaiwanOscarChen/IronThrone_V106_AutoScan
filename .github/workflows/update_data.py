import yfinance as yf
import os
import pandas as pd
from supabase import create_client

# 從 GitHub Secrets 讀取環境變數 (保護隱私)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
sb = create_client(url, key)

# 核心宇宙庫 86 檔
NAME_MAP = {
    "2330.TW":"台積電", "2317.TW":"鴻海", "2454.TW":"聯發科", "2382.TW":"廣達", "3231.TW":"緯創",
    "3017.TW":"奇鋐", "3324.TW":"雙鴻", "2308.TW":"台達電", "2603.TW":"長榮", "1519.TW":"華城",
    "2359.TW":"所羅門", "3661.TW":"世芯-KY", "3443.TW":"創意", "3034.TW":"聯詠", "2379.TW":"瑞昱",
    "6669.TW":"緯穎", "2356.TW":"英業達", "2376.TW":"技嘉", "2324.TW":"仁寶", "2301.TW":"光寶科"
    # ... 您可以依此格式補完 86 檔
}

print(f"🚀 開始執行獅王戰神 V108 巡檢，共 {len(NAME_MAP)} 檔標的...")

for ticker, name in NAME_MAP.items():
    try:
        df = yf.download(ticker, period="3mo", progress=False)
        if df.empty: continue
        
        # 統一處理 yfinance 的索引
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
        
        close = round(float(df['Close'].iloc[-1]), 2)
        ma20 = round(float(df['Close'].rolling(20).mean().iloc[-1]), 2)
        
        # 絕對紀律判定邏輯
        if close < ma20:
            cmd = "🛑 物理隔離 (立即停損)"
        elif close >= (ma20 * 1.2):
            cmd = "💰 獲利 20% (強制減碼)"
        else:
            cmd = "🎯 右側續抱 (站穩 20MA)"
        
        # 寫入 Supabase
        sb.table('lion_king_signals').upsert({
            "id": ticker.split('.')[0],
            "name": name,
            "price": close,
            "ma20": ma20,
            "instruction": cmd
        }).execute()
        print(f"✅ {name} ({ticker}) 更新成功")
    except Exception as e:
        print(f"❌ {name} 更新失敗: {e}")

print("🏁 產線巡檢完畢！")
