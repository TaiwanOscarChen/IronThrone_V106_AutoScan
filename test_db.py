import sys
import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
import time
import random
import urllib3
import pandas as pd
import os

# ==========================================
# [系統防護層] 確保 HMI 終端穩定性
# ==========================================
# 強制輸出為 UTF-8，消除 cp950 停機異常
sys.stdout.reconfigure(encoding='utf-8')
# 忽略 SSL 憑證警告 (因應部分政府官網憑證過期之容錯處理)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. 資料庫連線配置 (IronThrone V106 核心架構)
# ==========================================
CONNECTION_STRING = "mongodb+srv://qianhao_chen:Aa0983770098@cluster0.gdnkemb.mongodb.net/?appName=Cluster0"

try:
    print("Connecting to MongoDB Atlas [IronThrone Engine V106.12]...")
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client["crawler_db"]
    collection = db["scraped_articles"]
    print("✅ 雲端資料庫已連線！自動化決策矩陣上線中...\n")
except Exception as e:
    print(f"❌ RCA 診斷：資料庫連線異常。Error: {e}")
    exit()

# ==========================================
# 2. 核心股票池 (NAME_MAP - 80檔戰略打擊名單)
# ==========================================
NAME_MAP = {
    "2330.TW":"台積電", "2454.TW":"聯發科", "2303.TW":"聯電", "3711.TW":"日月光投控",
    "2317.TW":"鴻海", "2308.TW":"台達電", "2382.TW":"廣達", "3231.TW":"緯創",
    "6669.TW":"緯穎", "2356.TW":"英業達", "2357.TW":"華碩", "2376.TW":"技嘉",
    "2324.TW":"仁寶", "2301.TW":"光寶科", "2395.TW":"研華", "3017.TW":"奇鋐",
    "3324.TW":"雙鴻", "2421.TW":"建準", "3665.TW":"貿聯-KY", "2059.TW":"川湖",
    "3533.TW":"嘉澤", "3034.TW":"聯詠", "2379.TW":"瑞昱", "3035.TW":"智原",
    "4966.TW":"譜瑞-KY", "3443.TW":"創意", "3661.TW":"世芯-KY", "3529.TWO":"力旺",
    "8016.TWO":"矽創", "6138.TW":"茂達", "5347.TWO":"世界先進", "6770.TW":"力積電",
    "3363.TW":"上詮", "3450.TW":"聯鈞", "4979.TW":"華星光", "3163.TWO":"波若威",
    "4908.TW":"前鼎", "6442.TW":"光聖", "3081.TW":"聯亞", "2345.TW":"智邦",
    "5388.TWO":"中磊", "3062.TW":"建漢", "6285.TW":"啟碁", "3704.TW":"合勤控",
    "2419.TW":"仲琦", "3596.TWO":"智易", "4906.TW":"正文", "2359.TW":"所羅門",
    "2049.TW":"上銀", "2365.TW":"昆盈", "4562.TW":"穎漢", "8374.TW":"羅昇",
    "6640.TW":"均華", "3680.TWO":"家登", "3019.TW":"亞光", "1513.TW":"中興電",
    "1519.TW":"華城", "1503.TW":"士電", "1504.TW":"東元", "1514.TW":"亞力",
    "6806.TW":"森崴能源", "9958.TW":"世紀鋼", "1605.TW":"華新", "1609.TW":"大亞",
    "1536.TW":"和大", "6217.TWO":"中探針", "3003.TW":"健和興", "9921.TW":"巨大",
    "9914.TW":"美利達", "2105.TW":"正新", "2106.TW":"建大", "2603.TW":"長榮",
    "2609.TW":"陽明", "2615.TW":"萬海", "2408.TW":"南亞科", "2344.TW":"華邦電",
    "3481.TW":"群創", "2409.TW":"友達", "3260.TWO":"威剛", "8299.TWO":"群聯",
    "6116.TW":"彩晶", "8046.TWO":"南電", "3037.TW":"欣興", "3189.TW":"景碩",
    "8069.TWO":"元太", "2337.TW":"旺宏", "3105.TWO":"穩懋", "6409.TW":"旭隼",
    "2474.TW":"可成", "6121.TWO":"新普", "2327.TW":"國巨", "2492.TW":"華新科",
    "2881.TW":"富邦金"
}

# ==========================================
# 3. 爬蟲主模組 (具備自動標籤功能)
# ==========================================
def scrape_and_save(target_url, category="Standard"):
    """
    功能：自動抓取網頁標題與內容，判斷情緒，存入 MongoDB。
    """
    print(f"🚀 掃描目標 [{category}]: {target_url}")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    headers = {"User-Agent": random.choice(user_agents)}

    try:
        response = requests.get(target_url, headers=headers, timeout=15, verify=False)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("h1") or soup.find("title")
            title = title_tag.text.strip() if title_tag else ""
            
            # --- [數據清洗防呆]：長度小於3則不予呈現 ---
            if not title or len(title) <= 3:
                print("⚠️ RCA 診斷：抓取到無效標題或短代碼，略過入庫。")
                return

            paragraphs = soup.find_all("p")
            content = "\n".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 10])

            # --- [情緒引擎核心 V1.0] ---
            impact = "Neutral"
            if any(k in content for k in ["漲價", "擴產", "創新高", "認證通過", "買超", "噴出"]):
                impact = "Positive"
            elif any(k in content for k in ["關稅", "制裁", "砍單", "跌破", "賣超", "崩跌"]):
                impact = "Negative"

            article_data = {
                "source_url": target_url,
                "category": category,
                "title": title,
                "content": content,
                "impact": impact,  # 👈 寫入自動判斷的情緒標籤
                "crawled_at": datetime.now()
            }
            
            collection.update_one({"source_url": target_url}, {"$set": article_data}, upsert=True)
            print(f"✅ [{impact}] 資料入庫成功: {title[:20]}...\n")
        else:
            print(f"⚠️ 請求失敗，代碼: {response.status_code}\n")
    except Exception as e:
        print(f"❌ 錯誤: {e}\n")

# ==========================================
# 4. 決策分析模組
# ==========================================
def analyze_today_signals():
    """
    功能：從 MongoDB 讀取數據，比對股票池，輸出即時偵測報告。
    """
    print("獅王戰神決策系統：正在執行全維度數據比對...")
    
    # 取得今日數據
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    latest_intel = collection.find({"crawled_at": {"$gte": today}}).sort("crawled_at", -1).limit(100)

    signals_found = []
    
    for intel in latest_intel:
        title = intel.get("title", "")
        content = intel.get("content", "")
        impact_tag = intel.get("impact", "Neutral")
        
        for code, name in NAME_MAP.items():
            if name in title or name in content:
                # 轉換為更直觀的顯示文字
                status = "Positive (利多)" if impact_tag == "Positive" else "Negative (避雷)" if impact_tag == "Negative" else "Neutral"
                
                signals_found.append({
                    "代碼": code,
                    "標的": name,
                    "情緒": status,
                    "時效": intel.get("crawled_at").strftime('%H:%M')
                })

    if signals_found:
        df_signals = pd.DataFrame(signals_found).drop_duplicates(subset=['標的'])
        print("\n--- 📢 今日核心標的情緒偵測報告 ---")
        print(df_signals.to_string(index=False))
        print("\n[操盤指令]: 正向標的請檢核 20MA 支撐位；避雷標的一旦破線請物理隔離。")
    else:
        print("\n今日尚未偵測到核心標的之明確情緒訊號。")

# ==========================================
# 5. 全方位執行矩陣
# ==========================================
if __name__ == "__main__":
    
    news_urls = [
        "https://news.cnyes.com/news/cat/headline",
        "https://tw.stock.yahoo.com/news/",
        "https://wallstreetcn.com/news/global",
        "https://xnews.jin10.com/",
        "https://money.udn.com/money/index",
        "https://www.todayusstock.com/",
        "https://www.investor.com.tw/onlineNews/index.asp",
        "https://www.sinotrade.com.tw/Stock/Stock_3_6?ch=Stock_3_6_1",
        "https://www.spf.com.tw/sinopacSPF/research/list.do?id=15c34119ad300000481676416f806709",
        "https://www.stat.gov.tw/News.aspx?n=2668&sms=10980"
    ]

    all_active = [(u, "Matrix_Scan") for u in news_urls]
    
    print(f"IronThrone V106.12: 開始執行 {len(all_active)} 條戰略資訊流掃描...\n")

    for url, cat in all_active:
        scrape_and_save(url, cat)
        time.sleep(random.uniform(3, 7))

    # 執行最終分析
    analyze_today_signals()

    print("\n[V106.12 系統報告]: 數據與決策矩陣同步完畢。")
