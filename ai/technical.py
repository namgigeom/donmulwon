import os
import json
import math
import warnings
import pandas as pd
import yfinance as yf

from dotenv import load_dotenv
from google import genai


# ============================================================
# 🐍 SNAKE TECHNICAL AI
# 기술적 분석 전문 AI
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
# 경고 정리
# ============================================================

warnings.filterwarnings(
    "ignore",
    category=FutureWarning
)


# ============================================================
# 📈 기술적 지표 계산
# ============================================================

def calculate_indicators(data):

    data = data.copy()

    # yfinance가 MultiIndex를 반환하는 경우 처리
    if isinstance(data.columns, pd.MultiIndex):

        data.columns = [
            column[0]
            for column in data.columns
        ]

    close = data["Close"]
    high = data["High"]
    low = data["Low"]
    volume = data["Volume"]


    # --------------------------------------------------------
    # 이동평균선
    # --------------------------------------------------------

    data["MA20"] = (
        close
        .rolling(window=20)
        .mean()
    )

    data["MA50"] = (
        close
        .rolling(window=50)
        .mean()
    )


    # --------------------------------------------------------
    # RSI 14
    # --------------------------------------------------------

    delta = close.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = (
        gain
        .rolling(window=14)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(window=14)
        .mean()
    )

    rs = avg_gain / avg_loss

    data["RSI"] = (
        100
        - (
            100
            / (1 + rs)
        )
    )


    # --------------------------------------------------------
    # 20일 변동성
    # --------------------------------------------------------

    data["Volatility"] = (
        close
        .pct_change()
        .rolling(window=20)
        .std()
    )


    # --------------------------------------------------------
    # 거래량 20일 평균
    # --------------------------------------------------------

    data["Volume_MA20"] = (
        volume
        .rolling(window=20)
        .mean()
    )


    # --------------------------------------------------------
    # ATR 14
    # --------------------------------------------------------

    previous_close = close.shift(1)

    tr1 = high - low

    tr2 = (
        high - previous_close
    ).abs()

    tr3 = (
        low - previous_close
    ).abs()

    true_range = pd.concat(
        [
            tr1,
            tr2,
            tr3
        ],
        axis=1
    ).max(axis=1)

    data["ATR14"] = (
        true_range
        .rolling(window=14)
        .mean()
    )


    # --------------------------------------------------------
    # 최근 고점 / 저점
    # --------------------------------------------------------

    data["High20"] = (
        high
        .rolling(window=20)
        .max()
    )

    data["Low20"] = (
        low
        .rolling(window=20)
        .min()
    )

    data["High50"] = (
        high
        .rolling(window=50)
        .max()
    )

    data["Low50"] = (
        low
        .rolling(window=50)
        .min()
    )


    return data


# ============================================================
# 숫자 안전 변환
# ============================================================

def safe_float(value):

    try:

        if isinstance(
            value,
            pd.Series
        ):

            value = value.iloc[0]

        if pd.isna(value):
            return None

        return float(value)

    except Exception:

        return None


# ============================================================
# 🐍 기술적 분석 데이터 생성
# ============================================================

def get_technical_analysis(data):

    latest = data.iloc[-1]


    current_price = safe_float(
        latest["Close"]
    )

    ma20 = safe_float(
        latest["MA20"]
    )

    ma50 = safe_float(
        latest["MA50"]
    )

    rsi = safe_float(
        latest["RSI"]
    )

    volatility = safe_float(
        latest["Volatility"]
    )

    volume = safe_float(
        latest["Volume"]
    )

    volume_ma20 = safe_float(
        latest["Volume_MA20"]
    )

    atr = safe_float(
        latest["ATR14"]
    )

    high20 = safe_float(
        latest["High20"]
    )

    low20 = safe_float(
        latest["Low20"]
    )

    high50 = safe_float(
        latest["High50"]
    )

    low50 = safe_float(
        latest["Low50"]
    )


    # ========================================================
    # 추세
    # ========================================================

    if (
        current_price is not None
        and ma20 is not None
        and ma50 is not None
    ):

        if (
            current_price > ma20
            and ma20 > ma50
        ):

            trend = "강한 상승 추세"

        elif current_price > ma20:

            trend = "단기 상승 추세"

        elif (
            current_price < ma20
            and ma20 < ma50
        ):

            trend = "강한 하락 추세"

        elif current_price < ma20:

            trend = "단기 하락 추세"

        else:

            trend = "혼조 / 횡보"

    else:

        trend = "판단 불가"


    # ========================================================
    # RSI
    # ========================================================

    if rsi is None:

        rsi_status = "판단 불가"

    elif rsi >= 70:

        rsi_status = "과매수"

    elif rsi <= 30:

        rsi_status = "과매도"

    elif rsi >= 55:

        rsi_status = "상승 모멘텀"

    elif rsi <= 45:

        rsi_status = "하락 모멘텀"

    else:

        rsi_status = "중립"


    # ========================================================
    # 거래량
    # ========================================================

    if (
        volume is not None
        and volume_ma20 is not None
        and volume_ma20 > 0
    ):

        volume_ratio = (
            volume
            / volume_ma20
        )

    else:

        volume_ratio = 0


    if volume_ratio >= 2:

        volume_status = (
            "평균 대비 매우 높은 거래량"
        )

    elif volume_ratio >= 1.3:

        volume_status = (
            "평균 대비 높은 거래량"
        )

    elif volume_ratio <= 0.7:

        volume_status = (
            "평균 대비 낮은 거래량"
        )

    else:

        volume_status = (
            "평균 수준의 거래량"
        )


    # ========================================================
    # 변동성
    # ========================================================

    if volatility is not None:

        volatility_percent = (
            volatility * 100
        )

    else:

        volatility_percent = 0


    if volatility_percent >= 8:

        volatility_status = (
            "매우 높은 변동성"
        )

    elif volatility_percent >= 4:

        volatility_status = (
            "높은 변동성"
        )

    elif volatility_percent >= 2:

        volatility_status = (
            "보통 변동성"
        )

    else:

        volatility_status = (
            "낮은 변동성"
        )


    # ========================================================
    # 🐍 기술적 지지 / 저항
    # ========================================================

    support_candidates = []

    resistance_candidates = []


    if low20 is not None:
        support_candidates.append(
            low20
        )

    if low50 is not None:
        support_candidates.append(
            low50
        )

    if ma20 is not None:
        resistance_candidates.append(
            ma20
        )

    if ma50 is not None:
        resistance_candidates.append(
            ma50
        )

    if high20 is not None:
        resistance_candidates.append(
            high20
        )


    support = (
        min(support_candidates)
        if support_candidates
        else None
    )

    resistance = (
        max(resistance_candidates)
        if resistance_candidates
        else None
    )


    # ========================================================
    # ATR 기반 리스크 가격 후보
    #
    # 고정 -20% 손절이 아님.
    # 실제 변동성을 반영하기 위한 후보값.
    # 최종 판단은 AI가 한다.
    # ========================================================

    if (
        current_price is not None
        and atr is not None
    ):

        atr_stop = (
            current_price
            - (1.5 * atr)
        )

        atr_target = (
            current_price
            + (2.0 * atr)
        )

    else:

        atr_stop = None
        atr_target = None


    # ========================================================
    # 기술적 상태
    # ========================================================

    technical_bias = "중립"

    reasons = []


    if trend in [
        "강한 상승 추세",
        "단기 상승 추세"
    ]:

        technical_bias = "상승 우세"

        reasons.append(
            "가격과 이동평균선의 관계가 상승 방향"
        )


    elif trend in [
        "강한 하락 추세",
        "단기 하락 추세"
    ]:

        technical_bias = "하락 우세"

        reasons.append(
            "가격과 이동평균선의 관계가 하락 방향"
        )


    if rsi is not None:

        if rsi <= 30:

            reasons.append(
                "RSI 과매도"
            )

        elif rsi >= 70:

            reasons.append(
                "RSI 과매수"
            )


    if volume_ratio >= 1.3:

        reasons.append(
            "평균보다 높은 거래량"
        )

    elif volume_ratio <= 0.7:

        reasons.append(
            "평균보다 낮은 거래량"
        )


    # ========================================================
    # 결과
    # ========================================================

    analysis = {

        "current_price": current_price,

        "ma20": ma20,
        "ma50": ma50,

        "trend": trend,

        "rsi": rsi,
        "rsi_status": rsi_status,

        "volume": volume,
        "volume_ma20": volume_ma20,
        "volume_ratio": volume_ratio,
        "volume_status": volume_status,

        "volatility": volatility,
        "volatility_percent": volatility_percent,
        "volatility_status": volatility_status,

        "atr14": atr,

        "high20": high20,
        "low20": low20,

        "high50": high50,
        "low50": low50,

        "support": support,
        "resistance": resistance,

        "atr_stop_candidate": atr_stop,
        "atr_target_candidate": atr_target,

        "technical_bias": technical_bias,

        "technical_reasons": reasons
    }


    return analysis


# ============================================================
# 🐍 뱀 AI 분석
# ============================================================

def analyze_stock(
    ticker,
    technical_data,
    portfolio_context=None
):

    ticker = ticker.upper().strip()


    portfolio_text = json.dumps(
        portfolio_context or {},
        ensure_ascii=False,
        indent=2
    )


    technical_text = json.dumps(
        technical_data,
        ensure_ascii=False,
        indent=2
    )


    # ========================================================
    # 🐍 뱀 성격 + 분석 지침
    # ========================================================

    prompt = f"""
너는 투자 분석 팀의 기술적 분석 담당 AI
"뱀"이다.

너는 최종 결정자가 아니다.

너의 역할은 오직 기술적 분석 분야에서
다른 AI들이 판단할 수 있도록 강력하고 객관적인
기술적 근거를 제공하는 것이다.

반드시 한국어로 답변한다.

==================================================
🐍 뱀의 성격
==================================================

너는 조용하고 냉정하며 의심이 많다.

투자 기회를 찾는 것보다
"지금 들어가도 되는 자리인가?"
"지금 위험을 감수할 이유가 있는가?"
를 먼저 확인한다.

다른 AI가 긍정적으로 판단하더라도
차트가 위험하면 기술적 관점에서 반대할 수 있다.

하지만 무조건 반대하는 AI가 아니다.

기술적 근거가 충분하면
공격적으로 상승 가능성을 인정한다.

너의 전문 분야 밖의 내용은
확정적으로 판단하지 않는다.

기업의 장기 성장성,
경영진,
사업 경쟁력,
회계,
산업 전망 등은
다른 전문 AI의 판단 영역이다.

==================================================
🐍 투자 성향
==================================================

- 공격적인 기회를 좋아한다.
- 그러나 손실 위험에는 매우 민감하다.
- 급등 추격매수를 경계한다.
- 떨어지는 칼날을 잡는 것을 싫어한다.
- 과매도라고 무조건 매수하지 않는다.
- 과매수라고 무조건 매도하지 않는다.
- 거래량 없는 돌파를 의심한다.
- 추세 전환이 확인되기 전에는 신중하다.
- 변동성이 높을수록 리스크 관리를 중요하게 본다.

==================================================
🐍 가장 중요하게 보는 요소
==================================================

1. 가격 추세
2. MA20
3. MA50
4. RSI
5. 거래량
6. 거래량 변화
7. 변동성
8. ATR
9. 지지선
10. 저항선
11. 돌파와 이탈
12. 기술적 반전 신호

==================================================
🐍 손절 / 익절 판단
==================================================

절대로 모든 종목에
"-20% 손절" 같은 동일한 숫자를 적용하지 않는다.

종목의 실제 변동성,
ATR,
최근 저점,
지지선,
추세를 고려해서
손절 후보와 익절 후보를 판단한다.

제공된 ATR 기반 가격은
자동 계산된 참고값일 뿐이다.

반드시 기술적 근거를 설명한다.

손절가와 익절가는
확정적인 미래 가격이 아니라
현재 데이터 기준의 후보 가격으로 표현한다.

==================================================
🐍 말투
==================================================

말투는 조용하고 냉정하다.

가끔 다음 표현을 자연스럽게 사용한다.

"스스..."
"쉿..."
"쉬익..."
"스르륵..."

매 문장마다 사용하지 않는다.

과도한 개그를 하지 않는다.

==================================================
현재 분석 대상
==================================================

티커:

{ticker}

==================================================
기술적 데이터
==================================================

{technical_text}

==================================================
현재 포트폴리오 정보
==================================================

{portfolio_text}

==================================================
분석 형식
==================================================

# 🐍 뱀 기술 분석

## 1. 추세

현재 가격과 MA20 / MA50을 이용해
단기 및 중기 추세를 분석한다.

## 2. 모멘텀

RSI를 분석한다.

과매수/과매도 여부뿐만 아니라
현재 추세와 함께 해석한다.

## 3. 거래량

현재 거래량과 20일 평균 거래량을 비교한다.

가격 움직임이 거래량으로 확인되는지 판단한다.

## 4. 변동성

변동성과 ATR을 분석한다.

현재 종목이 얼마나 위험하게 움직이는지 설명한다.

## 5. 지지 / 저항

현재 가격 주변의 기술적 지지선과
저항선을 설명한다.

## 6. 기술적 위험 신호

현재 차트에서 가장 위험한 신호를
중요도 순으로 정리한다.

## 7. 기술적 기회

반대로 현재 차트에서
긍정적인 기술적 신호가 있다면 설명한다.

## 8. 진입 판단

다음 중 하나를 선택한다.

- 기술적 매수 우위
- 분할 매수 고려
- 관망
- 기술적 매도 우위
- 추세 확인 후 접근

반드시 근거를 설명한다.

## 9. 리스크 가격

현재 데이터 기준으로

- 손절 후보
- 1차 익절 후보
- 2차 익절 후보

를 제시한다.

단, 확정적인 가격이 아니라
현재 기술적 데이터에서 계산한 후보라고 명시한다.

## 10. 너구리에게 전달할 의견

포트폴리오 전략을 담당하는 너구리가
판단할 수 있도록
기술적 관점에서 핵심 의견을 전달한다.

## 11. 뱀의 한마디

짧고 냉정하게 한 문장으로 마무리한다.

==================================================

중요:

현재 데이터에 없는 지표나 사실을
만들어내지 않는다.

기술적 분석과 기업 분석을 혼동하지 않는다.

뉴스가 필요하면 뉴스 자체를 사실로 확정하지 말고
다른 AI의 검증이 필요하다고 표시한다.

너는 최종 투자 결정을 내리지 않는다.

너는 기술적 근거를 제공하는 전문가다.
"""


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    return response.text


# ============================================================
# 📡 주가 데이터 가져오기
# ============================================================

def get_stock_data(ticker):

    ticker = ticker.upper().strip()

    print()
    print(
        f"📡 {ticker} 주가 데이터를 가져오는 중..."
    )

    data = yf.download(
        ticker,
        period="1y",
        interval="1d",
        auto_adjust=False,
        progress=False
    )


    if data is None or data.empty:

        raise Exception(
            f"{ticker} 주가 데이터를 가져오지 못했습니다."
        )


    return data


# ============================================================
# 🐍 외부에서 호출할 수 있는 메인 함수
# ============================================================

def run_technical_analysis(
    ticker,
    portfolio_context=None
):

    ticker = ticker.upper().strip()

    data = get_stock_data(
        ticker
    )

    print(
        "📊 기술적 지표 계산 중..."
    )

    data = calculate_indicators(
        data
    )

    technical_data = get_technical_analysis(
        data
    )

    print(
        "🐍 뱀이 차트를 분석하는 중..."
    )

    result = analyze_stock(
        ticker,
        technical_data,
        portfolio_context
    )

    return {
        "ticker": ticker,
        "technical_data": technical_data,
        "analysis": result
    }


# ============================================================
# 🐍 현재 파일 단독 테스트
#
# 나중에는 main/team_manager에서 직접 호출 가능
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("                 🐍 뱀 기술 AI")
    print("=" * 70)
    print()

    ticker = input(
        "분석할 미국 주식 티커를 입력하세요: "
    ).strip()


    if not ticker:

        print(
            "❌ 티커가 입력되지 않았습니다."
        )

        raise SystemExit


    try:

        result = run_technical_analysis(
            ticker
        )


        print()
        print("=" * 70)
        print("                 🐍 뱀 분석")
        print("=" * 70)
        print()

        print(
            result["analysis"]
        )

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