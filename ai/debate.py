import json

from google.genai import types
from ai import ai_router

# ============================================================
# ⚔️ AI TRADING TEAM DEBATE ENGINE
#
# 4명 독립 분석은 batch_engine에서 병렬 처리한다.
# 여기서는 이미 나온 결과만 가지고 "한 번" 회의한다.
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
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
    except Exception:
        return str(result)


def _compact_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str)


def build_debate_prompt(question, parsed, account_data, team_results):
    """토론용 입력을 최소화하면서 4명의 원래 분석과 계좌 원본은 보존한다."""
    formatted_team = []
    for key, name in AI_NAMES.items():
        result = normalize_result(team_results.get(key, ""))
        # 비정상적으로 긴 로그가 토론 입력을 폭증시키는 것을 방지한다.
        if len(result) > 12000:
            result = result[:12000] + "\n[분석 후반부 생략]"
        formatted_team.append(f"[{name}]\n{result}")

    team_text = "\n\n".join(formatted_team)
    account_text = _compact_json(account_data)
    parsed_text = _compact_json(parsed)

    return f"""너는 🏦 돈물원 AI 투자팀의 공식 회의 진행 AI다.
이미 완료된 4명의 독립 분석을 가지고 실제 투자회의를 진행한다.
새로운 시장 데이터를 수집하거나 전문 AI를 다시 호출하지 마라.

[사용자 질문]
{question}

[질문 정보]
{parsed_text}

[현재 계좌 원본]
{account_text}

[4명 독립 분석]
{team_text}

[전문 역할]
🐦 김선달 = 펀더멘털/기업/뉴스. 자신감 있고 적극적.
🐍 이묵 = 기술적 분석. 냉정하고 짧게 허점을 지적.
🦝 너부리 = 계좌/포트폴리오. 비중과 실제 위험을 최우선.
🐢 현무 = 거시경제/시장환경. 차분하게 큰 흐름을 판단.

[회의 원칙]
- 각자의 전문 영역을 유지한다.
- 의견이 다르면 실제 근거를 비교한다.
- 억지 반박을 만들지 않는다.
- 없는 숫자/뉴스를 만들지 않는다.
- 현재 계좌 원본과 제공된 분석을 우선한다.
- 다수결이 아니라 근거의 질로 판단한다.
- 사용자의 질문에 직접 필요한 쟁점만 토론한다.

[진행]
1. 네 명의 핵심 주장 확인
2. 실제 충돌 1~3개만 선정
3. 각 충돌에 대해 짧게 반박/인정
4. 잘못되거나 근거 약한 주장 제거
5. 최종적으로 각 팀원의 입장과 합의/불일치를 정리

실제 회의처럼 자연스럽게 대화하되 장황하게 반복하지 마라.

[반환 형식]
JSON 하나만 반환:
{{
  "meeting_summary":"핵심 충돌과 합의",
  "agent_positions":{{"crow":"최종 입장","snake":"최종 입장","raccoon":"최종 입장","turtle":"최종 입장"}},
  "conflicts":["핵심 충돌"],
  "consensus":["공통 근거"],
  "important_corrections":["사실/논리 교정"],
  "transcript":"짧은 실제 회의 대화"
}}
"""


def run_debate(modules, parsed, account_data, team_results):
    question = parsed.get("question", "")

    print()
    print("=" * 70)
    print("                 ⚔️ 4인 통합 투자 토론")
    print("=" * 70)
    print("※ 독립 분석 재호출 없음 / 통합 토론 1회")

    prompt = build_debate_prompt(
        question=question,
        parsed=parsed,
        account_data=account_data,
        team_results=team_results,
    )

    try:
        # 토론은 사고의 질을 유지하면서 불필요하게 긴 출력은 제한한다.
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=900,
            response_mime_type="application/json",
        )
        result = ai_router.generate_content(
            prompt=prompt,
            config=config,
        )

        text = normalize_result(getattr(result, "text", result))
        print("\n✅ 4인 통합 토론 완료")

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
            "debate_results": [{
                "round": 1,
                "agent": "team",
                "name": "⚔️ 통합 회의",
                "content": text,
            }],
            "final_positions": parsed_result.get("agent_positions", {}),
            "meeting_summary": parsed_result.get("meeting_summary", ""),
            "conflicts": parsed_result.get("conflicts", []),
            "consensus": parsed_result.get("consensus", []),
            "important_corrections": parsed_result.get("important_corrections", []),
            "transcript": parsed_result.get("transcript", text),
        }

    except Exception as e:
        print(f"\n❌ 통합 토론 실패: {type(e).__name__}: {e}")
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
