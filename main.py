
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
# 실행 순서
#
# 사용자 질문
#      ↓
# main.py
#      ↓
# 토스 계좌정보 수집
#      ↓
# 🐦 김선달  → 펀더멘털 + 뉴스
#      ↓
# 🐍 이묵    → 기술적 분석
#      ↓
# 🦝 너부리  → 포트폴리오 + 계좌
#      ↓
# 🐢 현무    → 거시경제 + 시장환경
#      ↓
# 🐱 알프레도 → 원본 검증 + 교차검증 + 최종 판단
#
# ★ 중요
# main.py는 "회의 진행자"다.
# 각 AI가 자기 담당 영역을 벗어나지 않도록
# 질문 / 분석유형 / 분석종목 / 계좌원본을 명확하게 전달한다.
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
# 회의 데이터 저장
# ============================================================

def save_meeting_context(
    parsed,
    account_data
):

    filename = (
        f"meeting_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f".json"
    )

    filepath = os.path.join(
        HISTORY_DIR,
        filename
    )

    meeting_data = {

        "request": parsed,

        "account_data": account_data,

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
# 티커 후보
# ============================================================

KNOWN_TICKERS = {

    "REKR": "Rekor Systems",

    "ALAB": "Astera Labs",

    "VOO": "Vanguard S&P 500 ETF",

    "TTWO": "Take-Two Interactive",

    "JEPQ":
        "JPMorgan Nasdaq Equity Premium Income ETF",

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
# 티커 추출
# ============================================================

def extract_tickers(
    text
):

    if not text:

        return []

    text_upper = text.upper()

    found = []

    for ticker in KNOWN_TICKERS:

        if ticker in text_upper:

            found.append(
                ticker
            )

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
        "내 포트폴리오",
        "계좌",
        "포트폴리오",
        "보유종목",
        "보유 종목",
        "전체 자산",
        "비중",
        "내 자산",
        "계좌 전체"
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
        "매도",
        "손절",
        "익절"
    ]

    comparison_keywords = [

        "비교",
        "뭐가 나아",
        "뭐가 좋아",
        "둘 중",
        "어느 게",
        "어떤 게"
    ]

    # --------------------------------------------------------
    # 계좌 질문
    # --------------------------------------------------------

    if any(
        keyword in text_lower
        for keyword in portfolio_keywords
    ):

        if tickers:

            return "portfolio_stock"

        return "portfolio"

    # --------------------------------------------------------
    # 시장 질문
    # --------------------------------------------------------

    if any(
        keyword in text_lower
        for keyword in market_keywords
    ):

        return "market"

    # --------------------------------------------------------
    # 종목 비교
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
            tickers[0] if tickers else None,

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
            f"분석 종목   : "
            f"{', '.join(parsed['tickers'])}"
        )

    else:

        print(
            "분석 종목   : 특정 종목 없음"
        )


# ============================================================
# 토스 계좌정보 가져오기
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
# 계좌정보를 공통 원본으로 저장
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
# 분석할 티커 결정
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
# AI 프롬프트 가져오기
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
# ⭐ AI에게 전달할 분석 컨텍스트 생성
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

        analysis_target = (
            ", ".join(tickers)
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
    # 명확한 지침
    # --------------------------------------------------------

    if intent == "portfolio":

        target_instruction = """
사용자는 전체 계좌/포트폴리오를 분석해달라고 요청했다.

특정 종목을 질문한 것이 아니다.

따라서 계좌 원본의 보유종목, 평가금액, 매수금액,
손익, 비중, 현금 등을 중심으로 분석해야 한다.

계좌 원본에 없는 종목을 임의로 분석 대상으로 추가하지 마라.
"""

    elif intent == "portfolio_stock":

        target_instruction = f"""
사용자는 계좌 전체를 보는 동시에
특정 종목 {primary_ticker}에 대해서도 질문했다.

{primary_ticker}을 중심으로 분석하되,
반드시 실제 계좌 내 보유수량/평가금액/비중과 연결해서 판단하라.

계좌 원본에 없는 종목을 임의로 추가하지 마라.
"""

    elif intent in [
        "stock_analysis",
        "stock_decision"
    ]:

        target_instruction = f"""
사용자가 명시한 분석 종목은 {primary_ticker}이다.

이번 분석의 주 분석 대상은 반드시 {primary_ticker}이다.

사용자가 언급하지 않은 다른 종목을
주 분석 대상으로 바꾸지 마라.

다른 종목을 언급할 필요가 있다면
반드시 {primary_ticker}의 판단에 직접 필요한 경우에만
보조적으로 언급하라.
"""

    elif intent == "comparison":

        target_instruction = f"""
사용자가 비교 대상으로 지정한 종목은
{", ".join(tickers)}이다.

비교 대상 외의 종목을 임의로 주 분석 대상으로 추가하지 마라.
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
사용자 질문을 그대로 해석하고,
질문에서 요구하지 않은 종목을 임의로 만들어 분석하지 마라.
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
# ⭐ AI 호출
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
    #
    # ★ 중요
    # 종목이 없는 portfolio/market 질문에서는
    # None을 무조건 넘기지 않는다.
    #
    # 해당 함수가 ticker를 요구하더라도
    # 빈 문자열을 전달하여 None.upper() 오류를 방지한다.
    # --------------------------------------------------------

    if "ticker" in parameters:

        if primary_ticker:

            kwargs["ticker"] = primary_ticker

        else:

            kwargs["ticker"] = ""

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

        kwargs[
            "account_data"
        ] = account_data

    # --------------------------------------------------------
    # portfolio_context
    # --------------------------------------------------------

    if "portfolio_context" in parameters:

        kwargs[
            "portfolio_context"
        ] = account_data

    # --------------------------------------------------------
    # analysis_context
    # --------------------------------------------------------

    if "analysis_context" in parameters:

        kwargs[
            "analysis_context"
        ] = analysis_context

    # --------------------------------------------------------
    # context
    # --------------------------------------------------------

    if "context" in parameters:

        kwargs[
            "context"
        ] = analysis_context

    # --------------------------------------------------------
    # target_ticker
    # --------------------------------------------------------

    if "target_ticker" in parameters:

        kwargs[
            "target_ticker"
        ] = primary_ticker

    # --------------------------------------------------------
    # tickers
    # --------------------------------------------------------

    if "tickers" in parameters:

        kwargs[
            "tickers"
        ] = tickers

    # --------------------------------------------------------
    # 출력
    # --------------------------------------------------------

    print()
    print("=" * 70)

    print(
        f"                 {ai_name} 분석 시작"
    )

    print("=" * 70)

    if primary_ticker:

        print(
            f"🎯 분석 대상: {', '.join(tickers)}"
        )

    else:

        print(
            f"🎯 분석 대상: {analysis_context['analysis_target']}"
        )

    print(
        f"🧠 분석 유형: {intent}"
    )

    # --------------------------------------------------------
    # ★ 재시도
    # --------------------------------------------------------

    last_error = None

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

            last_error = e

            print(
                f"⚠️ {ai_name} 인자 전달 오류"
            )

            print(e)

            # ------------------------------------------------
            # ★ 정말 인자 문제일 때만
            # 인자 없는 함수 호출을 마지막 fallback으로 사용
            # ------------------------------------------------

            if attempt == MAX_AI_RETRIES:

                try:

                    print(
                        f"🔄 {ai_name} 기본 호출 방식으로 재시도"
                    )

                    result = function()

                    return result

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

            last_error = e

            error_text = str(
                e
            ).lower()

            error_name = type(
                e
            ).__name__.lower()

            # ------------------------------------------------
            # Gemini / API 일시적 오류
            # ------------------------------------------------

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

            # ------------------------------------------------
            # 일반 오류
            # ------------------------------------------------

            print(
                f"❌ {ai_name} 분석 중 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            break

    return None


# ============================================================
# 분석 결과 확인
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

# ============================================================
# ⭐ 회의 시작
# ============================================================

def start_meeting(
    parsed,
    modules,
    account_data
):

    ticker = get_primary_ticker(
        parsed
    )

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
            f"🎯 분석 대상: {', '.join(tickers)}"
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
    # 기존 AI 4명 독립 분석
    #
    # ★ 이 부분은 기존과 동일
    # ★ 캐릭터 파일 수정 없음
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
    # 독립 분석 결과 출력
    # ========================================================

    print()
    print("=" * 70)
    print(
        "                 📋 4명 독립 분석 완료"
    )
    print("=" * 70)

    print()

    print(
        f"🐦 김선달 : "
        f"{'완료' if team_results['crow'] else '실패'}"
    )

    print(
        f"🐍 이묵   : "
        f"{'완료' if team_results['snake'] else '실패'}"
    )

    print(
        f"🦝 너부리 : "
        f"{'완료' if team_results['raccoon'] else '실패'}"
    )

    print(
        f"🐢 현무   : "
        f"{'완료' if team_results['turtle'] else '실패'}"
    )

    # ========================================================
    # 3단계
    # ⚔️ 4인 토론
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
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ".json"
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
    #
    # 독립 분석 + 토론 전체를 전달
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
    # 알프레도에게 전달할 전체 회의 자료
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
    # 기존 cat.py의 run_discussion()이 있으면 사용
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
    # run_discussion()이 없을 경우
    #
    # 기존 call_ai()를 이용하되
    # 알프레도에게 회의 내용을 전달할 수 있도록
    # parsed.question을 임시로 확장
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

필요하면 특정 AI의 판단이 틀렸다고 명확하게 말하라.

최종적으로 사용자에게 실제 도움이 되는
하나의 결론을 내려라.

최종 판단은 다음 중 가장 적절한 행동을 선택하라.

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
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ".json"
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
    # 반환
    # ========================================================

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
# 메인 실행
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

    # --------------------------------------------------------
    # AI 모듈 준비
    # --------------------------------------------------------

    print()
    print("🔧 AI 모듈을 불러오는 중...")

    modules = load_ai_modules()

    print()
    print("📋 AI 모듈 상태")

    module_names = {
        "crow": "🐦 김선달",
        "snake": "🐍 이묵",
        "raccoon": "🦝 너부리",
        "turtle": "🐢 현무",
        "cat": "🐱 알프레도"
    }

    for key, name in module_names.items():

        if modules.get(key) is not None:

            print(
                f"  ✅ {name}"
            )

        else:

            print(
                f"  ❌ {name}"
            )

    print()
    print("=" * 70)

    # --------------------------------------------------------
    # 질문 반복
    # --------------------------------------------------------

    while True:

        question = get_user_question()

        if not question:

            print()
            print(
                "⚠️ 질문을 입력해주세요."
            )

            continue

        # ----------------------------------------------------
        # 종료
        # ----------------------------------------------------

        if question.lower() in [
            "exit",
            "quit",
            "종료",
            "나가기"
        ]:

            print()
            print(
                "🏦 AI TRADING TEAM을 종료합니다."
            )

            break

        # ----------------------------------------------------
        # 질문 분석
        # ----------------------------------------------------

        parsed = parse_question(
            question
        )

        show_request(
            parsed
        )

        # ----------------------------------------------------
        # 토스 계좌정보
        # ----------------------------------------------------

        account_data = get_account_data()

        # ----------------------------------------------------
        # 공통 원본 저장
        # ----------------------------------------------------

        save_account_source(
            account_data
        )

        # ----------------------------------------------------
        # 회의 요청 저장
        # ----------------------------------------------------

        save_meeting_context(
            parsed,
            account_data
        )

        # ----------------------------------------------------
        # AI 회의
        # ----------------------------------------------------

        try:

            result = start_meeting(
                parsed,
                modules,
                account_data
            )

        except Exception as e:

            print()
            print("=" * 70)
            print(
                "❌ AI TRADING TEAM 회의 실행 오류"
            )
            print("=" * 70)

            print(
                f"{type(e).__name__}: {e}"
            )

            continue

        # ----------------------------------------------------
        # 최종 결과
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print(
            "                 🐱 최종 분석 결과"
        )
        print("=" * 70)

        print()

        cat_result = result.get(
            "cat_result",
            ""
        )

        if cat_result:

            print(
                cat_result
            )

        else:

            print(
                "⚠️ 알프레도 최종 결과가 없습니다."
            )

        print()
        print("=" * 70)
        print(
            "                 🏦 회의 종료"
        )
        print("=" * 70)

        print()


# ============================================================
# 프로그램 시작점
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
        print("=" * 70)
        print(
            "❌ AI TRADING TEAM 실행 오류"
        )
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )