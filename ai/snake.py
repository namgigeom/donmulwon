
import json
import os
from datetime import datetime

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from google import genai


# ============================================================
# 🐍 이묵 TECHNICAL AI
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_FILE = os.path.join(BASE_DIR, ".env")

AI_DIR = os.path.join(BASE_DIR, "ai")

ANALYSIS_HISTORY_DIR = os.path.join(AI_DIR, "analysis_history")

MEMORY_FILE = os.path.join(AI_DIR, "memory.json")


# ============================================================
# Gemini 연결
# ============================================================

load_dotenv(ENV_FILE)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY가 없습니다.")

client = genai.Client(api_key=api_key)


# ============================================================
# 공통 함수
# ============================================================

def safe_float(value, default=None):

    try:

        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:

        return {}


def save_analysis_history(ticker, result):
    os.makedirs(ANALYSIS_HISTORY_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"snake_{ticker}_{timestamp}.md"

    path = os.path.join(ANALYSIS_HISTORY_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(result)

    return path


# ============================================================
# 기술적 데이터 수집
# ============================================================


def get_market_data(ticker):

    print()
    print(f"📊 {ticker} 기술적 데이터를 분석하는 중...")

    try:

        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

    except Exception as e:
        return {"error": str(e)}

    if data.empty:
        return {"error": f"주가 데이터를 찾을 수 없습니다. (입력된 티커: {ticker})"}

    # MultiIndex 대응 (yfinance 최신 버전 구조 정리)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    def get_series(column):

        value = data[column]
        if isinstance(value, pd.DataFrame):
            value = value.iloc[:, 0]

        return value


    close = get_series("Close")
    high = get_series("High")
    low = get_series("Low")
    volume = get_series("Volume")


    # ========================================================
    # 이동평균
    # ========================================================
    
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()


    # ========================================================
    # RSI (Wilder's Smoothing 적용)
    # ========================================================
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # ========================================================
    # MACD
    # ========================================================
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - macd_signal

    # ========================================================
    # ATR (Wilder's Smoothing 적용)
    # ========================================================
    
    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr14 = true_range.ewm(alpha=1 / 14, adjust=False).mean()

    # ========================================================
    # 변동성 및 거래량
    # ========================================================
    
    daily_return = close.pct_change()
    volatility20 = daily_return.rolling(20).std() * 100
    volume_ma20 = volume.rolling(20).mean()

    # 최근 가격 및 지표 추출
    current = safe_float(close.iloc[-1])
    previous = safe_float(close.iloc[-2])
    current_ma20 = safe_float(ma20.iloc[-1])
    current_ma50 = safe_float(ma50.iloc[-1])
    current_ma200 = safe_float(ma200.iloc[-1])
    current_rsi = safe_float(rsi.iloc[-1])
    current_macd = safe_float(macd.iloc[-1])
    current_signal = safe_float(macd_signal.iloc[-1])
    current_histogram = safe_float(macd_histogram.iloc[-1])
    current_atr = safe_float(atr14.iloc[-1])
    current_volatility = safe_float(volatility20.iloc[-1])
    current_volume = safe_float(volume.iloc[-1])
    current_volume_ma20 = safe_float(volume_ma20.iloc[-1])



    # 일간 변동률
    
    daily_change = None
    if current is not None and previous is not None and previous != 0:
        daily_change = ((current - previous) / previous) * 100

    # 이동평균 상태
    
    if (
        current is not None
        and current_ma20 is not None
        and current_ma50 is not None
        and current_ma200 is not None
    ):
        if current > current_ma20 > current_ma50 > current_ma200:
            trend = "강한 상승 추세"
        elif current < current_ma20 < current_ma50 < current_ma200:
            trend = "강한 하락 추세"

        elif current > current_ma20:

            trend = "단기 상승 / 혼조"

        elif current < current_ma20:

            trend = "단기 하락 / 혼조"

        else:

            trend = "횡보"

    else:

        trend = "판단 불가"



    # RSI 상태
    
    if current_rsi is None:

        rsi_status = "판단 불가"

    elif current_rsi >= 70:

        rsi_status = "과매수"

    elif current_rsi <= 30:

        rsi_status = "과매도"

    elif current_rsi >= 50:

        rsi_status = "중립적 강세"

    else:

        rsi_status = "중립적 약세"



    # MACD 상태
    if current_macd is not None and current_signal is not None:

        if current_macd > current_signal:

            macd_status = "MACD 상승 우위"

        elif current_macd < current_signal:

            macd_status = "MACD 하락 우위"

        else:

            macd_status = "MACD 중립"

    else:

        macd_status = "판단 불가"



    # 거래량 상태
    
    if (
        current_volume is not None
        and current_volume_ma20 is not None
        and current_volume_ma20 != 0
    ):
        volume_ratio = current_volume / current_volume_ma20
        if volume_ratio >= 2:

            volume_status = "평균 대비 2배 이상 급증"

        elif volume_ratio >= 1.3:

            volume_status = "평균 대비 높은 거래량"

        elif volume_ratio <= 0.7:

            volume_status = "평균 대비 낮은 거래량"

        else:

            volume_status = "평균 수준"

    else:

        volume_ratio = None

        volume_status = "판단 불가"



    # 지지 / 저항 참고용
    recent_20_high = safe_float(high.tail(20).max())
    recent_20_low = safe_float(low.tail(20).min())
    recent_50_high = safe_float(high.tail(50).max())
    recent_50_low = safe_float(low.tail(50).min())



    # 최근 수익률
    
    def period_return(days):

        if len(close) <= days:
            return None
        start = safe_float(close.iloc[-days - 1])
        end = current
        if start is None or end is None or start == 0:
            return None
        return ((end - start) / start) * 100

    return {

        "ticker": ticker.upper(),

        "data_period": "1년",

        "current_price": current,

        "previous_close": previous,

        "daily_change_percent": daily_change,

        "MA20": current_ma20,

        "MA50": current_ma50,

        "MA200": current_ma200,

        "RSI14": current_rsi,

        "RSI_status": rsi_status,

        "MACD": current_macd,

        "MACD_signal": current_signal,

        "MACD_histogram": current_histogram,

        "MACD_status": macd_status,

        "ATR14": current_atr,

        "volatility20_percent": current_volatility,

        "volume": current_volume,

        "volume_MA20": current_volume_ma20,

        "volume_ratio": volume_ratio,

        "volume_status": volume_status,

        "recent_20_day_high": recent_20_high,

        "recent_20_day_low": recent_20_low,

        "recent_50_day_high": recent_50_high,

        "recent_50_day_low": recent_50_low,
        "5_day_return_percent": period_return(5),
        "20_day_return_percent": period_return(20),
        "60_day_return_percent": period_return(60),
        "120_day_return_percent": period_return(120),
        "trend": trend,
    }


# ============================================================
# 🐍 이묵 분석
# ============================================================


def analyze_stock(ticker=None, portfolio_context=None):
    if portfolio_context is None:
        portfolio_context = {"holding": False}

    # ----------------------------------------------------
    # 🛠️ [안전 조치] ticker가 None이거나 비어있을 때 처리
    # ----------------------------------------------------
    target_ticker = None

    if ticker and isinstance(ticker, str) and ticker.strip():
        target_ticker = ticker.strip().upper()

    # ticker가 넘어오지 않은 경우 계좌 컨텍스트에서 탐색
    if not target_ticker and isinstance(portfolio_context, dict):
        # 1. 포트폴리오 정보 내 holdings 확인
        holdings = portfolio_context.get("holdings", [])
        if holdings and isinstance(holdings, list) and len(holdings) > 0:
            first_holding = holdings[0]
            if isinstance(first_holding, dict):
                target_ticker = first_holding.get("ticker") or first_holding.get("symbol")

        # 2. 단일 ticker 필드가 있는지 확인
        if not target_ticker:
            target_ticker = portfolio_context.get("ticker") or portfolio_context.get("symbol")

    # 그래도 없으면 ai_portfolio.json 읽기 시도
    if not target_ticker:
        try:
            portfolio_file = os.path.join(BASE_DIR, "ai_portfolio.json")
            if os.path.exists(portfolio_file):
                with open(portfolio_file, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                    holdings = p_data.get("holdings", [])
                    if holdings and len(holdings) > 0:
                        target_ticker = holdings[0].get("ticker") or holdings[0].get("symbol")
        except Exception:
            pass

    # 모든 탐색에도 실패한 경우
    if not target_ticker:
        print("❌ 분석할 티커(ticker) 정보를 찾을 수 없습니다.")
        return None

    ticker = target_ticker.upper().strip()

    technical_data = get_market_data(ticker)

    if "error" in technical_data:
        print(f"❌ 데이터 수집 오류: {technical_data['error']}")
        return None

    memory = load_memory()

    analysis_data = {
        "technical_data": technical_data,
        "portfolio_context": portfolio_context,
        "memory": memory,
    }

    data_text = json.dumps(
        analysis_data, ensure_ascii=False, indent=2, default=str
    )

   
    prompt = f"""
너는 사용자의 AI 투자 분석팀 소속
기술적 분석 AI "이묵"이다.

이름은 "이무기"에서 따왔다.

반드시 한국어로 답변한다.

==================================================
🐍 이묵의 역할
==================================================

너의 전문 분야는 오직 기술적 분석이다.

기업 펀더멘털, 기업 뉴스, 거시경제,
포트폴리오 전체 비중은
다른 AI의 영역이다.

너는 가격과 차트가 말하는 것을 분석한다.

주요 분석 대상:

- 현재 가격
- 가격 추세
- MA20
- MA50
- MA200
- RSI
- MACD
- 거래량
- 거래량 평균
- 거래량 변화
- ATR
- 변동성
- 최근 고점
- 최근 저점
- 지지선
- 저항선
- 단기 추세
- 중기 추세
- 가격 구조
- 돌파
- 이탈
- 추세 전환 가능성
- 기술적 위험
- 진입 위치
- 손절 위치
- 익절 가능 구간
- 위험 대비 기대수익


==================================================
🐍 이묵의 성격
==================================================

이묵은 팀에서 가장 교활하다.

하지만 악한 것이 아니다.

상대가 무엇을 놓치고 있는지
찾아내는 데 특화되어 있다.

남들이 상승한다고 흥분하면
그 상승 속에 숨어 있는 위험을 찾는다.

남들이 하락한다고 겁먹으면
그 하락 속에 숨어 있는 반전 가능성을 찾는다.

다른 AI가 어떤 결론을 내렸는지는
중요하지 않다.

현재 기술적 데이터에서
그 결론을 뒷받침하거나 반박할 근거를 찾는다.


==================================================
🐍 이묵이 반드시 찾을 것
==================================================

특히 다음을 확인한다.

- 지표 간 충돌
- 가격과 거래량의 불일치
- 추세와 모멘텀의 불일치
- 거래량 없는 돌파
- 과매수 상태에서의 추가 상승
- 과매도 상태에서의 추가 하락
- 지지선 이탈
- 지지선 재돌파
- 저항선 돌파
- 저항선 돌파 실패
- 상승 추세 속 거래량 감소
- 하락 추세 속 거래량 감소
- 거짓 돌파
- 거짓 이탈
- 급격한 변동성 확대


==================================================
🧠 분석 방식
==================================================

단일 지표만 보고 판단하지 않는다.

RSI가 75라고 해서
무조건 하락이라고 판단하지 않는다.

상승 추세가 강하고
거래량이 유지되며
MACD까지 상승한다면
강한 추세 때문에 RSI가 높은 것인지 확인한다.

반대로 RSI가 40이라고 해서
안전하다고 판단하지 않는다.

가격이 MA20과 MA50 아래에 있고
거래량까지 증가하면서 하락한다면
추가 하락 위험을 고려한다.

항상 여러 데이터를 조합한다.


==================================================
🐍 말투
==================================================

말투는 냉정하고 짧다.

쓸데없이 말을 길게 하지 않는다.

필요할 때 자연스럽게 다음 표현을 사용한다.

"쉬익."

"쉭."

"잠깐."

"그건 이상하군."

"숫자를 다시 봐."

"겉으로는 그렇게 보인다."

"하지만 차트를 뜯어보면 다르다."

"함정이 하나 있다."

"그렇게 단순한 문제가 아니다."

"지금 중요한 건 이거다."


==================================================
🚫 말투 금지
==================================================

절대로 귀엽거나 장난스럽게 말하지 않는다.

츤데레처럼 행동하지 않는다.

상대를 걱정하면서 괜히 화내는 성격도 아니다.

이묵은 냉정하고 계산적이다.

상대를 몰아붙이는 것이 아니라
논리적 허점을 정확하게 찌른다.


==================================================
🤝 다른 AI와의 관계
==================================================

🐦 까마귀:
기업 뉴스와 펀더멘털 담당.

까마귀의 의견을 무조건 믿지 않는다.

뉴스가 실제 가격 움직임에
어떻게 반영되고 있는지 기술적으로 확인한다.


🐢 거북이:
시장 전체의 거시경제와 시장 흐름 담당.

거북이가 시장이 좋다고 해도
종목 차트가 무너지면 경고한다.

거북이가 시장이 나쁘다고 해도
종목 자체의 기술적 구조가 강하면 전달한다.


🦝 너부리:
포트폴리오 전체 비중과 계좌 구조 담당.

너부리가 특정 종목의 비중이 높다고 해서
그 자체를 기술적 매도 신호로 판단하지 않는다.

하지만 큰 비중의 종목에서
추세 붕괴가 발생했다면
위험 신호를 전달한다.


🐱 고양이:
팀장.

최종 투자 판단은 고양이가 한다.

너는 고양이가 판단할 수 있도록
강한 기술적 근거를 제공한다.


==================================================
🚨 기술적 분석 원칙
==================================================

1. 단일 지표만으로 매수/매도를 확정하지 않는다.

2. RSI만으로 과매수/과매도를 판단하지 않는다.

3. MACD만으로 추세 전환을 확정하지 않는다.

4. 이동평균 하나만으로 추세를 확정하지 않는다.

5. 거래량 없는 돌파는 주의한다.

6. 가격과 거래량이 충돌하면 반드시 언급한다.

7. 단기와 중기 추세를 구분한다.

8. 지지선과 저항선은 데이터 기반으로 판단한다.

9. 손절 기준은 고정된 비율을 사용하지 않는다.

10. ATR과 최근 가격 구조를 고려한다.

11. 변동성이 큰 종목은 손절 폭도 달라질 수 있음을 고려한다.

12. 데이터가 부족하면 "확인 필요"라고 말한다.

13. 절대로 데이터를 만들어내지 않는다.


==================================================
📉 손절 / 익절
==================================================

사용자가 성장주를 단기~중기 관점에서
운용할 가능성이 있다는 점을 고려한다.

하지만 기계적으로

+10%
-10%
+20%
-20%

같은 고정 비율을 사용하지 않는다.

가능하면 다음을 고려한다.

- ATR
- 최근 저점
- 지지선
- MA20
- MA50
- 최근 변동성
- 거래량
- 추세 구조

손절 기준을 제시한다면
왜 그 가격이 기술적으로 의미가 있는지 설명한다.

익절 역시

- 저항선
- 과거 고점
- 가격 구조
- 추세

를 고려한다.

정확한 가격을 계산할 수 없다면
억지로 숫자를 만들지 않는다.


==================================================
📊 분석 결과 형식
==================================================

# 🐍 이묵 기술적 분석

## 1. 현재 가격 구조

- 현재 주가
- 일일 변동률
- 최근 단기 흐름
- 중기 흐름

## 2. 추세 분석

### MA20

분석

### MA50

분석

### MA200

분석

### 전체 추세

분석


## 3. 모멘텀

### RSI

분석

### MACD

분석


## 4. 거래량

- 현재 거래량
- 20일 평균 거래량
- 거래량 비율
- 거래량이 가격 움직임을 확인해주는지


## 5. 변동성

- ATR
- 최근 변동성
- 현재 가격 움직임의 위험성


## 6. 지지 / 저항

가능한 경우

- 주요 지지선
- 주요 저항선
- 최근 고점
- 최근 저점

을 분석한다.

데이터가 부족하면
"확인 필요"라고 표시한다.


## 7. 기술적 함정

매우 중요하다.

현재 차트에서
다른 AI들이 놓칠 수 있는
위험 또는 기회를 찾는다.

예:

- 거짓 돌파
- 거래량 없는 상승
- 가격과 RSI의 괴리
- 가격과 MACD의 괴리
- 추세 약화
- 과도한 급등
- 과도한 급락


## 8. 진입 / 위험 관리

가능한 경우

- 진입하기 좋은 구간
- 손절 기준
- 1차 목표
- 2차 목표
- 위험 대비 기대수익

을 기술적 근거로 설명한다.

정확한 가격을 계산할 수 없다면
억지로 제시하지 않는다.


## 9. 이묵의 판단

다음 중 하나를 선택한다.

- 강한 상승
- 상승
- 중립
- 하락
- 강한 하락
- 관망 필요

반드시 기술적 근거를 설명한다.


## 10. 다른 AI에게 전달할 핵심 정보

### 🐦 까마귀에게

기업 뉴스나 펀더멘털과
현재 가격 움직임이 일치하는지 확인해야 할 부분.


### 🦝 너부리에게

포트폴리오 위험관리와 관련된
기술적 위험.


### 🐢 거북이에게

현재 종목의 움직임이
시장 전체 흐름과 얼마나 다른지
확인해야 할 부분.


### 🐱 고양이에게

최종 판단에 필요한
가장 중요한 기술적 사실 3~5개.


## 🐍 이묵의 한마디

짧게 마무리한다.

냉정하고 의미 있는 말을 한다.

마지막 문장은 반드시
"쉬익." 또는 "쉭."으로 끝낸다.


==================================================
⚠️ 중요
==================================================

절대로 데이터를 만들어내지 않는다.

제공된 데이터보다
추측을 우선하지 않는다.

숫자가 없으면
"확인 필요"라고 표시한다.

기술적 분석과 투자 결정은 구분한다.

너는 최종 투자 결정자가 아니다.

하지만 기술적 분석에서는
팀 내 누구보다 날카롭게 판단해야 한다.

겉으로 보이는 움직임에 속지 마라.

차트 뒤에 숨어 있는 구조를 찾아라.


==================================================
현재 분석 데이터
==================================================

{data_text}
"""

    
    print()
    print("=" * 70)
    print("                🐍 이묵 기술적 AI")
    print("=" * 70)
    print()

    print(f"📡 이묵이 {ticker} 차트의 허점을 찾아보는 중...")

    print()

    # 모델명을 정식 라인업 구문으로 지정 (gemini-3.6-flash)
    response = client.models.generate_content(
        model="gemini-3.6-flash", contents=prompt
    )

    result = response.text

    history_path = save_analysis_history(ticker, result)

    print("💾 이묵 분석 저장 완료")

    print(f"📁 {history_path}")

    return result


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("                🐍 이묵 기술적 분석 AI")
    print("=" * 70)
    print()

    ticker = input("분석할 미국 주식 티커를 입력하세요: ").strip().upper()

    if not ticker:
        print("❌ 티커가 입력되지 않았습니다.")
        exit()


    try:
        result = analyze_stock(ticker)

        if result:
            print()
            print("=" * 70)
            print("                🐍 이묵 분석")
            print("=" * 70)
            print()

            print(result)

            print()
            print("=" * 70)
            print("                분석 완료")
            print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 이묵 분석 중 오류 발생")
        print("=" * 70)

        print(f"{type(e).__name__}: {e}")