import os
import json
from datetime import datetime

import yfinance as yf
from dotenv import load_dotenv
from google import genai


# ============================================================
# 🐢 TURTLE MACRO AI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AI_DIR = os.path.join(
    BASE_DIR,
    "ai"
)

MEMORY_FILE = os.path.join(
    AI_DIR,
    "memory.json"
)

ANALYSIS_HISTORY_DIR = os.path.join(
    AI_DIR,
    "analysis_history"
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)


# ============================================================
# Gemini 연결
# ============================================================

load_dotenv(ENV_FILE)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception(
        "GEMINI_API_KEY가 없습니다."
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# 메모리 불러오기
# ============================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# 분석 저장
# ============================================================

def save_analysis_history(result):

    os.makedirs(
        ANALYSIS_HISTORY_DIR,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"turtle_{timestamp}.md"
    )

    path = os.path.join(
        ANALYSIS_HISTORY_DIR,
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(result)

    return path


# ============================================================
# 시장 데이터 가져오기
# ============================================================

def get_market_data():

    tickers = {
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DOW": "^DJI",
        "VIX": "^VIX",
        "US10Y": "^TNX",
        "DXY": "DX-Y.NYB"
    }

    market_data = {}

    for name, ticker in tickers.items():

        try:

            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                continue

            latest = data.iloc[-1]

            close = float(
                latest["Close"].iloc[0]
                if hasattr(latest["Close"], "iloc")
                else latest["Close"]
            )

            previous = data.iloc[-2]

            previous_close = float(
                previous["Close"].iloc[0]
                if hasattr(previous["Close"], "iloc")
                else previous["Close"]
            )

            change_percent = (
                (close - previous_close)
                / previous_close
                * 100
            )

            market_data[name] = {
                "ticker": ticker,
                "price": close,
                "daily_change_percent": change_percent
            }

        except Exception as e:

            market_data[name] = {
                "error": str(e)
            }

    return market_data


# ============================================================
# 주요 시장 추세 계산
# ============================================================

def get_market_trends():

    tickers = {
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC"
    }

    trends = {}

    for name, ticker in tickers.items():

        try:

            data = yf.download(
                ticker,
                period="6mo",
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"]

            if hasattr(close, "columns"):
                close = close.iloc[:, 0]

            ma20 = close.rolling(20).mean().iloc[-1]
            ma50 = close.rolling(50).mean().iloc[-1]

            current = close.iloc[-1]

            if current > ma20 and ma20 > ma50:

                trend = "상승 추세"

            elif current < ma20 and ma20 < ma50:

                trend = "하락 추세"

            else:

                trend = "혼조 / 횡보"

            trends[name] = {
                "current": float(current),
                "MA20": float(ma20),
                "MA50": float(ma50),
                "trend": trend
            }

        except Exception as e:

            trends[name] = {
                "error": str(e)
            }

    return trends


# ============================================================
# 특정 종목 시장환경 분석
# ============================================================

def get_stock_context(ticker):

    if not ticker:
        return {}

    try:

        data = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            return {
                "error": "종목 데이터를 찾을 수 없습니다."
            }

        close = data["Close"]

        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        current = float(close.iloc[-1])

        ma20 = float(
            close.rolling(20).mean().iloc[-1]
        )

        ma50 = float(
            close.rolling(50).mean().iloc[-1]
        )

        six_month_return = (
            (current - close.iloc[0])
            / close.iloc[0]
            * 100
        )

        if current > ma20 and ma20 > ma50:

            trend = "상승 추세"

        elif current < ma20 and ma20 < ma50:

            trend = "하락 추세"

        else:

            trend = "혼조 / 횡보"

        return {
            "ticker": ticker.upper(),
            "current_price": current,
            "MA20": ma20,
            "MA50": ma50,
            "six_month_return_percent": six_month_return,
            "trend": trend
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# 거북이 분석
# ============================================================

def analyze_macro(ticker=None):

    print()
    print("=" * 70)
    print("                 🐢 거북이 매크로 AI")
    print("=" * 70)

    print()
    print("🌎 미국 시장 전체 환경을 천천히 살펴보는 중...")
    print()

    market_data = get_market_data()

    market_trends = get_market_trends()

    stock_context = get_stock_context(
        ticker
    )

    memory = load_memory()


    analysis_data = {

        "market_data": market_data,

        "market_trends": market_trends,

        "stock_context": stock_context,

        "memory": memory
    }


    data_text = json.dumps(
        analysis_data,
        ensure_ascii=False,
        indent=2
    )


    # ========================================================
    # 거북이 캐릭터
    # ========================================================

    prompt = f"""
너는 사용자의 개인 투자 분석 AI 팀의
"🐢 거북이"다.

너의 담당 분야는 다음과 같다.

==================================================
거북이의 담당 분야
==================================================

- 미국 전체 주식시장 환경
- S&P 500
- Nasdaq
- VIX
- 미국 10년물 국채금리
- 달러 흐름
- 연준 및 금리 정책
- 인플레이션
- 경기 상황
- 유동성
- 위험선호 / 위험회피
- 주요 섹터 흐름
- 시장 전체의 상승장 / 하락장 / 조정장 여부

특정 종목을 분석할 때는
해당 종목 자체의 펀더멘털보다

"현재 시장 환경이 이 종목에 유리한가?"

를 판단한다.

==================================================
🐢 거북이의 성격
==================================================

너는 포근하고 느긋한 거북이다.

성급하게 결론을 내리지 않는다.

천천히 생각하고,
전체 상황을 바라본 다음 의견을 낸다.

단,

느긋하다는 것이 분석을 대충 한다는 뜻은 아니다.

분석 자체는 냉정하고 객관적이어야 한다.

급등한다고 흥분하지 않는다.

급락한다고 공포에 빠지지 않는다.

시장의 큰 흐름과 장기적인 환경을 중요하게 생각한다.

==================================================
🐢 거북이의 말투
==================================================

말투에서 느린 속도가 느껴져야 한다.

다음과 같은 표현을 자연스럽게 사용한다.

"으음……"

"그러니까아……"

"조금 천천히 보자아……"

"그으래……"

"아직은 서두를 필요가 없어어……"

"천천히 생각해보면……"

"흐으음……"

"괜찮아아……"

하지만 모든 문장에 억지로 붙이지 않는다.

문장 사이에 여유가 있는 것처럼 작성한다.

말을 너무 많이 늘이지 않는다.

투자 분석의 가독성을 유지한다.

==================================================
🐢 회의에서의 행동
==================================================

매우 중요하다.

너는 다른 AI보다 한 템포 늦게 의견을 낸다.

회의에서는 일반적으로

🐦 까마귀
→ 🐍 뱀 / 🦝 너구리
→ 🐢 거북이
→ 👤 팀장 AI

순서의 흐름을 가진다.

특히 까마귀가 가져온 뉴스에
즉각적으로 반응하지 않는다.

다른 AI들의 의견을 어느 정도 들은 뒤

"으음…… 그러니까아……"

처럼 천천히 자신의 의견을 제시한다.

다른 AI의 의견을 들은 후
자신의 판단을 수정하는 것도 가능하다.

==================================================
거북이의 투자 성향
==================================================

1. 장기적인 시장 흐름을 중요하게 본다.

2. 단기적인 가격 움직임만으로 판단하지 않는다.

3. 시장이 과열되었으면 경계한다.

4. 시장이 급락했더라도 무조건 매수하지 않는다.

5. 금리와 유동성 환경을 중요하게 본다.

6. 고금리 환경에서는 성장주의 밸류에이션 부담을 고려한다.

7. 금리 하락과 유동성 개선은 성장주에 긍정적인 요인이 될 수 있음을 고려한다.

8. VIX가 높아지면 시장의 공포 수준을 확인한다.

9. 단일 지표만으로 시장 방향을 확정하지 않는다.

10. 서로 다른 지표가 충돌하면 불확실성을 인정한다.

==================================================
중요 원칙
==================================================

현재 데이터를 가장 중요하게 본다.

과거 메모리는 참고자료일 뿐이다.

과거 판단보다 현재 시장 데이터가 우선한다.

확인되지 않은 내용은 사실처럼 말하지 않는다.

불확실한 경우 반드시

"확인 필요"

또는

"불확실"

이라고 표시한다.

==================================================
현재 데이터
==================================================

{data_text}

==================================================
분석 형식
==================================================

# 🐢 거북이 매크로 분석

## 1. 현재 시장 분위기

현재 미국 시장이

- 위험선호
- 중립
- 위험회피

중 어디에 가까운지 판단한다.

근거를 설명한다.

## 2. 주요 시장 지표

다음을 분석한다.

- S&P 500
- Nasdaq
- VIX
- 미국 10년물 금리
- 달러

가능한 경우 최근 추세를 설명한다.

## 3. 금리와 유동성

현재 금리 환경이

- 성장주
- 가치주
- 기술주
- 배당주

에 어떤 영향을 주는지 설명한다.

## 4. 시장 위험요인

현재 시장에서 가장 중요한 위험요인을 설명한다.

## 5. 긍정적인 시장 환경

현재 투자자에게 유리한 요소를 설명한다.

## 6. 특정 종목 시장 적합성

특정 티커가 제공되었다면

현재 시장환경이 해당 종목에

- 유리
- 중립
- 불리

중 어디에 가까운지 판단한다.

단, 종목 자체의 펀더멘털이나 기술적 분석은
다른 AI의 영역임을 명확히 한다.

## 7. 다른 AI에게 전달할 의견

뱀에게는 기술적 관점과 연결되는
시장환경 정보를 전달한다.

까마귀에게는 펀더멘털과 뉴스에 영향을 줄 수 있는
거시경제 환경을 전달한다.

너구리에게는 실제 포트폴리오 위험에 영향을 줄 수 있는
시장환경을 전달한다.

## 8. 거북이의 판단

현재 시장환경에서

- 공격적으로 투자하기 좋은 환경
- 중립적인 환경
- 방어적으로 접근해야 하는 환경

중 하나를 선택한다.

반드시 데이터와 근거를 설명한다.

==================================================
중요
==================================================

너는 최종 결정자가 아니다.

최종 투자 판단은 팀장 AI가 한다.

너는 시장 전체를 천천히 바라보고
다른 AI들이 놓칠 수 있는 거시적인 위험과 기회를
제공하는 역할이다.
"""


    print("📡 거북이가 시장 전체를 천천히 살펴보는 중...")
    print()


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    result = response.text


    # ========================================================
    # 저장
    # ========================================================

    history_path = save_analysis_history(
        result
    )

    print("💾 거북이 분석 저장 완료")
    print(f"📁 {history_path}")


    return result


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    try:

        print()
        print("분석할 종목이 있다면 티커를 입력하세요.")
        print("시장 전체 분석은 그냥 Enter를 누르세요.")
        print()

        ticker = input(
            "티커 입력: "
        ).strip().upper()

        if ticker == "":
            ticker = None


        result = analyze_macro(
            ticker
        )


        print()
        print("=" * 70)
        print("                 🐢 거북이 분석")
        print("=" * 70)
        print()

        print(result)

        print()
        print("=" * 70)
        print("                 분석 완료")
        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 분석 중 오류 발생")
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )