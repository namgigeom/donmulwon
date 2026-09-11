import json

from ai import ai_router


# ============================================================
# ⚔️ AI TRADING TEAM DEBATE ENGINE
#
# 기존 구조의 문제:
#   4명 × ROUND 1 + 4명 × ROUND 2
#   → 같은 AI를 다시 호출하면서 데이터도 재수집
#
# 변경 구조:
#   4명 독립 분석 결과
#          ↓
#   통합 토론 AI 1회
#
# 중요:
# 각 AI의 기존 캐릭터/전문 분야는 독립 분석 단계에서 유지한다.
# 토론 단계에서는 이미 생성된 분석 결과만 전달하며,
# 전문 AI를 다시 호출하지 않는다.
# ============================================================

AI_NAMES = {
    "crow": "🐦 김선달",
    "snake": "🐍 이묵",
    "raccoon": "🦝 너부리",
    "turtle": "🐢 현무",
}


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
            default=str,
        )
    except Exception:
        return str(result)


def build_debate_prompt(
    question,
    parsed,
    account_data,
    team_results,
):
    """
    이미 완료된 4명의 분석만 사용해서 한 번에 회의를 진행한다.

    다시 각 전문 AI의 analyze_stock()을 호출하지 않는다.
    """

    formatted_team = []

    for key, name in AI_NAMES.items():
        result = normalize_result(
            team_results.get(key, "")
        )

        formatted_team.append(
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{result}"
        )

    team_text = "\n\n".join(formatted_team)

    account_text = json.dumps(
        account_data,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    parsed_text = json.dumps(
        parsed,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
너는 🏦 돈물원 AI 투자팀의 공식 회의 진행 AI다.

이번 단계에서는 새로운 시장 데이터를 수집하거나
전문 AI를 다시 호출하지 않는다.

이미 완료된 네 명의 독립 분석 결과를 바탕으로
한 번의 통합 회의를 진행한다.

==================================================
[사용자 질문]
==================================================
{question}

==================================================
[질문 정보]
==================================================
{parsed_text}

==================================================
[현재 계좌 원본]
==================================================
{account_text}

==================================================
[4명 독립 분석]
==================================================
{team_text}

==================================================
[회의 규칙]
==================================================

네 명의 기존 캐릭터와 전문 영역을 절대로 섞지 마라.

🐦 김선달
- 펀더멘털 + 기업 + 뉴스
- 자신감 있고 말빨이 좋다.
- 새로운 정보를 발견하면 적극적으로 끼어든다.
- 자연스러운 캐릭터 말투를 사용한다.

🐍 이묵
- 기술적 분석
- 냉정하고 짧게 말한다.
- 차트의 허점을 지적한다.

🦝 너부리
- 실제 계좌 + 포트폴리오
- 현실적인 관점에서 비중과 위험을 본다.
- 계좌에 손해가 될 만한 부분은 강하게 지적한다.

🐢 현무
- 거시경제 + 시장환경
- 느긋하고 차분하다.
- 급한 결론을 경계하며 큰 흐름을 본다.

중요:
- 이미 주어진 독립 분석을 우선 사용한다.
- 없는 숫자나 뉴스를 만들어내지 않는다.
- 네 명이 모두 같은 의견이라고 가정하지 않는다.
- 의견이 충돌하면 실제 근거가 더 강한 쪽을 구분한다.
- 억지로 반박하지 않는다.
- 잘못된 주장에는 명확하게 문제를 지적한다.
- 계좌 데이터가 있다면 현재 계좌 원본을 최우선으로 본다.

==================================================
[회의 진행 방식]
==================================================

기존 ROUND 1 / ROUND 2처럼 각 AI를 다시 호출하지 않는다.

한 번의 통합 회의 안에서 다음을 수행한다.

1. 네 명의 핵심 주장 파악
2. 서로 충돌하는 주장 확인
3. 근거가 약한 주장 제거
4. 서로의 주장에 대한 짧은 반박/인정
5. 의견이 바뀌어야 하는 부분 판단
6. 사용자 질문에 직접 연결

각 캐릭터가 실제 회의에서 말하는 것처럼 작성한다.

예:

🐦 김선달
"잠깐만! 이 숫자는 그냥 넘기면 안 돼."

🐍 이묵
"펀더멘털은 인정. 하지만 차트는 아직 약세다."

🦝 너부리
"둘 다 맞는데 계좌 비중을 봐야 해."

🐢 현무
"조금 천천히 보죠. 현재 시장환경까지 고려하면..."

이런 식으로 자연스럽게 의견 충돌이 드러나야 한다.

단, 모든 문장에 캐릭터 유행어를 붙이지 않는다.

==================================================
[토론 결과 형식]
==================================================

다음 JSON 형식으로 반환한다.

{{
  "meeting_summary": "회의에서 가장 중요한 충돌과 합의",
  "agent_positions": {{
    "crow": "김선달의 최종 입장",
    "snake": "이묵의 최종 입장",
    "raccoon": "너부리의 최종 입장",
    "turtle": "현무의 최종 입장"
  }},
  "conflicts": [
    "핵심 의견 충돌 1",
    "핵심 의견 충돌 2"
  ],
  "consensus": [
    "네 명이 공통적으로 인정하는 핵심 근거"
  ],
  "important_corrections": [
    "사실관계 또는 논리에서 바로잡은 내용"
  ],
  "transcript": "짧은 실제 회의 형식의 대화"
}}

JSON 외의 설명은 추가하지 않는다.
"""


def run_debate(
    modules,
    parsed,
    account_data,
    team_results,
):
    """
    4명의 독립 분석을 한 번만 수행한 뒤,
    그 결과를 하나의 AI 호출로 토론한다.
    """

    question = parsed.get("question", "")

    print()
    print("=" * 70)
    print("                 ⚔️ 4인 통합 투자 토론")
    print("=" * 70)
    print()
    print("※ 독립 분석을 다시 호출하지 않습니다.")
    print("※ 기존 2라운드 재반박 구조를 제거했습니다.")

    prompt = build_debate_prompt(
        question=question,
        parsed=parsed,
        account_data=account_data,
        team_results=team_results,
    )

    try:
        result = ai_router.generate_content(
            prompt=prompt,
            config=None,
        )

        text = normalize_result(
            getattr(result, "text", result)
        )

        print()
        print("✅ 4인 통합 토론 완료")

        try:
            parsed_result = json.loads(text)
        except Exception:
            parsed_result = {
                "meeting_summary": text,
                "agent_positions": {},
                "conflicts": [],
                "consensus": [],
                "important_corrections": [],
                "transcript": text,
            }

        return {
            "original_question": question,
            "initial_results": team_results,
            "debate_results": [
                {
                    "round": 1,
                    "agent": "team",
                    "name": "⚔️ 통합 회의",
                    "content": text,
                }
            ],
            "final_positions": parsed_result.get(
                "agent_positions", {}
            ),
            "meeting_summary": parsed_result.get(
                "meeting_summary", ""
            ),
            "conflicts": parsed_result.get(
                "conflicts", []
            ),
            "consensus": parsed_result.get(
                "consensus", []
            ),
            "important_corrections": parsed_result.get(
                "important_corrections", []
            ),
            "transcript": parsed_result.get(
                "transcript", text
            ),
        }

    except Exception as e:
        print()
        print("❌ 통합 토론 실패")
        print(
            f"{type(e).__name__}: {e}"
        )

        return {
            "original_question": question,
            "initial_results": team_results,
            "debate_results": [],
            "final_positions": {},
            "meeting_summary": "",
            "conflicts": [],
            "consensus": [],
            "important_corrections": [],
            "transcript": "",
            "error": str(e),
        }
