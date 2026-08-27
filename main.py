import os
import json
import importlib
import inspect
from datetime import datetime

# ============================================================
# 🏦 AI TRADING TEAM
# 통합 회의 시스템 (프롬프트 기반 가상 회의 토론 방식)
#
# 흐름
#
# 사용자 질문
#      ↓
# main.py
#      ↓
# 토스 계좌정보 수집
#      ↓
# ┌──────────────────────────────────────────────┐
# │ 🐦 김선달  → CROW_SYSTEM_PROMPT               │
# │ 🐍 이묵    → SNAKE_SYSTEM_PROMPT              │
# │ 🦝 너부리  → RACCOON_SYSTEM_PROMPT            │
# │ 🐢 현무    → TURTLE_SYSTEM_PROMPT             │
# └──────────────────────────────────────────────┘
#      ↓
# main.py에서 4명 AI 프롬프트 변수 통합 (방법 2)
#      ↓
# 🐱 알프레도 / 메인 LLM에 통합 토론 프롬프트 전달
#      ↓
# 4명 캐릭터 말투/성격 100% 반영된 회의 대화록 + 최종 투자 판단
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

    text_lower = text.lower()

    portfolio_keywords = [

        "내 계좌",
        "내 포트폴리오",
        "계좌",
        "포트폴리오",
        "보유종목",
        "보유 종목",
        "전체 자산",
        "비중"
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
        "vix"
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

    if any(
        keyword in text_lower
        for keyword in portfolio_keywords
    ):

        if tickers:

            return "portfolio_stock"

        return "portfolio"

    if any(
        keyword in text_lower
        for keyword in market_keywords
    ):

        return "market"

    if len(tickers) >= 2:

        return "comparison"

    if any(
        keyword in text_lower
        for keyword in comparison_keywords
    ):

        return "comparison"

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
        
        "run_discussion"  # 가상 회의용 함수 추가
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
# ⭐ [방법 2] 프롬프트 변수 가져오기 (안전 추출 함수)
# 각 AI 파일의 SYSTEM_PROMPT 또는 PROMPT 변수 추출
# ============================================================

def get_ai_prompt(module, default_name):

    if module is None:

        return f"({default_name} 성격 지침 없음)"

    # 변수 이름 후보들 탐색
    for attr in ["SYSTEM_PROMPT", "PROMPT", "CHARACTER_PROMPT", "CROW_SYSTEM_PROMPT", "SNAKE_SYSTEM_PROMPT", "RACCOON_SYSTEM_PROMPT", "TURTLE_SYSTEM_PROMPT"]:

        if hasattr(module, attr):

            return getattr(module, attr)

    return f"({default_name} 관점 분석 및 성격 지침)"


# ============================================================
# AI 분석 함수 호출
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

    ticker = get_primary_ticker(
        parsed
    )

    question = parsed[
        "question"
    ]

    intent = parsed[
        "intent"
    ]

    try:

        signature = inspect.signature(
            function
        )

        parameters = signature.parameters

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

        kwargs["intent"] = intent

    if "parsed" in parameters:

        kwargs["parsed"] = parsed

    if "portfolio_context" in parameters:

        kwargs[
            "portfolio_context"
        ] = account_data

    if "account_data" in parameters:

        kwargs[
            "account_data"
        ] = account_data

    print()
    print(
        "=" * 70
    )

    print(
        f"                 {ai_name} 분석 시작"
    )

    print(
        "=" * 70
    )

    try:

        result = function(
            **kwargs
        )

        return result

    except TypeError as e:

        print(
            f"⚠️ {ai_name} 인자 전달 방식 오류"
        )

        print(e)

        try:

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

        print(
            f"❌ {ai_name} 분석 중 오류"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

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
# ⭐ [방법 2 적용] 회의 시작 및 프롬프트 기반 가상 토론 실행
# ============================================================

def start_meeting(
    parsed,
    modules,
    account_data
):

    ticker = get_primary_ticker(
        parsed
    )

    print()
    print("=" * 70)
    print(
        "                 ⚔️ AI TRADING TEAM 회의"
    )
    print("=" * 70)

    print()

    if ticker:

        print(
            f"🎯 분석 대상: {ticker}"
        )

    else:

        print(
            "🎯 분석 대상: 전체 시장 / 포트폴리오"
        )

    print()

    print(
        "회의 구성"
    )

    print(
        "🐦 김선달  → 펀더멘털 + 뉴스"
    )

    print(
        "🐍 이묵    → 기술적 분석"
    )

    print(
        "🦝 너부리  → 포트폴리오 + 계좌"
    )

    print(
        "🐢 현무    → 거시경제 + 시장환경"
    )

    print(
        "🐱 알프레도 → 원본 검증 + 교차검증 + 회의 주관"
    )

    # --------------------------------------------------------
    # ⭐ 방법 2: 각 AI 모듈에서 프롬프트 변수 불러오기
    # --------------------------------------------------------

    crow_prompt = get_ai_prompt(modules["crow"], "🐦 김선달")
    snake_prompt = get_ai_prompt(modules["snake"], "🐍 이묵")
    raccoon_prompt = get_ai_prompt(modules["raccoon"], "🦝 너부리")
    turtle_prompt = get_ai_prompt(modules["turtle"], "🐢 현무")

    # --------------------------------------------------------
    # ⭐ 4명 프롬프트를 하나로 합친 회의 프롬프트 생성
    # --------------------------------------------------------

    discussion_prompt = f"""
[AI TRADING TEAM 실시간 대화식 투자 회의]

■ 사용자 질문: {parsed['question']}
■ 현재 계좌 상태: {json.dumps(account_data, ensure_ascii=False)}

■ 참석 AI 패널 시스템 프롬프트 및 성격:
1. 🐦 김선달 (펀더멘털/뉴스):
{crow_prompt}

2. 🐍 이묵 (기술적 분석/차트):
{snake_prompt}

3. 🦝 너부리 (포트폴리오/계좌 관리):
{raccoon_prompt}

4. 🐢 현무 (거시경제/시장환경):
{turtle_prompt}

■ 회의 진행 지침:
- 위 4명의 AI 캐릭터 성격, 어조, 분석 시각을 100% 반영하여 실제 회의를 하듯 티키타카 대화록을 작성하세요.
- 단순히 의견을 나열하지 말고, 서로의 의견에 반박하거나 동조하며 활발하게 토론하세요.
- 마지막에는 사회자(🐱 알프레도)가 회의 내용을 요약하고 최종 투자 실행 판단(매수/매도/관망/비중조절)을 내리세요.
"""

    # --------------------------------------------------------
    # 1~4. 4명의 개별 AI 분석도 수행 (기존 기능 유지)
    # --------------------------------------------------------

    crow_result = call_ai(
        modules["crow"],
        "🐦 김선달",
        parsed,
        account_data
    )

    snake_result = call_ai(
        modules["snake"],
        "🐍 이묵",
        parsed,
        account_data
    )

    raccoon_result = call_ai(
        modules["raccoon"],
        "🦝 너부리",
        parsed,
        account_data
    )

    turtle_result = call_ai(
        modules["turtle"],
        "🐢 현무",
        parsed,
        account_data
    )

    team_results = {

        "crow": normalize_result(
            crow_result
        ),

        "snake": normalize_result(
            snake_result
        ),

        "raccoon": normalize_result(
            raccoon_result
        ),

        "turtle": normalize_result(
            turtle_result
        )
    }

    print()
    print("=" * 70)
    print(
        "                 📋 4명 분석 완료"
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

    # --------------------------------------------------------
    # 회의 패키지 데이터 저장
    # --------------------------------------------------------

    meeting_package = {

        "request": parsed,

        "account_data": account_data,

        "team_results": team_results,

        "discussion_prompt": discussion_prompt,

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
        "💾 4명 AI 회의 프롬프트 및 데이터 저장 완료"
    )

    print(
        f"📁 {meeting_package_path}"
    )

    # --------------------------------------------------------
    # 🐱 알프레도 (또는 메인 리더 AI) 호출
    # 통합 회의 프롬프트(discussion_prompt)와 팀원 개별 결과를 전달
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "                 🐱 알프레도 회의 주관 & 검증 시작"
    )
    print("=" * 70)

    cat_module = modules[
        "cat"
    ]

    # cat_module의 함수에 discussion_prompt를 함께 넘겨 가상 회의록을 작성하도록 함
    if cat_module and hasattr(cat_module, "run_discussion"):

        cat_result = cat_module.run_discussion(
            discussion_prompt=discussion_prompt,
            team_results=team_results,
            account_data=account_data,
            parsed=parsed
        )

    else:

        cat_result = call_ai(
            cat_module,
            "🐱 알프레도",
            parsed,
            account_data
        )

    return {

        "team_results":
            team_results,

        "cat_result":
            normalize_result(
                cat_result
            )
    }


# ============================================================
# 메인
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

    # ========================================================
    # AI 모듈 준비
    # ========================================================

    modules = load_ai_modules()

    # ========================================================
    # 질문 반복
    # ========================================================

    while True:

        question = get_user_question()

        if not question:

            print()
            print(
                "⚠️ 질문을 입력해주세요."
            )

            continue

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

        # ====================================================
        # 질문 분석
        # ====================================================

        parsed = parse_question(
            question
        )

        show_request(
            parsed
        )

        # ====================================================
        # 토스 계좌정보
        # ====================================================

        account_data = get_account_data()

        # ====================================================
        # 공통 원본 저장
        # ====================================================

        save_account_source(
            account_data
        )

        # ====================================================
        # 회의 요청 저장
        # ====================================================

        save_meeting_context(
            parsed,
            account_data
        )

        # ====================================================
        # 4 AI → 알프레도 (통합 회의 진행)
        # ====================================================

        result = start_meeting(
            parsed,
            modules,
            account_data
        )

        # ====================================================
        # 최종 결과 출력
        # ====================================================

        print()
        print("=" * 70)
        print(
            "                 🐱 최종 분석 결과 & 회의록"
        )
        print("=" * 70)

        print()

        cat_result = result[
            "cat_result"
        ]

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
        print("=" * 70)
        print(
            "❌ AI TRADING TEAM 실행 오류"
        )
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )