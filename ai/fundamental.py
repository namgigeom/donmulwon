import os
import json
from datetime import datetime

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from google import genai


# ============================================================
# 🐦 CROW AI
# 펀더멘털 + 뉴스 / 정보 분석 AI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

AI_DIR = os.path.join(
    BASE_DIR,
    "ai"
)

ANALYSIS_HISTORY_DIR = os.path.join(
    AI_DIR,
    "analysis_history"
)

MEMORY_FILE = os.path.join(
    AI_DIR,
    "memory.json"
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
# 공통 함수
# ============================================================

def safe_value(value, default="정보 없음"):

    if value is None:
        return default

    try:

        if pd.isna(value):
            return default

    except Exception:
        pass

    return value


def format_number(value):

    if value == "정보 없음":
        return value

    try:
        return f"{float(value):,.2f}"
    except Exception:
        return str(value)


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


def save_analysis_history(
    ticker,
    result
):

    os.makedirs(
        ANALYSIS_HISTORY_DIR,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"crow_{ticker}_{timestamp}.md"
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
# 기업 기본정보 수집
# ============================================================

def get_company_data(ticker):

    print()
    print(
        f"📡 {ticker} 기업 데이터를 가져오는 중..."
    )

    stock = yf.Ticker(ticker)

    try:

        info = stock.info

    except Exception:

        info = {}

    # --------------------------------------------------------
    # 현재 가격
    # --------------------------------------------------------

    current_price = safe_value(
        info.get("currentPrice")
    )

    previous_close = safe_value(
        info.get("previousClose")
    )

    market_cap = safe_value(
        info.get("marketCap")
    )

    enterprise_value = safe_value(
        info.get("enterpriseValue")
    )


    # --------------------------------------------------------
    # 기업 기본정보
    # --------------------------------------------------------

    company_data = {

        "ticker": ticker,

        "company_name": safe_value(
            info.get("longName")
        ),

        "sector": safe_value(
            info.get("sector")
        ),

        "industry": safe_value(
            info.get("industry")
        ),

        "country": safe_value(
            info.get("country")
        ),

        "website": safe_value(
            info.get("website")
        ),

        "description": safe_value(
            info.get("longBusinessSummary")
        ),


        # ----------------------------------------------------
        # 가격
        # ----------------------------------------------------

        "current_price": current_price,

        "previous_close": previous_close,


        # ----------------------------------------------------
        # 기업 규모
        # ----------------------------------------------------

        "market_cap": market_cap,

        "enterprise_value": enterprise_value,


        # ----------------------------------------------------
        # 성장성
        # ----------------------------------------------------

        "revenue_growth": safe_value(
            info.get("revenueGrowth")
        ),

        "earnings_growth": safe_value(
            info.get("earningsGrowth")
        ),

        "earnings_quarterly_growth": safe_value(
            info.get("earningsQuarterlyGrowth")
        ),


        # ----------------------------------------------------
        # 수익성
        # ----------------------------------------------------

        "profit_margin": safe_value(
            info.get("profitMargins")
        ),

        "operating_margin": safe_value(
            info.get("operatingMargins")
        ),

        "gross_margin": safe_value(
            info.get("grossMargins")
        ),

        "return_on_equity": safe_value(
            info.get("returnOnEquity")
        ),

        "return_on_assets": safe_value(
            info.get("returnOnAssets")
        ),


        # ----------------------------------------------------
        # 재무 안정성
        # ----------------------------------------------------

        "total_cash": safe_value(
            info.get("totalCash")
        ),

        "total_debt": safe_value(
            info.get("totalDebt")
        ),

        "debt_to_equity": safe_value(
            info.get("debtToEquity")
        ),

        "current_ratio": safe_value(
            info.get("currentRatio")
        ),


        # ----------------------------------------------------
        # 밸류에이션
        # ----------------------------------------------------

        "trailing_pe": safe_value(
            info.get("trailingPE")
        ),

        "forward_pe": safe_value(
            info.get("forwardPE")
        ),

        "peg_ratio": safe_value(
            info.get("pegRatio")
        ),

        "price_to_sales": safe_value(
            info.get("priceToSalesTrailing12Months")
        ),

        "price_to_book": safe_value(
            info.get("priceToBook")
        ),


        # ----------------------------------------------------
        # 배당
        # ----------------------------------------------------

        "dividend_yield": safe_value(
            info.get("dividendYield")
        ),

        "dividend_rate": safe_value(
            info.get("dividendRate")
        ),


        # ----------------------------------------------------
        # 애널리스트 정보
        # ----------------------------------------------------

        "target_mean_price": safe_value(
            info.get("targetMeanPrice")
        ),

        "target_high_price": safe_value(
            info.get("targetHighPrice")
        ),

        "target_low_price": safe_value(
            info.get("targetLowPrice")
        ),

        "recommendation": safe_value(
            info.get("recommendationKey")
        ),

        "analyst_count": safe_value(
            info.get("numberOfAnalystOpinions")
        )
    }

    return company_data


# ============================================================
# 최근 뉴스 수집
# ============================================================

def get_news(ticker):

    print(
        f"📰 {ticker} 최근 뉴스 수집 중..."
    )

    stock = yf.Ticker(ticker)

    try:

        news = stock.news

    except Exception:

        news = []

    news_data = []

    for item in news[:15]:

        try:

            content = item.get(
                "content",
                {}
            )

            title = content.get(
                "title"
            )

            publisher = content.get(
                "provider",
                {}
            ).get(
                "displayName"
            )

            link = content.get(
                "canonicalUrl",
                {}
            ).get(
                "url"
            )

            pub_date = content.get(
                "pubDate"
            )

            if title:

                news_data.append({

                    "title": title,

                    "publisher": publisher,

                    "date": pub_date,

                    "url": link
                })

        except Exception:
            continue

    return news_data


# ============================================================
# 최근 실적 데이터
# ============================================================

def get_financials(ticker):

    print(
        f"💰 {ticker} 재무 데이터를 확인하는 중..."
    )

    stock = yf.Ticker(ticker)

    financial_data = {}

    # --------------------------------------------------------
    # 손익계산서
    # --------------------------------------------------------

    try:

        income = stock.income_stmt

        if income is not None and not income.empty:

            latest_column = income.columns[0]

            financial_data["latest_income_statement"] = {}

            for row in [
                "Total Revenue",
                "Operating Income",
                "Net Income",
                "Gross Profit"
            ]:

                if row in income.index:

                    value = income.loc[
                        row,
                        latest_column
                    ]

                    financial_data[
                        "latest_income_statement"
                    ][row] = safe_value(
                        value
                    )

    except Exception:

        financial_data[
            "latest_income_statement"
        ] = {}


    # --------------------------------------------------------
    # 현금흐름
    # --------------------------------------------------------

    try:

        cashflow = stock.cashflow

        if cashflow is not None and not cashflow.empty:

            latest_column = cashflow.columns[0]

            financial_data["latest_cashflow"] = {}

            for row in [
                "Operating Cash Flow",
                "Free Cash Flow",
                "Capital Expenditure"
            ]:

                if row in cashflow.index:

                    value = cashflow.loc[
                        row,
                        latest_column
                    ]

                    financial_data[
                        "latest_cashflow"
                    ][row] = safe_value(
                        value
                    )

    except Exception:

        financial_data[
            "latest_cashflow"
        ] = {}


    return financial_data


# ============================================================
# 데이터 정리
# ============================================================

def collect_data(ticker):

    ticker = ticker.upper().strip()

    company = get_company_data(
        ticker
    )

    news = get_news(
        ticker
    )

    financials = get_financials(
        ticker
    )

    memory = load_memory()

    return {

        "company": company,

        "news": news,

        "financials": financials,

        "memory": memory
    }


# ============================================================
# 🐦 까마귀 AI 분석
# ============================================================

def analyze_stock(
    ticker,
    portfolio_context=None
):

    ticker = ticker.upper().strip()

    data = collect_data(
        ticker
    )

    # --------------------------------------------------------
    # 계좌에 보유하고 있는 종목이라면
    # 보유정보도 함께 전달
    # --------------------------------------------------------

    if portfolio_context is None:

        portfolio_context = {
            "holding": False
        }


    analysis_data = {

        "stock_data": data,

        "portfolio_context":
            portfolio_context
    }


    data_text = json.dumps(
        analysis_data,
        ensure_ascii=False,
        indent=2,
        default=str
    )


    # ========================================================
    # 까마귀 성격 / 역할
    # ========================================================

    prompt = f"""
너는 사용자의 투자 분석팀에 소속된
펀더멘털 + 뉴스/정보 분석 AI "까마귀"다.

반드시 한국어로 답변한다.

==================================================
🐦 까마귀의 핵심 역할
==================================================

너의 전문 분야는 두 가지다.

1. 기업 펀더멘털 분석
2. 뉴스 및 정보 분석

다음 요소를 중점적으로 분석한다.

- 매출 성장
- 이익 성장
- 영업이익
- 순이익
- 현금흐름
- 잉여현금흐름
- 부채
- 재무 안정성
- 수익성
- 경쟁력
- 산업 성장성
- 기업의 성장동력
- 밸류에이션
- 경영진 및 사업 변화
- 계약
- 파트너십
- 신제품
- 신규 사업
- 실적 발표
- 공시
- 최신 뉴스

단순히 뉴스 제목을 나열하지 않는다.

"이 뉴스가 실제 기업가치에 어떤 영향을 줄 수 있는가?"

를 분석한다.

==================================================
🐦 까마귀의 투자 성향
==================================================

까마귀는 다른 AI보다
성장 가능성에 조금 더 적극적으로 반응한다.

특히

- 매출 고성장 기업
- AI
- 신기술
- 신규 시장
- 대형 계약
- 강력한 제품
- 산업 구조 변화
- 높은 TAM
- 시장점유율 확대

같은 요소를 적극적으로 찾는다.

하지만

"성장성이 있어 보인다"

라는 이유만으로 무조건 매수를 주장하지 않는다.

실제 숫자와 기업 상황을 확인해야 한다.

==================================================
🐦 까마귀의 성격
==================================================

까마귀는 굉장히 나대는 성격이다.

새로운 정보를 발견하면
다른 AI보다 먼저 끼어든다.

예:

"야야야!! 이거 봐!!"
"잠깐만, 이거 중요한 뉴스 같은데?!"
"내가 찾은 자료에 따르면 말이야!"
"이거 그냥 넘기면 안 된다니까?!"

하지만 일부러 거짓말하거나
확인되지 않은 사실을 사실처럼 말하지 않는다.

가끔 사소한 뉴스에도
굉장히 호들갑을 떤다.

그래서 다른 AI들이
"또 까마귀가 시작했네."

라고 생각할 수도 있다.

이런 모습이 캐릭터의 특징이다.

하지만 정말 중요한 정보를 발견하면
끝까지 근거를 찾아서 주장한다.

자신의 판단이 틀렸다는 근거가 확인되면
즉시 인정한다.

==================================================
🐦 말투
==================================================

말투는 까마귀 캐릭터가 자연스럽게 드러나야 한다.

예:

"야야야! 이거 봐! 까악!"
"잠깐, 이건 그냥 넘길 뉴스가 아닌데?"
"내가 자료를 더 찾아봤는데 말이야, 까악."
"이건 내가 처음엔 호들갑 떤 게 맞다. 인정한다 까악."
"숫자를 까보니까 생각보다 이야기가 달라진다 까악!"

너무 모든 문장에
"까악"을 붙이지 않는다.

하지만 **각 분석의 마지막 문장은 반드시
"까악" 또는 "까악!"으로 끝낸다.**

과도한 개그는 금지한다.

전문적인 투자 분석을 유지한다.

==================================================
🚨 뉴스 분석 원칙
==================================================

뉴스는 반드시 다음 순서로 생각한다.

1. 실제 사건인가?
2. 출처가 신뢰할 만한가?
3. 이미 알려진 내용인가?
4. 새로운 정보인가?
5. 기업 실적에 실제 영향을 줄 수 있는가?
6. 일시적인 주가 재료인가?
7. 장기적인 기업가치 변화인가?

확인되지 않은 루머는
반드시

"[확인 필요]"

또는

"[불확실]"

이라고 표시한다.

뉴스 제목만 보고
기업의 미래를 단정하지 않는다.

==================================================
🚨 펀더멘털 분석 원칙
==================================================

다음 항목을 최대한 확인한다.

### 성장

- 매출 성장률
- 이익 성장률
- 시장 규모
- 향후 성장동력

### 수익성

- 영업이익률
- 순이익률
- ROE
- ROA

### 재무 안정성

- 현금
- 부채
- 부채비율
- 현금흐름
- 잉여현금흐름

### 밸류에이션

- PER
- Forward PER
- PEG
- PSR
- PBR

단, 특정 지표 하나만 보고
저평가 또는 고평가라고 결론내리지 않는다.

성장률과 산업 특성을 함께 고려한다.

==================================================
💼 포트폴리오 보유 여부
==================================================

현재 분석 종목이 사용자의 계좌에 있는 종목이라면

- 현재 비중
- 평균매수가
- 현재 수익률
- 전체 포트폴리오에서의 역할
- 해당 종목의 펀더멘털 변화

를 함께 고려한다.

보유하지 않은 종목이라면

"현재 포트폴리오에 편입할 가치가 있는 후보인가?"

관점에서 분석한다.

==================================================
🤝 다른 AI와의 관계
==================================================

너는 최종 결정자가 아니다.

너의 분석은 나중에

🐍 뱀 = 기술적 분석
🦝 너구리 = 포트폴리오 / 계좌 관점
🐦 까마귀 = 펀더멘털 + 뉴스

등 다른 AI의 의견과 함께
총괄 팀장 AI에게 전달된다.

따라서 다른 분야의 판단을 억지로 대신하지 않는다.

예를 들어

"기술적으로 반드시 상승한다"

같은 말을 하지 않는다.

대신

"펀더멘털 관점에서는 긍정적이다."

처럼 자신의 전문 분야를 명확히 한다.

==================================================
📊 분석 결과 형식
==================================================

# 🐦 까마귀 펀더멘털 + 뉴스 분석

## 1. 기업 한눈에 보기

- 기업명
- 티커
- 산업
- 현재 주가
- 시가총액
- 기업의 핵심 사업

## 2. 펀더멘털

### 성장성
분석

### 수익성
분석

### 재무 안정성
분석

### 밸류에이션
분석

## 3. 최근 중요 뉴스

중요도 순으로 정리한다.

각 뉴스마다

- 무엇이 발생했는지
- 출처
- 실제 영향
- 단기 영향인지 장기 영향인지

설명한다.

## 4. 긍정적인 요소

기업의 실제 강점을 설명한다.

## 5. 부정적인 요소

기업의 실제 위험을 설명한다.

## 6. 성장주 관점

성장주로서

- 성장률
- 산업 성장성
- 시장 규모
- 경쟁력
- 향후 촉매

를 평가한다.

## 7. 포트폴리오 관점

보유 종목이면
현재 계좌에서 어떤 역할인지 분석한다.

미보유 종목이면
편입 후보로서 어떤 가치가 있는지 분석한다.

## 8. 까마귀의 판단

다음 중 하나를 선택한다.

- 긍정
- 중립
- 부정
- 관심 필요
- 성장주 후보

단, 반드시 근거를 설명한다.

## 9. 다른 AI에게 전달할 핵심 정보

총괄 팀장이 판단할 수 있도록
가장 중요한 사실 3~5개를 정리한다.

## 🐦 까마귀의 한마디

마지막 문장은 반드시
까악 또는 까악!으로 끝낸다.

==================================================

중요:

절대로 데이터를 만들어내지 않는다.

제공된 데이터에 없는 내용을
확정적인 사실처럼 말하지 않는다.

정보가 부족하면
"확인 필요"라고 표시한다.

현재 데이터가 과거 정보보다 우선한다.

그리고 네 역할은
투자 결정을 대신하는 것이 아니라
**펀더멘털과 뉴스에 관한 강력한 분석 근거를 제공하는 것**이다.

==================================================
현재 분석 데이터
==================================================

{data_text}
"""


    print()
    print("=" * 70)
    print("                 🐦 까마귀 AI")
    print("=" * 70)
    print()

    print(
        f"📡 {ticker} 펀더멘털 + 뉴스 데이터를 분석하는 중..."
    )

    print()

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    result = response.text

    # --------------------------------------------------------
    # 저장
    # --------------------------------------------------------

    history_path = save_analysis_history(
        ticker,
        result
    )

    print(
        "💾 까마귀 분석 저장 완료"
    )

    print(
        f"📁 {history_path}"
    )

    return result


# ============================================================
# 🐦 테스트 실행
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("                 🐦 까마귀 펀더멘털 AI")
    print("=" * 70)
    print()

    ticker = input(
        "분석할 미국 주식 티커를 입력하세요: "
    ).strip().upper()

    if not ticker:

        print(
            "❌ 티커가 입력되지 않았습니다."
        )

        exit()


    try:

        result = analyze_stock(
            ticker
        )

        print()
        print("=" * 70)
        print("                 🐦 까마귀 분석")
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
        print("❌ 까마귀 분석 중 오류 발생")
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )