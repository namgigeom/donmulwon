import inspect
import json
import time


# ============================================================
# ⚔️ AI TRADING TEAM DEBATE ENGINE
#
# 중요:
# 이 파일에서는 김선달 / 이묵 / 너부리 / 현무의
# 캐릭터를 새로 정의하지 않는다.
#
# 각 AI의 기존 analyze_stock()을 다시 호출하면서
# 회의 내용을 추가 전달한다.
#
# 따라서 기존 AI 파일에 작성된 말투 / 성격 / 사고방식 /
# 분석 원칙은 그대로 유지된다.
# ============================================================


MAX_DEBATE_RETRIES = 3
RETRY_WAIT_SECONDS = 3


AI_NAMES = {
    "crow": "🐦 김선달",
    "snake": "🐍 이묵",
    "raccoon": "🦝 너부리",
    "turtle": "🐢 현무",
}


# ============================================================
# 공통
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


def find_analysis_function(module):

    if module is None:
        return None

    candidates = [
        "analyze_stock",
        "analyze",
        "analysis",
        "run_analysis",
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
# AI 호출 인자 생성
# ============================================================

def build_kwargs(
    function,
    parsed,
    account_data,
    debate_question
):

    try:

        parameters = inspect.signature(
            function
        ).parameters

    except Exception:

        parameters = {}

    tickers = parsed.get(
        "tickers",
        []
    )

    primary_ticker = (
        tickers[0]
        if tickers
        else ""
    )

    intent = parsed.get(
        "intent",
        "general"
    )

    kwargs = {}

    # --------------------------------------------------------
    # ticker
    # --------------------------------------------------------

    if "ticker" in parameters:

        kwargs["ticker"] = primary_ticker

    # --------------------------------------------------------
    # question
    #
    # 기존 AI가 question을 받는 경우
    # 원래 질문 대신 회의용 질문을 전달한다.
    # 기존 프롬프트는 AI 파일 내부에서 그대로 유지된다.
    # --------------------------------------------------------

    if "question" in parameters:

        kwargs["question"] = debate_question

    elif "user_question" in parameters:

        kwargs["user_question"] = debate_question

    # --------------------------------------------------------
    # intent
    # --------------------------------------------------------

    if "intent" in parameters:

        kwargs["intent"] = intent

    # --------------------------------------------------------
    # parsed
    # --------------------------------------------------------

    if "parsed" in parameters:

        debate_parsed = dict(parsed)

        debate_parsed[
            "question"
        ] = debate_question

        kwargs["parsed"] = debate_parsed

    # --------------------------------------------------------
    # account
    # --------------------------------------------------------

    if "account_data" in parameters:

        kwargs["account_data"] = account_data

    if "portfolio_context" in parameters:

        kwargs[
            "portfolio_context"
        ] = account_data

    # --------------------------------------------------------
    # context
    # --------------------------------------------------------

    if "context" in parameters:

        kwargs["context"] = {
            "question": debate_question,
            "account_data": account_data,
            "intent": intent,
            "tickers": tickers,
        }

    # --------------------------------------------------------
    # analysis_context
    # --------------------------------------------------------

    if "analysis_context" in parameters:

        kwargs["analysis_context"] = {
            "question": debate_question,
            "account_data": account_data,
            "intent": intent,
            "tickers": tickers,
            "primary_ticker": primary_ticker,
        }

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

    return kwargs


# ============================================================
# 기존 AI를 이용한 토론 발언
# ============================================================

def call_existing_ai(
    module,
    ai_name,
    parsed,
    account_data,
    debate_question
):

    if module is None:

        return (
            f"{ai_name}: 모듈을 불러오지 못했습니다."
        )

    function = find_analysis_function(
        module
    )

    if function is None:

        return (
            f"{ai_name}: 기존 분석 함수를 찾지 못했습니다."
        )

    kwargs = build_kwargs(
        function,
        parsed,
        account_data,
        debate_question
    )

    last_error = None

    for attempt in range(
        1,
        MAX_DEBATE_RETRIES + 1
    ):

        try:

            result = function(
                **kwargs
            )

            return normalize_result(
                result
            )

        except TypeError as e:

            last_error = e

            # 인자 문제라면 fallback
            if attempt == MAX_DEBATE_RETRIES:

                try:

                    result = function()

                    return normalize_result(
                        result
                    )

                except Exception as fallback_error:

                    return (
                        f"{ai_name} 토론 발언 실패: "
                        f"{type(fallback_error).__name__}: "
                        f"{fallback_error}"
                    )

        except Exception as e:

            last_error = e

            error_text = (
                str(e).lower()
            )

            transient = any(
                keyword in error_text
                for keyword in [
                    "503",
                    "429",
                    "timeout",
                    "unavailable",
                    "resource exhausted",
                    "rate limit",
                    "temporarily",
                    "deadline"
                ]
            )

            if transient and attempt < MAX_DEBATE_RETRIES:

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

                continue

            return (
                f"{ai_name} 토론 발언 실패: "
                f"{type(e).__name__}: {e}"
            )

    return (
        f"{ai_name} 토론 발언 실패: "
        f"{last_error}"
    )


# ============================================================
# 토론용 질문 생성
# ============================================================

def make_debate_question(
    original_question,
    current_agent,
    transcript,
    round_number
):

    return f"""
[AI TRADING TEAM 공식 회의 - {round_number}라운드]

너는 기존의 너의 역할과 성격을 그대로 유지한다.

중요:
- 기존 캐릭터의 말투를 바꾸지 마라.
- 기존 캐릭터의 성격을 바꾸지 마라.
- 다른 AI의 역할을 대신하지 마라.
- 아래 회의 내용을 참고하여 네 관점에서 의견을 제시하라.
- 근거 없는 주장에는 동의하지 마라.
- 틀린 부분이 있다면 직접 반박하라.
- 좋은 주장이라면 인정해도 된다.
- 억지로 반박할 필요는 없다.
- 사실과 추정을 구분하라.
- 원본 계좌 데이터가 있다면 그것을 우선하라.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[원래 사용자 질문]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{original_question}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[현재 발언자]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{current_agent}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[현재까지의 회의 내용]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{transcript}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[이번 발언에서 해야 할 것]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 다른 팀원의 주장 중 동의하는 부분
2. 다른 팀원의 주장 중 반박할 부분
3. 반박한다면 구체적인 근거
4. 네 기존 담당 관점에서 추가로 확인해야 할 것
5. 현재 시점에서 네 의견이 바뀌었는지 여부
6. 최종적으로 사용자 질문에 대한 네 입장

단순히 다른 사람의 말을 요약하지 말고
실제 회의에서 상대방에게 말하듯이 이야기하라.
"""


# ============================================================
# 토론 시작
# ============================================================

def run_debate(
    modules,
    parsed,
    account_data,
    team_results
):

    question = parsed.get(
        "question",
        ""
    )

    print()
    print("=" * 70)
    print(
        "                 ⚔️ 4인 투자 토론 시작"
    )
    print("=" * 70)

    print()
    print(
        "※ 기존 AI 캐릭터와 프롬프트는 변경하지 않습니다."
    )

    # --------------------------------------------------------
    # 기존 분석 결과
    # --------------------------------------------------------

    transcript_parts = []

    transcript_parts.append(
        "===== 1차 독립 분석 ====="
    )

    for key, name in AI_NAMES.items():

        result = team_results.get(
            key,
            ""
        )

        transcript_parts.append(
            f"\n[{name}]\n{result}"
        )

    transcript = "\n".join(
        transcript_parts
    )

    debate_results = []

    # ========================================================
    # ROUND 1
    # ========================================================

    print()
    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    print(
        "⚔️ ROUND 1 — 서로의 의견에 대한 첫 반박"
    )
    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    for key, name in AI_NAMES.items():

        module = modules.get(
            key
        )

        print()
        print(
            f"▶ {name} 발언 준비..."
        )

        debate_question = make_debate_question(
            question,
            name,
            transcript,
            1
        )

        result = call_existing_ai(
            module,
            name,
            parsed,
            account_data,
            debate_question
        )

        debate_results.append({

            "round": 1,

            "agent": key,

            "name": name,

            "content": result
        })

        transcript += (
            f"\n\n[{name} - ROUND 1]\n"
            f"{result}"
        )

        print(
            f"✅ {name} 발언 완료"
        )

    # ========================================================
    # ROUND 2
    # ========================================================

    print()
    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    print(
        "⚔️ ROUND 2 — 재반박 및 의견 수정"
    )
    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    for key, name in AI_NAMES.items():

        module = modules.get(
            key
        )

        print()
        print(
            f"▶ {name} 재발언 준비..."
        )

        debate_question = make_debate_question(
            question,
            name,
            transcript,
            2
        )

        result = call_existing_ai(
            module,
            name,
            parsed,
            account_data,
            debate_question
        )

        debate_results.append({

            "round": 2,

            "agent": key,

            "name": name,

            "content": result
        })

        transcript += (
            f"\n\n[{name} - ROUND 2]\n"
            f"{result}"
        )

        print(
            f"✅ {name} 재발언 완료"
        )

    # ========================================================
    # 최종 의견 정리
    # ========================================================

    final_positions = {}

    for key, name in AI_NAMES.items():

        agent_rounds = [

            item["content"]

            for item in debate_results

            if item["agent"] == key
        ]

        final_positions[key] = {

            "name": name,

            "round_1":
                agent_rounds[0]
                if len(agent_rounds) > 0
                else "",

            "round_2":
                agent_rounds[1]
                if len(agent_rounds) > 1
                else ""
        }

    print()
    print("=" * 70)
    print(
        "                 ⚔️ 4인 토론 종료"
    )
    print("=" * 70)

    return {

        "original_question":
            question,

        "initial_results":
            team_results,

        "debate_results":
            debate_results,

        "final_positions":
            final_positions,

        "transcript":
            transcript
    }