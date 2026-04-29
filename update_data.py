import os
import time

import pandas as pd
import yfinance as yf
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in GitHub Secrets")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# LionKing V110 core stock universe. Keep secrets out of this public repo.
NAME_MAP = {
    "2330.TW": ("台積電", "核心半導體"),
    "2454.TW": ("聯發科", "核心半導體"),
    "2303.TW": ("聯電", "核心半導體"),
    "3711.TW": ("日月光投控", "核心半導體"),
    "2317.TW": ("鴻海", "核心權值與AI伺服器"),
    "2382.TW": ("廣達", "核心權值與AI伺服器"),
    "3231.TW": ("緯創", "核心權值與AI伺服器"),
    "6669.TW": ("緯穎", "核心權值與AI伺服器"),
    "2356.TW": ("英業達", "核心權值與AI伺服器"),
    "2357.TW": ("華碩", "核心權值與AI伺服器"),
    "2376.TW": ("技嘉", "核心權值與AI伺服器"),
    "2324.TW": ("仁寶", "核心權值與AI伺服器"),
    "2395.TW": ("研華", "核心權值與AI伺服器"),
    "2308.TW": ("台達電", "散熱電源與被動元件"),
    "2301.TW": ("光寶科", "散熱電源與被動元件"),
    "3017.TW": ("奇鋐", "散熱電源與被動元件"),
    "3324.TW": ("雙鴻", "散熱電源與被動元件"),
    "2421.TW": ("建準", "散熱電源與被動元件"),
    "2327.TW": ("國巨", "散熱電源與被動元件"),
    "2492.TW": ("華新科", "散熱電源與被動元件"),
    "3533.TW": ("嘉澤", "散熱電源與被動元件"),
    "3665.TW": ("貿聯-KY", "散熱電源與被動元件"),
    "2059.TW": ("川湖", "散熱電源與被動元件"),
    "3443.TW": ("創意", "半導體IP與矽光子CPO"),
    "3661.TW": ("世芯-KY", "半導體IP與矽光子CPO"),
    "3529.TWO": ("力旺", "半導體IP與矽光子CPO"),
    "3034.TW": ("聯詠", "半導體IP與矽光子CPO"),
    "2379.TW": ("瑞昱", "半導體IP與矽光子CPO"),
    "3035.TW": ("智原", "半導體IP與矽光子CPO"),
    "4966.TW": ("譜瑞-KY", "半導體IP與矽光子CPO"),
    "8016.TWO": ("矽創", "半導體IP與矽光子CPO"),
    "6138.TW": ("茂達", "半導體IP與矽光子CPO"),
    "5347.TWO": ("世界先進", "半導體IP與矽光子CPO"),
    "6770.TW": ("力積電", "半導體IP與矽光子CPO"),
    "3363.TW": ("上詮", "半導體IP與矽光子CPO"),
    "3450.TW": ("聯鈞", "半導體IP與矽光子CPO"),
    "4979.TW": ("華星光", "半導體IP與矽光子CPO"),
    "3163.TWO": ("波若威", "半導體IP與矽光子CPO"),
    "4908.TW": ("前鼎", "半導體IP與矽光子CPO"),
    "6442.TW": ("光聖", "半導體IP與矽光子CPO"),
    "3081.TW": ("聯亞", "半導體IP與矽光子CPO"),
    "1513.TW": ("中興電", "重電綠能與傳產"),
    "1519.TW": ("華城", "重電綠能與傳產"),
    "1503.TW": ("士電", "重電綠能與傳產"),
    "1504.TW": ("東元", "重電綠能與傳產"),
    "1514.TW": ("亞力", "重電綠能與傳產"),
    "6806.TW": ("森崴能源", "重電綠能與傳產"),
    "9958.TW": ("世紀鋼", "重電綠能與傳產"),
    "1605.TW": ("華新", "重電綠能與傳產"),
    "1609.TW": ("大亞", "重電綠能與傳產"),
    "1536.TW": ("和大", "重電綠能與傳產"),
    "3003.TW": ("健和興", "重電綠能與傳產"),
    "9921.TW": ("巨大", "重電綠能與傳產"),
    "9914.TW": ("美利達", "重電綠能與傳產"),
    "2105.TW": ("正新", "重電綠能與傳產"),
    "2106.TW": ("建大", "重電綠能與傳產"),
    "2408.TW": ("南亞科", "記憶體面板與成熟製程"),
    "2344.TW": ("華邦電", "記憶體面板與成熟製程"),
    "3481.TW": ("群創", "記憶體面板與成熟製程"),
    "2409.TW": ("友達", "記憶體面板與成熟製程"),
    "3260.TWO": ("威剛", "記憶體面板與成熟製程"),
    "8299.TWO": ("群聯", "記憶體面板與成熟製程"),
    "6116.TW": ("彩晶", "記憶體面板與成熟製程"),
    "8046.TWO": ("南電", "記憶體面板與成熟製程"),
    "3037.TW": ("欣興", "記憶體面板與成熟製程"),
    "3189.TW": ("景碩", "記憶體面板與成熟製程"),
    "8069.TWO": ("元太", "記憶體面板與成熟製程"),
    "2337.TW": ("旺宏", "記憶體面板與成熟製程"),
    "3105.TWO": ("穩懋", "記憶體面板與成熟製程"),
    "6409.TW": ("旭隼", "記憶體面板與成熟製程"),
    "2474.TW": ("可成", "記憶體面板與成熟製程"),
    "6121.TWO": ("新普", "記憶體面板與成熟製程"),
    "2603.TW": ("長榮", "航運"),
    "2609.TW": ("陽明", "航運"),
    "2615.TW": ("萬海", "航運"),
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [col[0] for col in df.columns]
    return df


def compute_signal(ticker: str, name: str, sector: str) -> dict | None:
    df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
    df = normalize_columns(df)
    if df.empty or len(df) < 60:
        return None

    close_series = df["Close"].dropna()
    volume_series = df["Volume"].dropna() if "Volume" in df else pd.Series(dtype=float)
    close = float(close_series.iloc[-1])
    ma20 = float(close_series.rolling(20).mean().iloc[-1])

    ema12 = close_series.ewm(span=12, adjust=False).mean()
    ema26 = close_series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = float((macd_line - signal_line).iloc[-1])

    delta = close_series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if not rs.empty else None
    volume = float(volume_series.iloc[-1]) if not volume_series.empty else None

    if close < ma20:
        instruction = "🛑 物理隔離 (破20MA停損)"
    elif close >= ma20 * 1.2:
        instruction = "💰 獲利達20% (強制減碼)"
    elif macd_hist > 0:
        instruction = "🔥 右側強攻 (動能向上)"
    else:
        instruction = "⏳ 站穩觀察 (等待放量)"

    return {
        "id": ticker.split(".")[0],
        "name": name,
        "sector": sector,
        "price": round(close, 2),
        "ma20": round(ma20, 2),
        "macd_hist": round(macd_hist, 4),
        "rsi": round(rsi, 2) if rsi is not None and pd.notna(rsi) else None,
        "volume": round(volume, 0) if volume is not None else None,
        "instruction": instruction,
        "source_module": "update_data.py",
    }


print(f"🚀 啟動 LionKing V110 Supabase 同步，共 {len(NAME_MAP)} 檔標的")

for ticker, (name, sector) in NAME_MAP.items():
    try:
        payload = compute_signal(ticker, name, sector)
        if not payload:
            print(f"⚠️ {name} ({ticker}) 資料不足，略過")
            continue
        sb.table("lion_king_signals").upsert(payload).execute()
        print(f"✅ {name} ({ticker}) 寫入成功")
        time.sleep(0.2)
    except Exception as exc:
        print(f"❌ {name} ({ticker}) 寫入失敗: {exc}")

print("🏁 LionKing V110 Supabase 同步完成")
