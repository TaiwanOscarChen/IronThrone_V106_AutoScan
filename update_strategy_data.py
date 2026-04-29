import ast
import os
import time
from pathlib import Path

import pandas as pd
import yfinance as yf
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in GitHub Secrets")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

BASE_SIGNAL_FIELDS = {
    "id",
    "name",
    "sector",
    "price",
    "ma20",
    "macd_hist",
    "rsi",
    "volume",
    "instruction",
    "source_module",
}

STRATEGY_RULES = [
    {
        "rule_key": "ma20_life_line",
        "title": "20MA 生命線",
        "category": "技術面",
        "condition_text": "收盤價站上 20MA 才允許偏多；跌破 20MA 視為轉弱警訊。",
        "action_text": "站穩 20MA 可觀察回檔買點；跌破先降部位或空手等待。",
        "weight": 18,
        "source_title": "核心股票技術策略與校正 / 智能選股",
    },
    {
        "rule_key": "macd_momentum",
        "title": "MACD 動能柱",
        "category": "技術面",
        "condition_text": "MACD histogram 由負轉正或持續擴大，代表短線動能轉強。",
        "action_text": "動能轉強且價格在月線上方可列入候選；動能縮小時避免追價。",
        "weight": 14,
        "source_title": "MACD成交量策略標準研擬 / 自動化戰情模組",
    },
    {
        "rule_key": "volume_ratio",
        "title": "估量比與量能放大",
        "category": "量價",
        "condition_text": "成交量高於 20 日均量且價格同步站穩均線，訊號可信度提高。",
        "action_text": "量增價漲偏多；量增但跌破支撐視為出貨或分歧風險。",
        "weight": 12,
        "source_title": "台股估量比策略分析 / 風暴比策略",
    },
    {
        "rule_key": "rsi_heat",
        "title": "RSI 過熱與過冷",
        "category": "技術面",
        "condition_text": "RSI 高於 78 視為短線過熱，低於 35 視為超跌反彈觀察。",
        "action_text": "過熱不追高；超跌必須等價格重新站回關鍵均線。",
        "weight": 10,
        "source_title": "智能判讀指數 / 趨勢交易策略深度研究",
    },
    {
        "rule_key": "k_three_three",
        "title": "K 線三三原則",
        "category": "K線型態",
        "condition_text": "連續三根 K 線守住支撐且高低點墊高，才視為較完整的轉強結構。",
        "action_text": "未形成三三結構前只觀察；跌破前低則訊號失效。",
        "weight": 9,
        "source_title": "K線三三原則與進場策略",
    },
    {
        "rule_key": "chip_follow",
        "title": "籌碼主力順風",
        "category": "籌碼面",
        "condition_text": "法人或主力買超與股價同步上升，代表籌碼偏順風。",
        "action_text": "價漲但籌碼分歧時降低追高權重；連續賣超應守停損。",
        "weight": 13,
        "source_title": "籌碼面分析進出場訊號 / 資金流向策略法則",
    },
    {
        "rule_key": "risk_stop",
        "title": "停損停利與部位控管",
        "category": "風控",
        "condition_text": "跌破 20MA 或跌破停損線先處理風險；漲幅過大分批停利。",
        "action_text": "不攤平破線標的；單一股票避免重壓，分批進出。",
        "weight": 15,
        "source_title": "策略模擬器 / 投資訊號與警示深度分析",
    },
    {
        "rule_key": "macro_estop",
        "title": "黑天鵝與宏觀 E-Stop",
        "category": "宏觀風控",
        "condition_text": "大盤、台積電、槓桿 ETF 同步轉弱時，系統應切換防守模式。",
        "action_text": "降低持股、保留現金、避免逆勢追高；等市場重新轉強再恢復攻擊。",
        "weight": 16,
        "source_title": "黑天鵝與宏觀對沖機制 / 中東局勢影響台股訊號判斷",
    },
]


def load_name_map() -> dict[str, tuple[str, str]]:
    source = Path(__file__).with_name("update_data.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "NAME_MAP":
                    return ast.literal_eval(node.value)
    raise RuntimeError("NAME_MAP not found in update_data.py")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [col[0] for col in df.columns]
    return df


def safe_latest(series: pd.Series, fallback: float | None = None) -> float | None:
    clean = series.dropna()
    if clean.empty:
        return fallback
    value = float(clean.iloc[-1])
    return value if pd.notna(value) else fallback


def pct_range(center: float, lower: float, upper: float, digits: int = 2) -> str:
    return f"{round(center * lower, digits)} ~ {round(center * upper, digits)}"


def build_strategy(close: float, ma5: float, ma20: float, ma60: float, macd_hist: float, rsi: float | None, volume_ratio: float | None) -> dict:
    score = 50
    tags: list[str] = []

    if close >= ma20:
        score += 15
        tags.append("站上20MA")
    else:
        score -= 22
        tags.append("跌破20MA")

    if close >= ma5:
        score += 6
        tags.append("短線強於MA5")
    else:
        score -= 5
        tags.append("短線低於MA5")

    if close >= ma60:
        score += 8
        tags.append("中期多方")
    else:
        score -= 8
        tags.append("中期偏弱")

    macd_weight = min(14, 5 + abs(macd_hist) / max(close, 1) * 220)
    if macd_hist > 0:
        score += macd_weight
        tags.append("MACD動能向上")
    else:
        score -= macd_weight
        tags.append("MACD動能轉弱")

    if rsi is not None:
        if rsi >= 78:
            score -= 10
            tags.append("RSI過熱")
        elif rsi <= 35:
            score -= 4
            tags.append("RSI超跌待確認")
        elif 45 <= rsi <= 68:
            score += 7
            tags.append("RSI健康區")

    if volume_ratio is not None:
        if volume_ratio >= 1.35 and close >= ma20:
            score += 8
            tags.append("量增價穩")
        elif volume_ratio >= 1.35 and close < ma20:
            score -= 10
            tags.append("量增破線風險")
        elif volume_ratio < 0.75:
            score -= 3
            tags.append("量能不足")

    score = int(max(0, min(100, round(score))))
    stop_loss = min(ma20 * 0.985, close * 0.93)
    take_profit = close * 1.12 if score >= 70 else max(ma20 * 1.08, close * 1.06)

    if close < ma20:
        signal_level = "防守"
        risk_level = "高"
        instruction = "🛑 破20MA防守 (先降部位)"
        position_plan = "破月線先控制風險；等重新站回 20MA 且量能回溫再評估。"
    elif score >= 78 and rsi is not None and rsi >= 78:
        signal_level = "偏強過熱"
        risk_level = "中高"
        instruction = "💰 偏強過熱 (分批停利)"
        position_plan = "已持有者分批停利；新倉等待回測支撐，不急追高。"
    elif score >= 72:
        signal_level = "攻擊"
        risk_level = "中"
        instruction = "🔥 右側強攻 (回檔找買點)"
        position_plan = "回測支撐不破可分批；跌破停損線立即降風險。"
    elif score >= 55:
        signal_level = "觀察"
        risk_level = "中"
        instruction = "⏳ 站穩觀察 (等量能確認)"
        position_plan = "小部位觀察或等待 MACD/量能同步轉強。"
    else:
        signal_level = "保守"
        risk_level = "中高"
        instruction = "⚠️ 動能不足 (等待轉強)"
        position_plan = "暫不追價；等待三三結構或站回均線後再評估。"

    if volume_ratio is not None:
        analysis_note = (
            f"分數 {score}/100；價格相對20MA偏離 {((close / ma20 - 1) * 100):.2f}%；"
            f"MACD柱狀體 {macd_hist:.2f}；量比 {volume_ratio:.2f}。"
        )
    else:
        analysis_note = f"分數 {score}/100；量能資料不足；MACD柱狀體 {macd_hist:.2f}。"

    return {
        "strategy_score": score,
        "signal_level": signal_level,
        "risk_level": risk_level,
        "position_plan": position_plan,
        "entry_zone": pct_range(max(ma20, close * 0.96), 0.995, 1.015),
        "support_zone": pct_range(max(ma20, close * 0.94), 0.985, 1.02),
        "pressure_zone": pct_range(close * 1.035, 0.99, 1.03),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "strategy_tags": tags[:8],
        "analysis_note": analysis_note,
        "instruction": instruction,
    }


def seed_strategy_rules() -> None:
    for rule in STRATEGY_RULES:
        sb.table("lion_king_strategy_rules").upsert(rule).execute()
    print(f"📘 已同步 {len(STRATEGY_RULES)} 條策略規則")


def compute_signal(ticker: str, name: str, sector: str) -> dict | None:
    df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
    df = normalize_columns(df)
    if df.empty or len(df) < 60:
        return None

    close_series = df["Close"].dropna()
    volume_series = df["Volume"].dropna() if "Volume" in df else pd.Series(dtype=float)
    close = float(close_series.iloc[-1])
    ma5 = safe_latest(close_series.rolling(5).mean(), close) or close
    ma20 = safe_latest(close_series.rolling(20).mean(), close) or close
    ma60 = safe_latest(close_series.rolling(60).mean(), ma20) or ma20

    ema12 = close_series.ewm(span=12, adjust=False).mean()
    ema26 = close_series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = float((macd_line - signal_line).iloc[-1])

    delta = close_series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = safe_latest(100 - (100 / (1 + rs))) if not rs.empty else None
    volume = safe_latest(volume_series) if not volume_series.empty else None
    volume_ma20 = safe_latest(volume_series.rolling(20).mean()) if not volume_series.empty else None
    volume_ratio = (volume / volume_ma20) if volume and volume_ma20 else None

    strategy = build_strategy(close, ma5, ma20, ma60, macd_hist, rsi, volume_ratio)
    return {
        "id": ticker.split(".")[0],
        "name": name,
        "sector": sector,
        "price": round(close, 2),
        "ma20": round(ma20, 2),
        "macd_hist": round(macd_hist, 4),
        "rsi": round(rsi, 2) if rsi is not None and pd.notna(rsi) else None,
        "volume": round(volume, 0) if volume is not None else None,
        "source_module": "update_strategy_data.py",
        **strategy,
    }


def upsert_signal(payload: dict) -> None:
    try:
        sb.table("lion_king_signals").upsert(payload).execute()
        return
    except Exception as exc:
        print(f"⚠️ 完整策略欄位寫入失敗，改寫基本欄位: {exc}")

    fallback = {key: value for key, value in payload.items() if key in BASE_SIGNAL_FIELDS}
    sb.table("lion_king_signals").upsert(fallback).execute()


def main() -> None:
    name_map = load_name_map()
    print(f"🚀 啟動 LionKing V111 策略同步，共 {len(name_map)} 檔標的")

    try:
        seed_strategy_rules()
    except Exception as exc:
        print(f"⚠️ 策略規則同步失敗，請先執行 supabase/strategy_upgrade_v111.sql: {exc}")

    for ticker, (name, sector) in name_map.items():
        try:
            payload = compute_signal(ticker, name, sector)
            if not payload:
                print(f"⚠️ {name} ({ticker}) 資料不足，略過")
                continue
            upsert_signal(payload)
            print(f"✅ {name} ({ticker}) 寫入成功 | {payload['signal_level']} {payload['strategy_score']}/100")
            time.sleep(0.2)
        except Exception as exc:
            print(f"❌ {name} ({ticker}) 寫入失敗: {exc}")

    print("🏁 LionKing V111 策略同步完成")


if __name__ == "__main__":
    main()
