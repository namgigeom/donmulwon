
import os
import json
import importlib
import inspect
import time
from datetime import datetime


# ============================================================
# 🏦 AI TRADING TEAM
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.join(BASE_DIR, "ai")
HISTORY_DIR = os.path.join(AI_DIR, "analysis_history")
AI_PORTFOLIO_FILE = os.path.join(BASE_DIR, "ai_portfolio.json")

os.makedirs(AI_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

MAX_AI_RETRIES = 3
RETRY_WAIT_SECONDS = 3


# ============================================================
# 종목 / 별칭
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
    "META": "Meta",
}

TICKER_ALIASES = {
    "조비": "JOBY",
    "조비에비에이션": "JOBY",
    "조비 에비에이션": "JOBY",
    "joby aviation": "JOBY",

    "아스테라": "ALAB",
    "아스테라랩스": "ALAB",
    "아스테라 랩스": "ALAB",
    "astera labs": "ALAB",

    "리코": "REKR",
    "리커": "REKR",
    "리코 시스템즈": "REKR",
    "리코르": "REKR",
    "rekor systems": "REKR",

    "브이오오": "VOO",
    "s&p500": "VOO",
    "s&p 500": "VOO",

    "제프큐": "JEPQ",
    "제이이피큐": "JEPQ",

    "테슬라": "TSLA",
    "엔비디아": "NVDA",
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "마소": "MSFT",
    "알파벳": "GOOGL",
    "구글": "GOOGL",
    "아마존": "AMZN",
    "메타": "META",

    "테이크투": "TTWO",
    "테이크 투": "TTWO",
}


# ============================================================
# AI 모듈
# ============================================================

def load_ai_modules():

    modules = {}

    for name in [
        "crow",
        "snake",
        "raccoon",
        "turtle",
        "cat",
    ]:

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
# JSON
# ============================================================

def save_json(path, data):

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
    print("무엇을 분석할까요?")
    print("예시:")
    print("  • REKR 지금 사도 괜찮아?")
    print("  • ALAB 손절해야 돼?")
    print("  • 내 계좌 전체적으로 봐줘")
    print("  • 이번 주 투자금 어디에 넣을까?")
    print("  • 요즘 미국 증시 분위기 어때?")
    print("  • REKR하고 ALAB 중 뭐가 나아?")
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
    text_lower = text.lower()

    found = []

    # 직접 티커
    for ticker in KNOWN_TICKERS:

        if ticker in text_upper:
            found.append(ticker)

    # 한글 / 별칭
    for alias, ticker in TICKER_ALIASES.items():

        if alias.lower() in text_lower:
            found.append(ticker)

    # 중복 제거
    return list(
        dict.fromkeys(found)
    )


# ============================================================
# 질문 의도
# ============================================================

def detect_intent(text, tickers):

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
        "자산 상태",
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
        "fed",
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
        "목표가",
    ]

    comparison_keywords = [
        "비교",
        "뭐가 나아",
        "뭐가 좋아",
        "둘 중",
        "어느 게",
        "어떤 게",
        "어느쪽",
    ]

    # 계좌 + 종목
    if any(
        keyword in text_lower
        for keyword in portfolio_keywords
    ):

        if tickers:
            return "portfolio_stock"

        return "portfolio"

    # 시장
    if any(
        keyword in text_lower
        for keyword in market_keywords
    ):

        return "market"

    # 비교
    if len(tickers) >= 2:
        return "comparison"

    if any(
        keyword in text_lower
        for keyword in comparison_keywords
    ):

        return "comparison"

    # 종목
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

def parse_question(question):

    tickers = extract_tickers(question)

    intent = detect_intent(
        question,
        tickers
    )

    return {

        "question": question,

        "tickers": tickers,

        "intent": intent,

        "primary_ticker":
            tickers[0]
            if tickers
            else None,

        "timestamp":
            datetime.now().isoformat(),
    }


# ============================================================
# 질문 출력
# ============================================================

def show_request(parsed):

    print()
    print("=" * 70)
    print("                        🧠 질문 분석")
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
# 토스 계좌
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
            "status": "계좌정보 조회 실패",
            "error": str(e),
            "account": {},
            "holdings": [],
        }


# ============================================================
# 계좌 원본 저장
# ============================================================

def save_account_source(account_data):

    if save_json(
        AI_PORTFOLIO_FILE,
        account_data
    ):

        print(
            "💾 공통 계좌 원본 저장 완료"
        )

        print(
            f"📁 {AI_PORTFOLIO_FILE}"
        )


# ============================================================
# 회의 컨텍스트
# ============================================================

def save_meeting_context(
    parsed,
    account_data
):

    filepath = os.path.join(
        HISTORY_DIR,
        "meeting_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
    )

    save_json(
        filepath,
        {
            "request": parsed,
            "account_data": account_data,
            "created_at":
                datetime.now().isoformat(),
        }
    )

    print()
    print(
        "💾 회의 컨텍스트 저장 완료"
    )

    print(
        f"📁 {filepath}"
    )


# ============================================================
# 분석 컨텍스트
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

    if tickers:

        analysis_target = ", ".join(
            tickers
        )

    else:

        analysis_target = "특정 종목 없음"

    if intent == "portfolio":

        target_instruction = """
사용자는 전체 계좌/포트폴리오를 분석해달라고 요청했다.

계좌 원본의 보유종목, 평가금액, 매수금액,
손익, 비중, 현금 등을 중심으로 분석하라.

계좌 원본에 없는 종목을 임의로 추가하지 마라.
"""

    elif intent == "portfolio_stock":

        target_instruction = f"""
사용자는 계좌 전체 상태와 함께 다음 종목들을
명시적으로 질문했다.

분석 대상:
{", ".join(tickers)}

계좌 전체 상태를 확인하되,
위 종목 각각을 독립적으로 분석하라.

각 종목에 대해:

- 현재 가격
- 평균 매수가
- 보유 수량
- 평가금액
- 계좌 내 비중
- 현재 손익
- 매도 판단
- 목표 매도가
- 손절 기준

을 계좌 상황과 연결해서 판단하라.

사용자가 명시한 종목 외의 종목을
주 분석 대상으로 추가하지 마라.
"""

    elif intent in [
        "stock_analysis",
        "stock_decision",
    ]:

        target_instruction = f"""
사용자가 명시한 분석 종목:

{", ".join(tickers)}

각 종목을 개별적으로 분석하라.

사용자가 언급하지 않은 종목을
주 분석 대상으로 바꾸지 마라.
"""

    elif intent == "comparison":

        target_instruction = f"""
비교 대상:

{", ".join(tickers)}

모든 종목을 동일한 기준으로 비교하라.
비교 대상 외 종목을 임의로 추가하지 마라.
"""

    elif intent == "market":

        target_instruction = """
미국 증시와 시장환경을 분석하라.

시장지수, 금리, 변동성, 경기,
연준, 성장주/가치주 환경을 중심으로 분석하라.

개별 종목을 임의로 선택하지 마라.
"""

    else:

        target_instruction = """
사용자 질문을 그대로 해석하라.

질문에서 요구하지 않은 종목을
임의로 분석 대상으로 추가하지 마라.
"""

    return {

        "intent": intent,

        "tickers": tickers,

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
            account_data,
    }


# ============================================================
# AI 함수 찾기
# ============================================================

def find_analysis_function(module):

    if module is None:
        return None

    for name in [
        "analyze_stock",
        "analyze",
        "analysis",
        "run_analysis",
        "run_discussion",
    ]:

        function = getattr(
            module,
            name,
            None
        )

        if callable(function):
            return function

    return None


# ============================================================
# 결과 정규화
# ============================================================

def normalize_result(result):

    if result is None:
        return ""

    if isinstance(result, str):
        return result

    try:

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    except Exception:

        return str(result)


# ============================================================
# 단일 AI 호출
# ============================================================

def call_ai_once(
    module,
    ai_name,
    parsed,
    account_data,
    ticker_override=None,
    question_override=None,
):

    if module is None:
        return None

    function = find_analysis_function(
        module
    )

    if function is None:

        print(
            f"❌ {ai_name} 분석 함수를 찾을 수 없습니다."
        )

        return None

    tickers = parsed.get(
        "tickers",
        []
    )

    ticker = (
        ticker_override
        if ticker_override
        else (
            tickers[0]
            if tickers
            else ""
        )
    )

    question = (
        question_override
        if question_override is not None
        else parsed.get(
            "question",
            ""
        )
    )

    analysis_context = build_analysis_context(
        parsed,
        account_data
    )

    # 특정 티커를 분석하는 경우
    if ticker:

        local_context = dict(
            analysis_context
        )

        local_context[
            "current_ticker"
        ] = ticker

    else:

        local_context = analysis_context

    try:

        parameters = inspect.signature(
            function
        ).parameters

    except Exception:

        parameters = {}

    kwargs = {}

    if "ticker" in parameters:
        kwargs["ticker"] = ticker

    if "question" in parameters:
        kwargs["question"] = question

    if "user_question" in parameters:
        kwargs["user_question"] = question

    if "intent" in parameters:
        kwargs["intent"] = parsed.get(
            "intent",
            "general"
        )

    if "parsed" in parameters:

        local_parsed = dict(
            parsed
        )

        if ticker:
            local_parsed[
                "current_ticker"
            ] = ticker

        local_parsed[
            "question"
        ] = question

        kwargs["parsed"] = local_parsed

    if "account_data" in parameters:
        kwargs["account_data"] = account_data

    if "portfolio_context" in parameters:
        kwargs[
            "portfolio_context"
        ] = account_data

    if "analysis_context" in parameters:
        kwargs[
            "analysis_context"
        ] = local_context

    if "context" in parameters:
        kwargs[
            "context"
        ] = local_context

    if "target_ticker" in parameters:
        kwargs[
            "target_ticker"
        ] = ticker

    if "tickers" in parameters:
        kwargs[
            "tickers"
        ] = tickers

    for attempt in range(
        1,
        MAX_AI_RETRIES + 1
    ):

        try:

            result = function(
                **kwargs
            )

            if result is not None:
                return result

            return None

        except TypeError as e:

            if attempt == MAX_AI_RETRIES:

                try:
                    return function()

                except Exception as fallback_error:

                    print(
                        f"❌ {ai_name} 분석 실패: "
                        f"{type(fallback_error).__name__}: "
                        f"{fallback_error}"
                    )

                    return None

            print(
                f"⚠️ {ai_name} 인자 오류 "
                f"({attempt}/{MAX_AI_RETRIES}): {e}"
            )

        except Exception as e:

            error_text = (
                str(e).lower()
            )

            transient = any(
                keyword in error_text
                for keyword in [
                    "503",
                    "429",
                    "unavailable",
                    "resource exhausted",
                    "rate limit",
                    "high demand",
                    "temporarily",
                    "timeout",
                    "deadline",
                ]
            )

            if transient and attempt < MAX_AI_RETRIES:

                print(
                    f"⚠️ {ai_name} 일시적 API 오류 "
                    f"({attempt}/{MAX_AI_RETRIES})"
                )

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

                continue

            print(
                f"❌ {ai_name} 분석 오류: "
                f"{type(e).__name__}: {e}"
            )

            return None

    return None


# ============================================================
# ⭐ 핵심
# 종목이 여러 개면 종목별로 AI 분석
# ============================================================

def call_ai(
    module,
    ai_name,
    parsed,
    account_data,
):

    tickers = parsed.get(
        "tickers",
        []
    )

    intent = parsed.get(
        "intent",
        "general"
    )

    print()
    print("=" * 70)
    print(
        f"                 {ai_name} 분석 시작"
    )
    print("=" * 70)

    print(
        f"🎯 분석 대상: "
        + (
            ", ".join(tickers)
            if tickers
            else "특정 종목 없음"
        )
    )

    print(
        f"🧠 분석 유형: {intent}"
    )

    # --------------------------------------------------------
    # ⭐ portfolio_stock / 여러 종목 질문
    # --------------------------------------------------------
    #
    # JOBY + ALAB처럼 여러 종목이면
    # 하나만 primary_ticker로 보내지 않고
    # 각각 독립 호출한다.
    #
    # 결과는 종목별로 묶어서 반환한다.
    # --------------------------------------------------------

    if (
        len(tickers) >= 2
        and intent in [
            "portfolio_stock",
            "stock_analysis",
            "stock_decision",
            "comparison",
        ]
    ):

        results = {}

        for ticker in tickers:

            print()
            print(
                f"🎯 {ai_name} → {ticker}"
            )

            result = call_ai_once(
                module,
                ai_name,
                parsed,
                account_data,
                ticker_override=ticker,
            )

            results[ticker] = normalize_result(
                result
            )

        return results

    # --------------------------------------------------------
    # 단일 종목
    # --------------------------------------------------------

    result = call_ai_once(
        module,
        ai_name,
        parsed,
        account_data,
    )

    return result


# ============================================================
# 회의 시작
# ============================================================

def start_meeting(
    parsed,
    modules,
    account_data,
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
    print("회의 구성")
    print("🐦 김선달  → 독립 분석")
    print("🐍 이묵    → 독립 분석")
    print("🦝 너부리  → 독립 분석")
    print("🐢 현무    → 독립 분석")
    print("          ↓")
    print("⚔️ 4인 토론")
    print("          ↓")
    print("🐱 알프레도 → 검증 / 최종 판단")

    # ========================================================
    # 1. 독립 분석
    # ========================================================

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("                 1️⃣ 독립 분석")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print()
    print("▶ 🐦 김선달")

    crow_result = call_ai(
        modules["crow"],
        "🐦 김선달",
        parsed,
        account_data,
    )

    print()
    print("▶ 🐍 이묵")

    snake_result = call_ai(
        modules["snake"],
        "🐍 이묵",
        parsed,
        account_data,
    )

    print()
    print("▶ 🦝 너부리")

    raccoon_result = call_ai(
        modules["raccoon"],
        "🦝 너부리",
        parsed,
        account_data,
    )

    print()
    print("▶ 🐢 현무")

    turtle_result = call_ai(
        modules["turtle"],
        "🐢 현무",
        parsed,
        account_data,
    )

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
            ),
    }

    print()
    print("=" * 70)
    print(
        "                 📋 4명 독립 분석 완료"
    )
    print("=" * 70)

    for key, name in [
        ("crow", "🐦 김선달"),
        ("snake", "🐍 이묵"),
        ("raccoon", "🦝 너부리"),
        ("turtle", "🐢 현무"),
    ]:

        print(
            f"{name:<10}: "
            + (
                "완료"
                if team_results[key]
                else "실패"
            )
        )

    # ========================================================
    # 2. 토론
    # ========================================================

    debate_result = None

    try:

        debate_module = importlib.import_module(
            "ai.debate"
        )

        print()
        print("=" * 70)
        print(
            "                 ⚔️ 4인 토론 시작"
        )
        print("=" * 70)

        debate_result = (
            debate_module.run_debate(
                modules=modules,
                parsed=parsed,
                account_data=account_data,
                team_results=team_results,
            )
        )

    except Exception as e:

        print()
        print(
            "❌ 토론 엔진 오류"
        )

        print(
            f"{type(e).__name__}: {e}"
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
                "",
        }

    # ========================================================
    # 3. 회의 저장
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
            datetime.now().isoformat(),
    }

    meeting_path = os.path.join(
        HISTORY_DIR,
        "team_meeting_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
    )

    save_json(
        meeting_path,
        meeting_package
    )

    print()
    print(
        "💾 전체 회의 데이터 저장 완료"
    )

    print(
        f"📁 {meeting_path}"
    )

    # ========================================================
    # 4. 알프레도
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
            debate_result,
    }

    # --------------------------------------------------------
    # run_discussion 사용
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

            cat_result = (
                cat_module.run_discussion(
                    discussion_prompt=json.dumps(
                        cat_context,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    ),

                    team_results=team_results,

                    account_data=account_data,

                    parsed=parsed,
                )
            )

        except Exception as e:

            print()
            print(
                "❌ 알프레도 run_discussion 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

    # --------------------------------------------------------
    # fallback
    # --------------------------------------------------------

    if cat_result is None:

        cat_parsed = dict(
            parsed
        )

        cat_parsed["question"] = f"""
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
    default=str,
)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[토론]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(
    debate_result,
    ensure_ascii=False,
    indent=2,
    default=str,
)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[알프레도 역할]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

너는 이 회의의 팀장이다.

4명의 의견을 무조건 평균내지 마라.

근거가 약한 주장은 지적하고,
사실과 추정을 구분하라.

여러 종목이 있다면
각 종목을 반드시 별도로 판단하라.

특히 사용자가 매도 가격을 요청했다면
각 종목별로:

- 현재 가격
- 평균 매수가
- 실제 변동성
- 기술적 지지/저항
- 기업 상황
- 실적
- 뉴스
- 시장환경
- 위험 대비 기대수익

을 종합해서 판단하라.

가격을 임의의 고정 퍼센트 규칙으로 정하지 마라.

최종 판단은 실제 사용자에게 도움이 되는
명확한 행동으로 내려라.

가능한 판단:

- 매수
- 추가매수
- 보유
- 일부매도
- 전량매도
- 관망
- 비중조절
"""

        try:

            cat_result = call_ai_once(
                cat_module,
                "🐱 알프레도",
                cat_parsed,
                account_data,
            )

        except Exception as e:

            print()
            print(
                "❌ 알프레도 최종판단 오류"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

    # ========================================================
    # 5. 최종 저장
    # ========================================================

    final_path = os.path.join(
        HISTORY_DIR,
        "final_meeting_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
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
            datetime.now().isoformat(),
    }

    save_json(
        final_path,
        final_data
    )

    print()
    print(
        "💾 최종 회의록 저장 완료"
    )

    print(
        f"📁 {final_path}"
    )

    # ========================================================
    # 최종 출력
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
            ),
    }


# ============================================================
# main
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
        + ("✅" if modules["crow"] else "❌")
        + " 🐦 김선달"
    )

    print(
        "  "
        + ("✅" if modules["snake"] else "❌")
        + " 🐍 이묵"
    )

    print(
        "  "
        + ("✅" if modules["raccoon"] else "❌")
        + " 🦝 너부리"
    )

    print(
        "  "
        + ("✅" if modules["turtle"] else "❌")
        + " 🐢 현무"
    )

    print(
        "  "
        + ("✅" if modules["cat"] else "❌")
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
