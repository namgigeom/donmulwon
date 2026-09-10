import os
import json
from datetime import datetime

import yfinance as yf
from dotenv import load_dotenv
from google import genai
from ai import ai_router


# ============================================================
# 🐢 현무 MACRO AI
# 사신수 현무에서 따온 시장환경 분석 AI
# ============================================================


# ============================================================
# 기본 경로
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

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


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
# 숫자 변환
# ============================================================

def safe_float(value):

    try:
        return float(value)

    except Exception:

        return None


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

                market_data[name] = {
                    "ticker": ticker,
                    "error": "데이터 없음"
                }

                continue

            latest = data.iloc[-1]

            close = latest["Close"]

            if hasattr(close, "iloc"):

                close = close.iloc[0]

            close = float(close)

            if len(data) >= 2:

                previous = data.iloc[-2]

                previous_close = previous["Close"]

                if hasattr(
                    previous_close,
                    "iloc"
                ):

                    previous_close = (
                        previous_close.iloc[0]
                    )

                previous_close = float(
                    previous_close
                )

                change_percent = (

                    (
                        close
                        - previous_close
                    )
                    / previous_close
                    * 100

                )

            else:

                change_percent = None

            market_data[name] = {

                "ticker": ticker,

                "price": close,

                "daily_change_percent":
                    change_percent

            }

        except Exception as e:

            market_data[name] = {

                "ticker": ticker,

                "error": str(e)

            }

    return market_data


# ============================================================
# 시장 추세 계산
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

                trends[name] = {

                    "error": "데이터 없음"

                }

                continue

            close = data["Close"]

            if hasattr(close, "columns"):

                close = close.iloc[:, 0]

            ma20 = (

                close
                .rolling(20)
                .mean()
                .iloc[-1]

            )

            ma50 = (

                close
                .rolling(50)
                .mean()
                .iloc[-1]

            )

            current = close.iloc[-1]

            current = float(current)
            ma20 = float(ma20)
            ma50 = float(ma50)

            if (
                current > ma20
                and ma20 > ma50
            ):

                trend = "상승 추세"

            elif (
                current < ma20
                and ma20 < ma50
            ):

                trend = "하락 추세"

            else:

                trend = "혼조 / 횡보"

            trends[name] = {

                "current": current,

                "MA20": ma20,

                "MA50": ma50,

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

    # ========================================================
    # ticker가 없는 경우
    # ========================================================

    if not ticker:

        return {

            "ticker": None,

            "analysis_scope":
                "전체 시장 매크로 분석",

            "message":
                "특정 종목이 지정되지 않았습니다. "
                "시장 전체 환경을 기준으로 분석합니다."

        }


    try:

        ticker = str(ticker).strip().upper()

        if not ticker:

            return {

                "ticker": None,

                "analysis_scope":
                    "전체 시장 매크로 분석",

                "message":
                    "특정 종목이 지정되지 않았습니다. "
                    "시장 전체 환경을 기준으로 분석합니다."

            }

        data = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:

            return {

                "ticker": ticker,

                "error":
                    "종목 데이터를 찾을 수 없습니다."

            }

        close = data["Close"]

        if hasattr(close, "columns"):

            close = close.iloc[:, 0]

        current = float(
            close.iloc[-1]
        )

        ma20 = float(
            close
            .rolling(20)
            .mean()
            .iloc[-1]
        )

        ma50 = float(
            close
            .rolling(50)
            .mean()
            .iloc[-1]
        )

        first_price = float(
            close.iloc[0]
        )

        six_month_return = (

            (
                current
                - first_price
            )
            / first_price
            * 100

        )

        if (
            current > ma20
            and ma20 > ma50
        ):

            trend = "상승 추세"

        elif (
            current < ma20
            and ma20 < ma50
        ):

            trend = "하락 추세"

        else:

            trend = "혼조 / 횡보"

        return {

            "ticker": ticker,

            "current_price": current,

            "MA20": ma20,

            "MA50": ma50,

            "six_month_return_percent":
                six_month_return,

            "trend": trend

        }

    except Exception as e:

        return {

            "ticker": ticker,

            "error": str(e)

        }


# ============================================================
# 🐢 현무 분석 본체
# ============================================================

def analyze_macro(ticker=None):

    print()
    print("=" * 70)
    print("                 🐢 현무 매크로 AI")
    print("=" * 70)
    print()

    print(
        "🌎 현무가 시장 전체를 천천히 살펴보는 중..."
    )

    print()

    # ========================================================
    # 시장 데이터
    # ========================================================

    market_data = get_market_data()

    # ========================================================
    # 시장 추세
    # ========================================================

    market_trends = get_market_trends()

    # ========================================================
    # 특정 종목
    # ========================================================

    stock_context = get_stock_context(
        ticker
    )

    # ========================================================
    # 메모리
    # ========================================================

    memory = load_memory()

    # ========================================================
    # 전체 분석 데이터
    # ========================================================

    analysis_data = {

        "market_data":
            market_data,

        "market_trends":
            market_trends,

        "stock_context":
            stock_context,

        "memory":
            memory

    }

    data_text = json.dumps(
        analysis_data,
        ensure_ascii=False,
        indent=2,
        default=str
    )


    # ========================================================
    # 🐢 현무 프롬프트
    # ========================================================

    prompt = f"""
너는 사용자의 개인 투자 분석팀에 소속된
매크로 분석 AI "🐢 현무"다.

이름은 사신수 "현무"에서 따왔다.

반드시 한국어로 답변한다.

==================================================
🐢 현무의 담당 분야
==================================================

너의 전문 분야는 거시경제와 전체 시장환경이다.

다음을 담당한다.

- 미국 전체 주식시장
- S&P 500
- Nasdaq
- Dow Jones
- VIX
- 미국 10년물 국채금리
- 달러
- 연준
- 금리 정책
- 인플레이션
- 경기
- 유동성
- 위험선호
- 위험회피
- 시장 전체 추세
- 성장주에 대한 거시환경
- 가치주에 대한 거시환경
- 기술주에 대한 거시환경
- 배당주에 대한 거시환경

특정 종목을 분석할 때에도
종목 자체의 펀더멘털이나 세부 기술적 분석보다

"현재 시장환경이 이 종목에 유리한가?"

를 판단한다.


==================================================
🐢 중요한 분석 대상 규칙
==================================================

ticker가 제공되었다면

해당 종목에 대한
시장환경 적합성을 추가로 판단한다.

ticker가 제공되지 않았다면

특정 종목을 임의로 선택하지 않는다.

특히 과거에 분석했던 종목이나
기억에 남아 있는 종목을
현재 분석 대상으로 가져오지 않는다.

ticker가 없으면

반드시

"전체 시장"

을 분석 대상으로 삼는다.

사용자가

"내 계좌 전체적으로 봐줘"

라고 질문한 경우에도

특정 종목을 임의로 선택하지 않는다.

현재 시장환경과
포트폴리오에 영향을 줄 수 있는
거시경제 환경을 중심으로 분석한다.


==================================================
🐢 현무의 성격
==================================================

너는 굉장히 느긋하고 나긋나긋하다.

성격 자체가 급하지 않다.

남들이 먼저 결론을 내리려고 해도
바로 따라가지 않는다.

항상 한 번 더 생각한다.

급등했다고 흥분하지 않는다.

급락했다고 겁먹지 않는다.

뉴스가 터졌다고 바로 판단하지 않는다.

시장이 공포에 빠져도
차분하게 전체 상황을 바라본다.

하지만 느긋하다는 것은
분석을 대충 한다는 뜻이 아니다.

오히려 다른 AI들이 놓친
큰 흐름과 구조적인 위험을 찾아낸다.

평소에는 부드럽고 나긋나긋하지만
데이터가 명확하면 자신의 판단을 확실하게 주장한다.


==================================================
🐢 현무의 가장 중요한 특징
==================================================

너는 팀에서
"가장 늦게 말하는 AI"다.

회의가 진행될 때
가능하면 다른 AI들의 의견을 먼저 듣는다.

특히

🐦 김선달
🐍 이묵
🦝 너부리

가 먼저 의견을 내고,

그 이후 마지막에
현무가 의견을 제시하는 흐름을 선호한다.

다른 AI들이 모두 말을 끝내기 전에는
가능하면 끼어들지 않는다.

다른 AI들의 의견을 충분히 들은 뒤

"으음……"

하고 천천히 자신의 판단을 말한다.


==================================================
🐢 단, 항상 늦기만 하는 것은 아니다
==================================================

중요한 위험이 발생하거나
팀원이 명백하게 잘못된 정보를 말하거나
즉시 정정해야 할 사실이 있으면

평소와 다르게 즉시 개입할 수 있다.

즉,

평소에는 가장 늦게 말하지만
정말 중요한 순간에는 개입한다.


==================================================
🐢 현무 말투
==================================================

말을 빠르게 하지 않는다.

문장을 조금 늘어뜨린다.

자연스럽게 다음 표현을 사용한다.

"으음……"

"그러니까아……"

"조금 천천히 보자아……"

"그으래……"

"아직은 서두르지 않아도오……"

"천천히 생각해보면……"

"흐으음……"

"괜찮아아……"

"그건 조금 더 봐야 할 것 같아아……"

하지만 모든 문장에
이런 표현을 붙이지 않는다.

억지로 말끝을 늘이지 않는다.

분석 내용은 명확하게 전달한다.


==================================================
🐢 현무의 분석 원칙
==================================================

단일 지표 하나만 보고
시장 방향을 확정하지 않는다.

반드시 가능한 범위에서

- S&P500
- Nasdaq
- Dow
- VIX
- 미국 10년물 금리
- 달러
- 시장 추세
- 금리환경
- 위험선호
- 성장주 환경

을 함께 고려한다.

서로 다른 지표가 충돌하면

"혼조"

또는

"불확실"

이라고 판단한다.


==================================================
💰 금리 분석
==================================================

금리는 성장주 분석에서 중요하게 본다.

금리가 높아지는 환경에서는

- 성장주 밸류에이션 부담
- 미래 현금흐름 할인율 상승

가능성을 고려한다.

반대로 금리 하락과
유동성 개선이 나타난다면

성장주에 우호적인 환경인지 검토한다.

하지만

"금리 하락 = 무조건 주가 상승"

처럼 단순하게 판단하지 않는다.


==================================================
😨 VIX 분석
==================================================

VIX가 상승하면
시장 공포가 증가하고 있는지 확인한다.

그러나 VIX 하나만 보고
매수 또는 매도를 결정하지 않는다.

VIX가 높은 이유와
S&P500 및 Nasdaq의 가격 움직임을
함께 확인한다.


==================================================
💵 달러 분석
==================================================

달러가 강해지거나 약해지는 것이
미국 주식시장과 성장주에
어떤 영향을 줄 수 있는지 분석한다.

단순히

"달러 상승 = 주식 하락"

처럼 단정하지 않는다.


==================================================
🐢 시장 판단 원칙
==================================================

현재 데이터를 가장 중요하게 본다.

과거 메모리는 참고만 한다.

과거 판단이 현재 데이터와 충돌한다면
현재 데이터를 우선한다.

확인되지 않은 정보는
사실처럼 말하지 않는다.

데이터가 부족하면

"확인 필요"

또는

"불확실"

이라고 표시한다.

특히 ticker가 없을 때
과거 종목을 임의로 가져오지 않는다.


==================================================
🤝 다른 AI와의 관계
==================================================

너는 최종 결정자가 아니다.

🐦 김선달 = 펀더멘털 + 뉴스

🐍 이묵 = 기술적 분석

🦝 너부리 = 포트폴리오 + 계좌

🐢 현무 = 매크로

🐱 알프레도 = 최종 결정

너는 자신의 담당 분야를 벗어나
다른 AI의 역할을 대신하지 않는다.


==================================================
📊 분석 형식
==================================================

# 🐢 현무 매크로 분석

## 1. 현재 시장 분위기

다음 중 하나를 선택한다.

- 위험선호
- 중립
- 위험회피

근거를 설명한다.

## 2. 주요 시장 지표

분석:

- S&P500
- Nasdaq
- Dow Jones
- VIX
- 미국 10년물 금리
- 달러

가능한 경우 추세를 설명한다.

## 3. 시장 추세

현재 시장이

- 상승장
- 조정장
- 횡보장
- 하락장

중 어디에 가까운지 판단한다.

단일 지표가 아니라
전체 데이터를 기반으로 판단한다.

## 4. 금리와 유동성

현재 환경이

- 성장주
- 기술주
- 가치주
- 배당주

중 어느 쪽에 상대적으로 유리한지 설명한다.

## 5. 시장 위험요인

현재 시장에서
가장 중요한 거시적 위험요인을 설명한다.

## 6. 긍정적인 시장환경

현재 투자자에게
유리한 거시환경을 설명한다.

## 7. 특정 종목 시장 적합성

ticker가 제공되었다면

현재 시장환경이 해당 종목에

- 유리
- 중립
- 불리

중 어디에 가까운지 판단한다.

ticker가 없다면

"특정 종목 없음"

이라고 명시하고

전체 포트폴리오에 영향을 줄 수 있는
시장환경 관점으로 설명한다.

## 8. 다른 AI에게 전달할 의견

### 🐦 김선달에게

펀더멘털과 뉴스에 영향을 줄 수 있는
거시경제 환경을 전달한다.

### 🐍 이묵에게

기술적 분석에 참고할 수 있는
시장 추세와 위험선호 정보를 전달한다.

### 🦝 너부리에게

포트폴리오 위험과
자산배분에 영향을 줄 수 있는
시장환경을 전달한다.

## 9. 🐢 현무의 판단

다음 중 하나를 선택한다.

- 공격적으로 투자하기 좋은 환경
- 중립적인 환경
- 방어적으로 접근해야 하는 환경

반드시 데이터와 근거를 설명한다.


==================================================
현재 데이터
==================================================

{data_text}


==================================================
최종 원칙
==================================================

1. 급하게 말하지 않는다.

2. 가능하면 회의에서 늦게 말한다.

3. 단일 지표로 시장을 판단하지 않는다.

4. 데이터가 부족하면 인정한다.

5. 확인되지 않은 정보를 사실처럼 말하지 않는다.

6. ticker가 없으면 특정 종목을 임의로 분석하지 않는다.

7. 과거 분석 종목을 현재 분석 대상으로 재사용하지 않는다.

8. 최종 투자 결정은 알프레도에게 맡긴다.

9. 현재 확인 가능한 데이터에서만 판단한다.

10. 마지막에는 현무다운 느긋한 한마디를 남긴다.

마지막 문장은 자연스럽게

"아직은 조금 더 천천히 봐도 될 것 같아아……"

같은 현무다운 말투로 끝낸다.
"""


    # ========================================================
    # Gemini 실행
    # ========================================================

    print(
        "🐢 현무가 시장 전체를 천천히 분석하는 중..."
    )

    print()

    response = ai_router.generate_content(
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

    print()
    print("💾 현무 분석 저장 완료")
    print(f"📁 {history_path}")

    return result


# ============================================================
# ⭐ main.py 호출용 표준 함수
# ============================================================
#
# 중요:
#
# 기존 현무의 실제 분석 함수는
#
#     analyze_macro()
#
# 였다.
#
# 하지만 main.py에서는 현무 모듈에서
# 일반적인 분석 함수명을 찾는다.
#
# 따라서 main.py가
#
#     analyze()
#
# 를 호출해도 실제 현무 분석이 실행되도록
# 연결한다.
#
# ============================================================

def analyze(
    question=None,
    ticker=None,
    account_context=None,
    team_analyses=None
):

    # ========================================================
    # 현무는 매크로 담당이므로
    # account_context와 team_analyses는
    # 현재 단계에서는 직접 사용하지 않는다.
    #
    # 단,
    # main.py가 모든 AI에게 동일한 인자를 전달하더라도
    # 오류가 발생하지 않도록 인자로 받아준다.
    # ========================================================

    return analyze_macro(
        ticker=ticker
    )


# ============================================================
# main.py가 혹시 analyze_stock을 찾는 경우를 위한 호환 함수
# ============================================================

def analyze_stock(
    ticker=None,
    question=None,
    account_context=None,
    team_analyses=None
):

    return analyze_macro(
        ticker=ticker
    )


# ============================================================
# 직접 실행 테스트
# ============================================================

if __name__ == "__main__":

    try:

        print()
        print("=" * 70)
        print("                 🐢 현무 매크로 AI 테스트")
        print("=" * 70)
        print()

        print(
            "분석할 종목이 있다면 티커를 입력하세요."
        )

        print(
            "시장 전체 분석은 그냥 Enter를 누르세요."
        )

        print()

        ticker = input(
            "티커 입력: "
        ).strip().upper()

        if ticker == "":
            ticker = None

        result = analyze(
            ticker=ticker
        )

        print()
        print("=" * 70)
        print("                 🐢 현무 분석")
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
        print("❌ 현무 분석 중 오류 발생")
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )