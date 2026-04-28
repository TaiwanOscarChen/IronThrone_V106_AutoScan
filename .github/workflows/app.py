from flask import Flask, render_template, jsonify
import pymongo
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# 1. MongoDB 連線配置
MONGO_URI = "mongodb+srv://qianhao_chen:Aa0983770098@cluster0.gdnkemb.mongodb.net/?appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client["crawler_db"]
collection = db["lion_king_signals"]

# 2. 核心股票池 (示範部分標的，可自行補齊 80 檔)
NAME_MAP = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", 
    "3017.TW": "奇鋐", "3324.TW": "雙鴻", "2603.TW": "長榮"
}

@app.route('/api/update')
def update_signals():
    """執行量價結構掃描，推算 20MA 支撐與獲利滿足點，寫入資料庫"""
    signals = []
    for ticker, name in NAME_MAP.items():
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)
            if df.empty or len(df) < 20: continue
            if isinstance(df.columns, pd.MultiIndex): 
                df.columns = [c[0] for c in df.columns]
            
            close_px = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            vol_today = float(df['Volume'].iloc[-1])
            
            # 零股流動性與量能基礎判定
            liquidity = "充足" if vol_today > 1000000 else "枯竭 (避開零股交易)"
            
            # 絕對操盤紀律判定
            profit_ratio = (close_px - ma20) / ma20
            
            if close_px < ma20:
                status = "🔴 跌破月線"
                action = "物理隔離 (立即停損)"
            elif profit_ratio >= 0.2:
                status = "🔥 漲幅過大"
                action = "獲利 20% 強制減碼"
            else:
                status = "🟢 站穩 20MA"
                action = "沿月線續抱"

            signal_data = {
                "代碼": ticker.split('.')[0],
                "標的": name,
                "現價": round(close_px, 2),
                "MA20": round(ma20, 2),
                "流動性": liquidity,
                "技術態勢": status,
                "操盤指令": action,
                "更新時間": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            # 更新至 MongoDB
            collection.update_one({"代碼": ticker.split('.')[0]}, {"$set": signal_data}, upsert=True)
            signals.append(signal_data)
        except Exception as e:
            continue
            
    return jsonify({"status": "success", "message": "戰情庫更新完畢", "data": signals})

@app.route('/api/signals')
def get_signals():
    """供 HTML 前端讀取的 API 接口"""
    data = list(collection.find({}, {"_id": 0}).sort("代碼", 1))
    return jsonify(data)

@app.route('/')
def index():
    """渲染 HTML 戰情室"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
