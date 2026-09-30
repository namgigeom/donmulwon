"""Technical preprocessing for 🐍 이묵.

Converts raw OHLCV/indicator data into a compact, explicit chart-reading brief.
The LLM receives computed evidence and the recent candles separately.
"""
import math


def _f(v):
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _sign(v):
    v = _f(v)
    if v is None:
        return "확인 필요"
    return "상승" if v > 0 else "하락" if v < 0 else "보합"


def _relation(price, level):
    price, level = _f(price), _f(level)
    if price is None or level in (None, 0):
        return "확인 필요"
    d = (price / level - 1) * 100
    return f"{d:+.2f}% ({'위' if d >= 0 else '아래'})"


def _cross(a, b):
    a, b = _f(a), _f(b)
    if a is None or b is None:
        return "확인 필요"
    return "상향" if a > b else "하향" if a < b else "동일"


def build_chart_brief(stock):
    if not isinstance(stock, dict) or stock.get("status") != "OK":
        return {"status": "NO_DATA", "reason": stock.get("error", "기술 데이터 없음") if isinstance(stock, dict) else "기술 데이터 없음"}

    p = _f(stock.get("current_price"))
    ma20, ma50, ma200 = _f(stock.get("MA20")), _f(stock.get("MA50")), _f(stock.get("MA200"))
    rsi, macd, signal = _f(stock.get("RSI14")), _f(stock.get("MACD")), _f(stock.get("MACD_signal"))
    atr, atr_pct = _f(stock.get("ATR14")), _f(stock.get("ATR_percent_of_price"))
    vr = _f(stock.get("volume_ratio"))
    h20, l20 = _f(stock.get("recent_20_day_high")), _f(stock.get("recent_20_day_low"))
    h50, l50 = _f(stock.get("recent_50_day_high")), _f(stock.get("recent_50_day_low"))
    h52, l52 = _f(stock.get("52_week_high")), _f(stock.get("52_week_low"))
    returns = stock.get("returns") or {}

    above = [x for x, level in (("MA20", ma20), ("MA50", ma50), ("MA200", ma200)) if p is not None and level is not None and p > level]
    below = [x for x, level in (("MA20", ma20), ("MA50", ma50), ("MA200", ma200)) if p is not None and level is not None and p < level]

    if p is not None and ma20 and ma50 and ma200:
        if p > ma20 > ma50 > ma200:
            trend = "정배열 상승"
        elif p < ma20 < ma50 < ma200:
            trend = "역배열 하락"
        elif p > ma20 and ma20 < ma50:
            trend = "단기 반등/중기 약세 가능성"
        elif p < ma20 and ma20 > ma50:
            trend = "단기 조정/중기 상승 가능성"
        else:
            trend = "혼조 또는 횡보"
    else:
        trend = stock.get("trend", "확인 필요")

    if rsi is None:
        momentum = "RSI 확인 필요"
    elif rsi >= 70:
        momentum = f"과열권(RSI {rsi:.1f})"
    elif rsi <= 30:
        momentum = f"침체권(RSI {rsi:.1f})"
    elif rsi >= 55:
        momentum = f"상대적 강세(RSI {rsi:.1f})"
    elif rsi <= 45:
        momentum = f"상대적 약세(RSI {rsi:.1f})"
    else:
        momentum = f"중립(RSI {rsi:.1f})"

    if macd is not None and signal is not None:
        macd_state = f"MACD {'상향' if macd > signal else '하향'} 신호선 교차/위치, 히스토그램 {_sign(stock.get('MACD_histogram'))}"
    else:
        macd_state = "MACD 확인 필요"

    if vr is None:
        volume_state = "거래량 확인 필요"
    elif vr >= 1.8:
        volume_state = f"평균 대비 거래량 급증({vr:.2f}x)"
    elif vr >= 1.2:
        volume_state = f"평균 대비 거래량 증가({vr:.2f}x)"
    elif vr <= 0.7:
        volume_state = f"평균 대비 거래량 감소({vr:.2f}x)"
    else:
        volume_state = f"평균 수준({vr:.2f}x)"

    return {
        "status": "OK",
        "ticker": stock.get("ticker"),
        "trend": trend,
        "price_vs_ma20": _relation(p, ma20),
        "price_vs_ma50": _relation(p, ma50),
        "price_vs_ma200": _relation(p, ma200),
        "moving_average_stack": _cross(ma20, ma50) + " MA20/MA50, " + _cross(ma50, ma200) + " MA50/MA200",
        "above_mas": above,
        "below_mas": below,
        "momentum": momentum,
        "macd": macd_state,
        "volume": volume_state,
        "volatility": f"ATR14 {atr:.4f} / 가격 대비 {atr_pct:.2f}%" if atr is not None and atr_pct is not None else "ATR 확인 필요",
        "support_resistance": {
            "support_20d": l20,
            "resistance_20d": h20,
            "support_50d": l50,
            "resistance_50d": h50,
            "52w_low": l52,
            "52w_high": h52,
            "distance_to_20d_support": _relation(p, l20),
            "distance_to_20d_resistance": _relation(p, h20),
        },
        "returns": {k: returns.get(k) for k in ("5d", "20d", "60d", "120d")},
        "reading_rules": [
            "눌림목은 단순 하락만으로 판정하지 말고 상승 추세 유지 여부, MA20/50 지지, 거래량 감소 후 반등 여부를 함께 본다.",
            "돌파는 저항선 상향 이탈과 거래량 증가가 동반되는지 확인한다.",
            "지지선은 단일 숫자가 아니라 최근 swing low와 MA가 겹치는 가격대를 우선한다.",
            "RSI 과열/침체만으로 매수·매도를 결정하지 않는다.",
        ],
    }


def build_snake_prompt_data(stocks):
    briefs = {}
    for ticker, stock in (stocks or {}).items():
        briefs[ticker] = build_chart_brief(stock)
    return briefs
