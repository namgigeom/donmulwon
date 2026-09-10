
import os
import json
import importlib
import inspect
import time
from datetime import datetime


# ============================================================
# 🏦 AI TRADING TEAM
# 통합 투자 분석 시스템
#
# main.py = 회의 진행자 / 오케스트레이터
#
# 사용자 질문
#      ↓
# 질문 파싱
#      ↓
# 토스 계좌정보
#      ↓
# 🐦 김선달  → 펀더멘털 + 뉴스

# 🐍 이묵    → 기술적 분석

# 🦝 너부리  → 포트폴리오 + 계좌

# 🐢 현무    → 거시경제 + 시장환경
#      ↓
# ⚔️ 4인 토론
#      ↓
# 🐱 알프레도 → 검증 + 최종 판단
# ============================================================


# ============================================================
# 기본 경로
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AI_DIR = os.path.join(
    BASE_DIR,
    "ai"
)

HISTORY_DIR = os.path.join(
    AI_DIR,
    "analysis_history"
)

AI_PORTFOLIO_FILE = os.path.join(
    BASE_DIR,
    "ai_portfolio.json"
)

MARKET_DATA_FILE = os.path.join(
    BASE_DIR,
    "market_data.json"
)

NEWS_DATA_FILE = os.path.join(
    BASE_DIR,
    "news_data.json"
)

os.makedirs(
    AI_DIR,
    exist_ok=True
)

os.makedirs(
    HISTORY_DIR,
    exist_ok=True
)


# ============================================================
# AI 호출 설정
# ============================================================

MAX_AI_RETRIES = 3

RETRY_WAIT_SECONDS = 3


# ============================================================
# 종목 데이터
# ============================================================

KNOWN_TICKERS = {

    "REKR": "Rekor Systems",
    "ALAB": "Astera Labs",
    "VOO": "Vanguard S&P 500 ETF",
    "TTWO": "Take-Two Interactive",
    "JEPQ": "JPMorgan Nasdaq Equity Premium Income ETF",
    "JOBY": "Joby Aviation",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta"
}


# ============================================================
# 한글 / 일반명 → 티커 변환
# ============================================================

TICKER_ALIASES = {

    # Joby
    "조비": "JOBY",
    "조비에비에이션": "JOBY",
    "조비 에비에이션": "JOBY",
    "joby aviation": "JOBY",

    # Astera Labs
    "아스테라": "ALAB",
    "아스테라랩스": "ALAB",
    "아스테라 랩스": "ALAB",
    "astera labs": "ALAB",

    # Rekor
    "리코": "REKR",
    "리커": "REKR",
    "리코 시스템즈": "REKR",
    "리코르": "REKR",
    "rekor systems": "REKR",

    # VOO
    "브이오오": "VOO",
    "s&p500": "VOO",
    "s&p 500": "VOO",

    # JEPQ
    "제프큐": "JEPQ",
    "제이이피큐": "JEPQ",

    # Tesla
    "테슬라": "TSLA",

    # NVIDIA
    "엔비디아": "NVDA",
    "엔비디아": "NVDA",

    # Apple
    "애플": "AAPL",

    # Microsoft
    "마이크로소프트": "MSFT",
    "마소": "MSFT",

    # Alphabet
    "알파벳": "GOOGL",
    "구글": "GOOGL",

    # Amazon
    "아마존": "AMZN",

    # Meta
    "메타": "META",

    # TTWO
    "테이크투": "TTWO",
    "테이크 투": "TTWO",
}


# ============================================================
# 모듈 import
# ============================================================

def load_ai_modules():

    modules = {}

    module_names = [
        "crow",
        "snake",
        "raccoon",
        "turtle",
        "cat"
    ]

    for name in module_names:

        try:

            modules[name] = importlib.import_module(
                f"ai.{name}"
            )

        except Exception as e:

            print(
                f"⚠️ {name}.py 불러오기 실패: {e}"
            )

            modules[name] = None

    return modules


# ============================================================
# JSON 저장
# ============================================================

def save_json(
    path,
    data
):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        return True

    except Exception as e:

        print(
            f"⚠️ JSON 저장 실패: {path}"
        )

        print(e)

        return False





# ============================================================
# 사용자 질문
# ============================================================

def get_user_question():

    print()
    print(
        "무엇을 분석할까요?"
    )

    print(
        "예시:"
    )

    print(
        "  • REKR 지금 사도 괜찮아?"
    )

    print(
        "  • ALAB 손절해야 돼?"
    )

    print(
        "  • 내 계좌 전체적으로 봐줘"
    )

    print(
        "  • 이번 주 투자금 어디에 넣을까?"
    )

    print(
        "  • 요즘 미국 증시 분위기 어때?"
    )

    print(
        "  • REKR하고 ALAB 중 뭐가 나아?"
    )

    print()

    return input(
        "👤 사용자: "
    ).strip()





# ============================================================
# 티커 추출
# ============================================================

def extract_tickers(text):

    if not text:

        return []

    text_upper = text.upper()

    found = []

    # --------------------------------------------------------
    # 1. 직접 티커 검색
    # --------------------------------------------------------

    for ticker in KNOWN_TICKERS:

        if ticker in text_upper:

            found.append(
                ticker
            )

    # --------------------------------------------------------
    # 2. 한글 / 별칭 검색
    # --------------------------------------------------------

    text_lower = text.lower()

    for alias, ticker in TICKER_ALIASES.items():

        if alias.lower() in text_lower:

            found.append(
                ticker
            )

    # --------------------------------------------------------
    # 중복 제거 + 순서 유지
    # --------------------------------------------------------

    return list(
        dict.fromkeys(found)
    )


# ============================================================
# 질문 의도 분석
# ============================================================

def detect_intent(
    text,
    tickers
):

    if not text:

        return "general"

    text_lower = text.lower()

    portfolio_keywords = [

        "내 계좌",
        "내계좌",
        "내 포트폴리오",
        "내포트폴리오",
        "계좌",
        "포트폴리오",
        "보유종목",
        "보유 종목",
        "전체 자산",
        "비중",
        "내 자산",
        "계좌 전체",
        "계좌상태",
        "계좌 상태",
        "자산 상태"
    ]

    market_keywords = [

        "미국 증시",
        "미국시장",
        "미국 시장",
        "시장 분위기",
        "시장 상황",
        "매크로",
        "금리",
        "나스닥",
        "s&p",
        "vix",
        "연준",
        "fed"
    ]

    trading_keywords = [

        "사도",
        "살까",
        "매수",
        "매수해",
        "들어가",
        "진입",
        "팔까",
        "팔아",
        "팔아야",
        "매도",
        "얼마에 팔",
        "얼마에팔",
        "손절",
        "익절",
        "목표가"
    ]

    comparison_keywords = [

        "비교",
        "뭐가 나아",
        "뭐가 좋아",
        "둘 중",
        "어느 게",
        "어떤 게",
        "어느쪽"
    ]

    # --------------------------------------------------------
    # 계좌 + 특정 종목
    # --------------------------------------------------------

    if any(
        keyword in text_lower
        for keyword in portfolio_keywords
    ):

        if tickers:

            return "portfolio_stock"

        return "portfolio"

    # --------------------------------------------------------
    # 시장
    # --------------------------------------------------------

    if any(
        keyword in text_lower
        for keyword in market_keywords
    ):

        return "market"

    # --------------------------------------------------------
    # 종목 2개 이상이면 비교
    # 단, 계좌 질문이면 위에서 portfolio_stock 처리
    # --------------------------------------------------------

    if len(tickers) >= 2:

        return "comparison"

    if any(
        keyword in text_lower
        for keyword in comparison_keywords
    ):

        return "comparison"

    # --------------------------------------------------------
    # 종목 질문
    # --------------------------------------------------------

    if tickers:

        if any(
            keyword in text_lower
            for keyword in trading_keywords
        ):

            return "stock_decision"

        return "stock_analysis"

    return "general"


# ============================================================
# 질문 파싱
# ============================================================

def parse_question(
    question
):

    tickers = extract_tickers(
        question
    )

    intent = detect_intent(
        question,
        tickers
    )

    return {

        "question":
            question,

        "tickers":
            tickers,

        "intent":
            intent,

        "primary_ticker":
            tickers[0]
            if tickers
            else None,

        "timestamp":
            datetime.now().isoformat()
    }


# ============================================================
# 질문 출력
# ============================================================

def show_request(
    parsed
):

    print()
    print("=" * 70)
    print(
        "                        🧠 질문 분석"
    )
    print("=" * 70)

    print(
        f"사용자 질문 : {parsed['question']}"
    )

    print(
        f"분석 유형   : {parsed['intent']}"
    )

    if parsed["tickers"]:

        print(
            "분석 종목   : "
            + ", ".join(
                parsed["tickers"]
            )
        )

    else:

        print(
            "분석 종목   : 특정 종목 없음"
        )


# ============================================================
# 토스 계좌정보
# ============================================================

def get_account_data():

    print()
    print(
        "🏦 토스증권 계좌정보를 확인하는 중..."
    )

    try:

        toss_api = importlib.import_module(
            "toss_api"
        )

        account_data = (
            toss_api.get_account_data()
        )

        if not account_data:

            raise Exception(
                "토스 API에서 계좌정보가 비어 있습니다."
            )

        print(
            "✅ 실제 토스 계좌정보 확보 완료"
        )

        return account_data

    except Exception as e:

        print()
        print(
            "❌ 토스 계좌정보를 가져오지 못했습니다."
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        return {

            "status":
                "계좌정보 조회 실패",

            "error":
                str(e),

            "account":
                {},

            "holdings":
                []
        }


# ============================================================
# 계좌정보 원본 저장
# ============================================================

def save_account_source(
    account_data
):

    success = save_json(
        AI_PORTFOLIO_FILE,
        account_data
    )

    if success:

        print(
            "💾 공통 계좌 원본 저장 완료"
        )

        print(
            f"📁 {AI_PORTFOLIO_FILE}"
        )

    return success


# ============================================================
# 회의 컨텍스트 저장
# ============================================================

def save_meeting_context(
    parsed,
    account_data
):

    filename = (
        "meeting_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
    )

    filepath = os.path.join(
        HISTORY_DIR,
        filename
    )

    meeting_data = {

        "request":
            parsed,

        "account_data":
            account_data,

        "created_at":
            datetime.now().isoformat()
    }

    save_json(
        filepath,
        meeting_data
    )

    print()
    print(
        "💾 회의 컨텍스트 저장 완료"
    )

    print(
        f"📁 {filepath}"
    )


# ============================================================
# 분석할 대표 티커
# ============================================================

def get_primary_ticker(
    parsed
):

    tickers = parsed.get(
        "tickers",
        []
    )

    if tickers:

        return tickers[0]

    return None


# ============================================================
# AI 함수 찾기
# ============================================================

def find_analysis_function(
    module
):

    if module is None:

        return None

    candidates = [

        "analyze_stock",

        "analyze",

        "analysis",

        "run_analysis",

        "run_discussion"
    ]

    for name in candidates:

        function = getattr(
            module,
            name,
            None
        )

        if callable(function):

            return function

    return None


# ============================================================
# AI 프롬프트
# ============================================================

def get_ai_prompt(
    module,
    default_name
):

    if module is None:

        return f"({default_name} 모듈 없음)"

    candidates = [

        "SYSTEM_PROMPT",

        "PROMPT",

        "CHARACTER_PROMPT",

        "CROW_SYSTEM_PROMPT",

        "SNAKE_SYSTEM_PROMPT",

        "RACCOON_SYSTEM_PROMPT",

        "TURTLE_SYSTEM_PROMPT"
    ]

    for attr in candidates:

        if hasattr(
            module,
            attr
        ):

            value = getattr(
                module,
                attr
            )

            if value is not None:

                return str(
                    value
                )

    return (
        f"({default_name} "
        f"관점 분석 및 성격 지침)"
    )


# ============================================================
# AI 분석 컨텍스트
# ============================================================

def build_analysis_context(
    parsed,
    account_data
):

    intent = parsed.get(
        "intent",
        "general"
    )

    tickers = parsed.get(
        "tickers",
        []
    )

    primary_ticker = (
        tickers[0]
        if tickers
        else None
    )

    # --------------------------------------------------------
    # 분석 대상
    # --------------------------------------------------------

    if tickers:

        analysis_target = ", ".join(
            tickers
        )

    elif intent in [
        "portfolio",
        "market",
        "general"
    ]:

        analysis_target = (
            "특정 종목 없음"
        )

    else:

        analysis_target = (
            "특정 종목 없음"
        )

    # --------------------------------------------------------
    # 대상 지침
    # --------------------------------------------------------

    if intent == "portfolio":

        target_instruction = """
사용자는 전체 계좌/포트폴리오를 분석해달라고 요청했다.

특정 종목을 질문한 것이 아니다.

계좌 원본의 보유종목, 평가금액, 매수금액,
손익, 비중, 현금 등을 중심으로 분석하라.

계좌 원본에 없는 종목을 임의로 분석 대상으로 추가하지 마라.
"""

    elif intent == "portfolio_stock":

        target_instruction = f"""
사용자는 계좌 전체 상태와 함께 다음 종목을 명시적으로 질문했다.

분석 대상:
{", ".join(tickers)}

계좌 전체의 상태를 확인하되,
위 종목 각각에 대해 독립적으로 판단하라.

특히 각 종목의:
- 현재 가격
- 평균 매수가
- 보유 수량
- 평가금액
- 계좌 내 비중
- 현재 손익
- 매도 판단
- 목표 매도가
- 손절 기준

을 계좌 상황과 연결해서 분석하라.

사용자가 명시한 종목 외의 종목을
주 분석 대상으로 임의 추가하지 마라.
"""

    elif intent in [
        "stock_analysis",
        "stock_decision"
    ]:

        target_instruction = f"""
사용자가 명시한 분석 종목은 다음과 같다.

{", ".join(tickers)}

이번 분석의 주 분석 대상은 반드시 위 종목들이다.

각 종목을 개별적으로 분석하라.

사용자가 언급하지 않은 다른 종목을
주 분석 대상으로 바꾸지 마라.


"""

    elif intent == "comparison":

        target_instruction = f"""
사용자가 비교 대상으로 지정한 종목은 다음과 같다.

{", ".join(tickers)}

각 종목을 동일한 기준으로 비교하라.

비교 대상 외의 종목을 임의로
주 분석 대상으로 추가하지 마라.
"""

    elif intent == "market":

        target_instruction = """
사용자는 미국 증시/시장환경/매크로 분석을 요청했다.

개별 종목 하나를 임의로 선택해서 분석하지 마라.

시장지수, 금리, 변동성, 경기, 연준,
성장주/가치주 환경 등을 중심으로 분석하라.
"""

    else:

        target_instruction = """
사용자 질문을 그대로 해석하라.

질문에서 요구하지 않은 종목을
임의로 만들어 분석하지 마라.
"""

    return {

        "intent":
            intent,

        "tickers":
            tickers,

        "primary_ticker":
            primary_ticker,

        "analysis_target":
            analysis_target,

        "target_instruction":
            target_instruction,

        "question":
            parsed.get(
                "question",
                ""
            ),

        "account_data":
            account_data
    }


# ============================================================
# AI 호출
# ============================================================

def call_ai(
    module,
    ai_name,
    parsed,
    account_data
):

    if module is None:

        print(
            f"❌ {ai_name} 모듈이 없습니다."
        )

        return None

    function = find_analysis_function(
        module
    )

    if function is None:

        print(
            f"❌ {ai_name}에서 분석 함수를 찾을 수 없습니다."
        )

        return None

    question = parsed.get(
        "question",
        ""
    )

    intent = parsed.get(
        "intent",
        "general"
    )

    tickers = parsed.get(
        "tickers",
        []
    )

    primary_ticker = (
        tickers[0]
        if tickers
        else None
    )

    analysis_context = build_analysis_context(
        parsed,
        account_data
    )

    # --------------------------------------------------------
    # 함수 인자 확인
    # --------------------------------------------------------

    try:

        signature = inspect.signature(
            function
        )

        parameters = signature.parameters

    except Exception:

        parameters = {}

    kwargs = {}

    # --------------------------------------------------------
    # ticker


    # --------------------------------------------------------

    if "ticker" in parameters:

        kwargs["ticker"] = (
            primary_ticker
            if primary_ticker
            else ""
        )

    # --------------------------------------------------------
    # question
    # --------------------------------------------------------

    if "question" in parameters:

        kwargs["question"] = question

    if "user_question" in parameters:

        kwargs["user_question"] = question

    # --------------------------------------------------------
    # intent
    # --------------------------------------------------------

    if "intent" in parameters:

        kwargs["intent"] = intent

    # --------------------------------------------------------
    # parsed
    # --------------------------------------------------------

    if "parsed" in parameters:

        kwargs["parsed"] = parsed

    # --------------------------------------------------------
    # account_data
    # --------------------------------------------------------

    if "account_data" in parameters:

        kwargs["account_data"] = account_data

    # --------------------------------------------------------
    # portfolio_context
    # --------------------------------------------------------

    if "portfolio_context" in parameters:

        kwargs["portfolio_context"] = account_data

    # --------------------------------------------------------
    # analysis_context
    # --------------------------------------------------------

    if "analysis_context" in parameters:

        kwargs["analysis_context"] = analysis_context

    # --------------------------------------------------------
    # context
    # --------------------------------------------------------

    if "context" in parameters:

        kwargs["context"] = analysis_context

    # --------------------------------------------------------
    # target_ticker
    # --------------------------------------------------------

    if "target_ticker" in parameters:

        kwargs["target_ticker"] = primary_ticker

    # --------------------------------------------------------
    # tickers
    # --------------------------------------------------------

    if "tickers" in parameters:

        kwargs["tickers"] = tickers

    # --------------------------------------------------------
    # 출력
    # --------------------------------------------------------

    print()
    print("=" * 70)

    print(
        f"                 {ai_name} 분석 시작"
    )

    print("=" * 70)

    if tickers:

        print(
            "🎯 분석 대상: "
            + ", ".join(tickers)
        )

    else:

        print(
            "🎯 분석 대상: "
            + analysis_context[
                "analysis_target"
            ]
        )

    print(
        f"🧠 분석 유형: {intent}"
    )

    # --------------------------------------------------------
    # 재시도
    # --------------------------------------------------------



    for attempt in range(
        1,
        MAX_AI_RETRIES + 1
    ):

        try:

            if attempt > 1:

                print(
                    f"🔄 {ai_name} 재시도 "
                    f"{attempt}/{MAX_AI_RETRIES}"
                )

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

            result = function(
                **kwargs
            )

            if result is not None:

                return result

            print(
                f"⚠️ {ai_name} 분석 결과가 비어 있습니다."
            )

            return None

        except TypeError as e:



            print(
                f"⚠️ {ai_name} 인자 전달 오류"
            )

            print(e)



            if attempt == MAX_AI_RETRIES:

                try:

                    print(
                        f"🔄 {ai_name} 기본 호출 방식으로 재시도"
                    )

                    return function()

                except Exception as retry_error:

                    print(
                        f"❌ {ai_name} 분석 실패"
                    )

                    print(
                        f"{type(retry_error).__name__}: "
                        f"{retry_error}"
                    )

                    return None

        except Exception as e:



            error_text = str(
                e
            ).lower()

            error_name = type(
                e
            ).__name__.lower()



            transient_error = any(
                keyword in (
                    error_text
                    + " "
                    + error_name
                )
                for keyword in [
                    "503",
                    "unavailable",
                    "429",
                    "resource exhausted",
                    "rate limit",
                    "high demand",
                    "temporarily",
                    "timeout",
                    "deadline"
                ]
            )

            if transient_error:

                print(
                    f"⚠️ {ai_name} 일시적 API 오류 "
                    f"({attempt}/{MAX_AI_RETRIES})"
                )

                print(
                    f"{type(e).__name__}: {e}"
                )

                if attempt < MAX_AI_RETRIES:

                    continue



            print(
                f"❌ {ai_name} 분석 중 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            break

    return None


# ============================================================
# 결과 정규화
# ============================================================

def normalize_result(
    result
):

    if result is None:

        return ""

    if isinstance(
        result,
        str
    ):

        return result

    try:

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    except Exception:

        return str(
            result
        )




# ============================================================
# ⭐ 회의 시작
# ============================================================

def start_meeting(
    parsed,
    modules,
    account_data
):



    tickers = parsed.get(
        "tickers",
        []
    )

    intent = parsed.get(
        "intent",
        "general"
    )

    question = parsed.get(
        "question",
        ""
    )

    analysis_context = build_analysis_context(
        parsed,
        account_data
    )

    print()
    print("=" * 70)

    print(
        "                 ⚔️ AI TRADING TEAM 회의"
    )

    print("=" * 70)

    print()

    if tickers:

        print(
            "🎯 분석 대상: "
            + ", ".join(tickers)
        )

    else:

        print(
            "🎯 분석 대상: 전체 시장 / 포트폴리오"
        )

    print(
        f"🧠 분석 유형: {intent}"
    )

    print()

    print(
        "회의 구성"
    )

    print(
        "🐦 김선달  → 독립 분석"
    )

    print(
        "🐍 이묵    → 독립 분석"
    )

    print(
        "🦝 너부리  → 독립 분석"
    )

    print(
        "🐢 현무    → 독립 분석"
    )

    print(
        "          ↓"
    )

    print(
        "⚔️ 4인 토론 → 서로 반박 / 재반박"
    )

    print(
        "          ↓"
    )

    print(
        "🐱 알프레도 → 회의 주관 / 검증 / 최종 판단"
    )

    # ========================================================
    # 1단계
    # 독립 분석
    # ========================================================

    print()
    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    print(
        "                 1️⃣ 독립 분석"
    )

    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    print()
    print(
        "▶ 🐦 김선달"
    )

    crow_result = call_ai(
        modules["crow"],
        "🐦 김선달",
        parsed,
        account_data
    )

    print()
    print(
        "▶ 🐍 이묵"
    )

    snake_result = call_ai(
        modules["snake"],
        "🐍 이묵",
        parsed,
        account_data
    )

    print()
    print(
        "▶ 🦝 너부리"
    )

    raccoon_result = call_ai(
        modules["raccoon"],
        "🦝 너부리",
        parsed,
        account_data
    )

    print()
    print(
        "▶ 🐢 현무"
    )

    turtle_result = call_ai(
        modules["turtle"],
        "🐢 현무",
        parsed,
        account_data
    )

    # ========================================================
    # 2단계
    # 결과 정규화
    # ========================================================

    team_results = {

        "crow":
            normalize_result(
                crow_result
            ),

        "snake":
            normalize_result(
                snake_result
            ),

        "raccoon":
            normalize_result(
                raccoon_result
            ),

        "turtle":
            normalize_result(
                turtle_result
            )
    }

    # ========================================================
    # 독립 분석 결과
    # ========================================================

    print()
    print("=" * 70)

    print(
        "                 📋 4명 독립 분석 완료"
    )

    print("=" * 70)

    print()

    print(
        "🐦 김선달 : "
        + (
            "완료"
            if team_results["crow"]
            else "실패"
        )
    )

    print(
        "🐍 이묵   : "
        + (
            "완료"
            if team_results["snake"]
            else "실패"
        )
    )

    print(
        "🦝 너부리 : "
        + (
            "완료"
            if team_results["raccoon"]
            else "실패"
        )
    )

    print(
        "🐢 현무   : "
        + (
            "완료"
            if team_results["turtle"]
            else "실패"
        )
    )

    # ========================================================
    # 3단계
    # 4인 토론
    # ========================================================

    debate_result = None

    try:

        debate_module = importlib.import_module(
            "ai.debate"
        )

        print()
        print(
            "=" * 70
        )

        print(
            "                 ⚔️ 4인 토론 시작"
        )

        print(
            "=" * 70
        )

        debate_result = debate_module.run_debate(
            modules=modules,
            parsed=parsed,
            account_data=account_data,
            team_results=team_results
        )

    except Exception as e:

        print()
        print(
            "❌ 토론 엔진 오류"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        print(
            "⚠️ 독립 분석 결과를 기반으로 알프레도에게 전달합니다."
        )

        debate_result = {

            "original_question":
                question,

            "initial_results":
                team_results,

            "debate_results":
                [],

            "final_positions":
                {},

            "transcript":
                ""
        }

    # ========================================================
    # 4단계
    # 회의 패키지 저장
    # ========================================================

    meeting_package = {

        "request":
            parsed,

        "analysis_context":
            analysis_context,

        "account_data":
            account_data,

        "team_results":
            team_results,

        "debate":
            debate_result,

        "timestamp":
            datetime.now().isoformat()
    }

    meeting_package_path = os.path.join(
        HISTORY_DIR,
        (
            "team_meeting_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".json"
        )
    )

    save_json(
        meeting_package_path,
        meeting_package
    )

    print()
    print(
        "💾 전체 회의 데이터 저장 완료"
    )

    print(
        f"📁 {meeting_package_path}"
    )

    # ========================================================
    # 5단계
    # 🐱 알프레도

    # ========================================================

    print()
    print("=" * 70)

    print(
        "                 🐱 알프레도 최종 검증"
    )

    print("=" * 70)

    cat_module = modules.get(
        "cat"
    )

    cat_result = None

    # --------------------------------------------------------
    # 전체 회의 자료
    # --------------------------------------------------------

    cat_context = {

        "user_question":
            question,

        "parsed":
            parsed,

        "analysis_context":
            analysis_context,

        "account_data":
            account_data,

        "initial_team_results":
            team_results,

        "debate":
            debate_result
    }

    # --------------------------------------------------------
    # run_discussion
    # --------------------------------------------------------

    if (
        cat_module
        and hasattr(
            cat_module,
            "run_discussion"
        )
        and callable(
            getattr(
                cat_module,
                "run_discussion"
            )
        )
    ):

        try:

            cat_result = cat_module.run_discussion(
                discussion_prompt=json.dumps(
                    cat_context,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                ),

                team_results=team_results,

                account_data=account_data,

                parsed=parsed
            )

        except Exception as e:

            print()
            print(
                "❌ 알프레도 run_discussion 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            cat_result = None

    # --------------------------------------------------------
    # fallback
    # --------------------------------------------------------

    if cat_result is None:

        try:

            cat_parsed = dict(
                parsed
            )

            cat_parsed[
                "question"
            ] = f"""
[알프레도 최종판단 요청]

원래 사용자 질문:
{question}

사용자가 명시한 분석 종목:
{", ".join(tickers) if tickers else "없음"}

아래는 4명의 독립 분석과 토론 전체 내용이다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[독립 분석]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(
    team_results,
    ensure_ascii=False,
    indent=2,
    default=str
)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[토론 전체]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(
    debate_result,
    ensure_ascii=False,
    indent=2,
    default=str
)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[알프레도 역할]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

너는 이 회의의 팀장이다.

4명의 의견을 무조건 평균내지 마라.

잘한 주장은 인정하고,
근거가 약한 주장은 지적하고,
서로 충돌하는 주장은 원본 데이터와 사실관계를
기준으로 검증하라.

특정 종목이 여러 개라면 각각 별도로 판단하라.

특히 사용자가 매도 가격을 요청했다면
현재 가격, 실제 변동성, 기술적 지지/저항,
기업 상황, 실적, 뉴스, 시장환경을 종합하여
근거 있는 가격 구간을 제시하라.

가격을 임의의 고정 퍼센트 규칙으로 정하지 마라.

최종적으로 사용자에게 실제 도움이 되는
명확한 결론을 내려라.

가능한 최종 판단:

- 매수
- 추가매수
- 보유
- 일부매도
- 전량매도
- 관망
- 비중조절

단순히 4명의 의견을 요약하지 말고
팀장으로서 최종 결정을 내려라.
"""

            cat_result = call_ai(
                cat_module,
                "🐱 알프레도",
                cat_parsed,
                account_data
            )

        except Exception as e:

            print()
            print(
                "❌ 알프레도 최종판단 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            cat_result = None

    # ========================================================
    # 최종 저장
    # ========================================================

    final_result_path = os.path.join(
        HISTORY_DIR,
        (
            "final_meeting_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".json"
        )
    )

    final_data = {

        "request":
            parsed,

        "account_data":
            account_data,

        "team_results":
            team_results,

        "debate":
            debate_result,

        "alfredo":
            normalize_result(
                cat_result
            ),

        "timestamp":
            datetime.now().isoformat()
    }

    save_json(
        final_result_path,
        final_data
    )

    print()
    print(
        "💾 최종 회의록 저장 완료"
    )

    print(
        f"📁 {final_result_path}"
    )

    # ========================================================
    # 최종 결과 출력
    # ========================================================

    print()
    print("=" * 70)

    print(
        "                 🐱 최종 분석 결과"
    )

    print("=" * 70)

    print()

    if cat_result:

        print(
            normalize_result(
                cat_result
            )
        )

    else:

        print(
            "❌ 알프레도 최종 결과가 없습니다."
        )

    print()
    print("=" * 70)

    print(
        "                 🏦 회의 종료"
    )

    print("=" * 70)

    return {

        "team_results":
            team_results,

        "debate_result":
            debate_result,

        "cat_result":
            normalize_result(
                cat_result
            )
    }


# ============================================================
# 프로그램 시작
# ============================================================

def main():

    print()
    print("=" * 70)

    print(
        "                 🏦 AI TRADING TEAM"
    )

    print(
        "                 통합 투자 분석 시스템"
    )

    print("=" * 70)



    print()
    print(
        "🔧 AI 모듈을 불러오는 중..."
    )

    modules = load_ai_modules()

    print()
    print(
        "📋 AI 모듈 상태"
    )

    print(
        "  "
        + (
            "✅"
            if modules["crow"]
            else "❌"
        )
        + " 🐦 김선달"
    )

    print(
        "  "
        + (
            "✅"
            if modules["snake"]
            else "❌"
        )
        + " 🐍 이묵"
    )

    print(
        "  "
        + (
            "✅"
            if modules["raccoon"]
            else "❌"
        )
        + " 🦝 너부리"
    )

    print(
        "  "
        + (
            "✅"
            if modules["turtle"]
            else "❌"
        )
        + " 🐢 현무"
    )

    print(
        "  "
        + (
            "✅"
            if modules["cat"]
            else "❌"
        )
        + " 🐱 알프레도"
    )

    print()
    print("=" * 70)



    while True:

        question = get_user_question()

        if not question:



            print(
                "⚠️ 질문을 입력해주세요."
            )

            continue



        parsed = parse_question(
            question
        )

        show_request(
            parsed
        )



        account_data = get_account_data()



        save_account_source(
            account_data
        )



        save_meeting_context(
            parsed,
            account_data
        )

        start_meeting(
            parsed,
            modules,
            account_data
        )




# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print(
            "⚠️ 사용자가 프로그램을 종료했습니다."
        )

    except Exception as e:

        print()

        print(
            "❌ 프로그램 실행 중 치명적 오류"
        )


        print(
            f"{type(e).__name__}: {e}"
        )