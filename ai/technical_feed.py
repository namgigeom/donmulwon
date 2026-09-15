"""Robust technical-market feed for 🐍 이묵.

Keeps the raw OHLCV series separate from the LLM prompt so the technical
agent always receives actual chart evidence instead of a vague market summary.
"""
import math
import pandas as pd
import yfinance as yf


def _series(frame, name):
    value = frame[name]
    if isinstance(value, pd.DataFrame):
        value = value.iloc[:, 0]
    return pd.to_numeric(value, errors="coerce")


def _f(v):
    try:
        if v is None or pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None


def _pct(a, b):
    if a is None or b in (None, 0):
        return None
    return (a / b - 1.0) * 100.0


def get_market_data(ticker):
    ticker = str(ticker).upper().strip()
    try:
        data = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
            repair=True,
            multi_level_index=True,
        )
    except Exception as exc:
        return {"error": f"Yahoo Finance 데이터 요청 실패: {type(exc).__name__}: {exc}"}

    if data is None or data.empty:
        return {"error": f"{ticker} 일봉 데이터가 비어 있습니다."}

    if isinstance(data.columns, pd.MultiIndex):
        # For a single ticker yfinance can return (field, ticker) or
        # (ticker, field). Select the OHLCV field level explicitly.
        if set(["Open", "High", "Low", "Close", "Volume"]).issubset(set(data.columns.get_level_values(0))):
            data.columns = data.columns.get_level_values(0)
        else:
            data.columns = data.columns.get_level_values(-1)

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [x for x in required if x not in data.columns]
    if missing:
        return {"error": f"{ticker} OHLCV 필드 누락: {', '.join(missing)}"}

    open_s = _series(data, "Open")
    high = _series(data, "High")
    low = _series(data, "Low")
    close = _series(data, "Close")
    volume = _series(data, "Volume")
    frame = pd.concat([open_s, high, low, close, volume], axis=1)
    frame.columns = required
    frame = frame.dropna(subset=["High", "Low", "Close"]).copy()
    if len(frame) < 30:
        return {"error": f"{ticker} 유효한 일봉 데이터가 {len(frame)}개뿐입니다."}

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - (100 / (1 + (avg_gain / avg_loss.replace(0, math.nan))))
    prev = close.shift(1)
    tr = pd.concat([(high - low), (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    returns = close.pct_change()
    vol20 = returns.rolling(20).std() * 100
    volume_ma20 = volume.rolling(20).mean()

    current = _f(close.iloc[-1])
    previous = _f(close.iloc[-2])
    atr_now = _f(atr.iloc[-1])
    ma20_now, ma50_now, ma200_now = _f(ma20.iloc[-1]), _f(ma50.iloc[-1]), _f(ma200.iloc[-1])
    rsi_now, macd_now, signal_now = _f(rsi.iloc[-1]), _f(macd.iloc[-1]), _f(signal.iloc[-1])
    vol_now, vol_ma = _f(volume.iloc[-1]), _f(volume_ma20.iloc[-1])

    # Recent swing levels: use completed daily candles, not the current close
    # alone. These are reference zones, not guaranteed support/resistance.
    recent = frame.tail(60)
    recent_20, recent_50 = frame.tail(20), frame.tail(50)
    resistance_20 = _f(recent_20["High"].max())
    support_20 = _f(recent_20["Low"].min())
    resistance_50 = _f(recent_50["High"].max())
    support_50 = _f(recent_50["Low"].min())

    # Last 60 candles are supplied to the model in compact form so it can
    # inspect actual price structure rather than inventing chart conclusions.
    candles = []
    for idx, row in recent.iterrows():
        candles.append({
            "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
            "open": _f(row["Open"]), "high": _f(row["High"]),
            "low": _f(row["Low"]), "close": _f(row["Close"]),
            "volume": _f(row["Volume"]),
        })

    trend = "데이터 부족"
    if ma20_now is not None and ma50_now is not None and ma200_now is not None:
        if current > ma20_now > ma50_now > ma200_now:
            trend = "강한 상승 추세"
        elif current < ma20_now < ma50_now < ma200_now:
            trend = "강한 하락 추세"
        elif current > ma20_now:
            trend = "단기 상승 / 중기 혼조"
        elif current < ma20_now:
            trend = "단기 하락 / 중기 혼조"
        else:
            trend = "횡보"

    return {
        "status": "OK",
        "ticker": ticker,
        "data_period": "2년 일봉",
        "bars_available": int(len(frame)),
        "current_price": current,
        "previous_close": previous,
        "daily_change_percent": _pct(current, previous),
        "MA20": ma20_now, "MA50": ma50_now, "MA200": ma200_now,
        "MA20_distance_percent": _pct(current, ma20_now),
        "MA50_distance_percent": _pct(current, ma50_now),
        "MA200_distance_percent": _pct(current, ma200_now),
        "RSI14": rsi_now,
        "MACD": macd_now, "MACD_signal": signal_now,
        "MACD_histogram": _f((macd - signal).iloc[-1]),
        "ATR14": atr_now,
        "ATR_percent_of_price": (atr_now / current * 100) if atr_now and current else None,
        "volatility20_percent": _f(vol20.iloc[-1]),
        "volume": vol_now, "volume_MA20": vol_ma,
        "volume_ratio": (vol_now / vol_ma) if vol_now is not None and vol_ma else None,
        "recent_20_day_high": resistance_20, "recent_20_day_low": support_20,
        "recent_50_day_high": resistance_50, "recent_50_day_low": support_50,
        "52_week_high": _f(frame.tail(252)["High"].max()),
        "52_week_low": _f(frame.tail(252)["Low"].min()),
        "trend": trend,
        "returns": {
            "5d": _pct(current, _f(close.iloc[-6])) if len(close) >= 6 else None,
            "20d": _pct(current, _f(close.iloc[-21])) if len(close) >= 21 else None,
            "60d": _pct(current, _f(close.iloc[-61])) if len(close) >= 61 else None,
            "120d": _pct(current, _f(close.iloc[-121])) if len(close) >= 121 else None,
        },
        "chart_data": candles,
        "data_note": "실제 Yahoo Finance 일봉 OHLCV와 계산 지표. chart_data는 최근 60거래일.",
    }
