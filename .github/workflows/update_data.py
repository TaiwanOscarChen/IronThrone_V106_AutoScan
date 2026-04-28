import yfinance as yf
from supabase import create_client
import os

# 連線 Supabase
url = "YOUR_SUPABASE_URL"
key = "YOUR_SERVICE_ROLE_KEY" # 注意：這裡用 Service Role Key 才有權限寫入
sb = create_client(url, key)

NAME_MAP = {"2330.TW":"台積電", "2317.TW":"鴻海", "2454.TW":"聯發科", "3017.TW":"奇鋐"}

for ticker, name in NAME_MAP.items():
    df = yf.download(ticker, period="3mo", progress=False)
    close = round(float(df['Close'].iloc[-1]), 2)
    ma20 = round(float(df['Close'].rolling(20).mean().iloc[-1]), 2)
    
    cmd = "🛑 物理隔離" if close < ma20 else "🎯 右側續抱"
    
    sb.table('lion_king_signals').upsert({
        "id": ticker.split('.')[0], "name": name, "price": close, "ma20": ma20, "instruction": cmd
    }).execute()

print("✅ 數據更新完畢")
