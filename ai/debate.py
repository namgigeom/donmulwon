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
        if len(result) > 6000:
            result = result[:6000] + "\n[분석 후반부 생략]"
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

[transcript 말풍선 규칙]
- transcript는 실제 회의처럼 6~12개의 짧은 발언으로 작성한다.
- 한 발언은 반드시 한 줄로 작성한다.
- 형식은 정확히 "🐦 김선달: 발언", "🐍 이묵: 발언", "🦝 너부리: 발언", "🐢 현무: 발언" 중 하나를 사용한다.
- 같은 사람이 연속해서 너무 오래 말하지 않는다.
- 서로의 주장에 실제로 반응하고, 동의/반박/질문/재반박이 섞이게 한다.
- 발언은 말풍선에 들어갈 수 있도록 짧게 쓴다.
- 각 캐릭터의 기존 말투를 유지한다. 김선달은 까악 계열, 이묵은 쉭/쉬익 계열, 너부리는 구리/구리구리/너굴 계열, 현무는 기존의 느긋한 말버릇을 사용한다.
- 전문용어와 숫자는 유지하되 긴 문단은 만들지 않는다.
"""


def _turn_prompt(question, parsed, account_data, team_results, speaker, history, turn_index):
    role_text = {
        "crow": "🐦 김선달 = 펀더멘털/기업/뉴스. 자신감 있고 적극적. 말투에는 기존 까악 계열을 자연스럽게 사용한다.",
        "snake": "🐍 이묵 = 기술적 분석. 냉정하고 짧게 허점을 지적. 말투에는 기존 쉭/쉬익/쉬이익 계열을 자연스럽게 사용한다.",
        "raccoon": "🦝 너부리 = 계좌/포트폴리오. 비중과 실제 위험을 최우선. 말투에는 기존 구리/구리구리/너굴 계열을 자연스럽게 사용한다.",
        "turtle": "🐢 현무 = 거시경제/시장환경. 차분하게 큰 흐름을 판단하고 기존 느긋한 말버릇을 사용한다.",
    }
    compact_team = {}
    for key, value in team_results.items():
        text = normalize_result(value)
        compact_team[key] = text[:4500] + ("\n[후반 생략]" if len(text) > 4500 else "")
    history_text = "\n".join(history[-8:]) if history else "(아직 다른 팀원의 발언이 없다.)"
    return f"""너는 돈물원 투자회의의 {speaker}다.
이번 요청은 '독립 분석을 다시 하는 것'이 아니라 실제 회의에서 앞사람의 말을 듣고 한 번 발언하는 것이다.

[사용자 질문]
{question}

[계좌]
{_compact_json(account_data)}

[독립 분석]
{_compact_json(compact_team)}

[네 역할]
{role_text[speaker]}

[지금까지 실제 회의 발언]
{history_text}

[회의 규칙]
- 이전 발언 중 실제로 중요한 주장 하나에 반응한다.
- 동의, 반박, 질문, 보완 중 하나를 명확히 한다.
- 네 전문 영역에서 숫자/근거를 하나 이상 언급할 수 있으면 언급한다.
- 없는 데이터는 만들지 않는다.
- 길게 설명하지 말고 말풍선 하나에 들어갈 정도의 1~3문장으로 말한다.
- 기존 캐릭터 말투를 자연스럽게 유지한다. 말투를 문장마다 억지로 붙이지 않는다.
- {turn_index}번째 발언이다. 같은 내용을 반복하지 않는다.

JSON 하나만 반환:
{{
  "speaker":"{speaker}",
  "speech":"실제 회의에서 말할 1~3문장",
  "position":"현재 입장 한 줄",
  "response_to":"누구의 어떤 주장에 반응했는지 한 줄"
}}"""


def run_debate(modules, parsed, account_data, team_results):
    question = parsed.get("question", "")
    print()
    print("=" * 70)
    print("                 ⚔️ 실제 멀티턴 투자회의")
    print("=" * 70)
    print("※ 독립 분석 완료 후 4명이 순서대로 서로의 발언을 듣는다.")

    speakers = ["crow", "snake", "raccoon", "turtle"]
    history = []
    turns = []
    positions = {}

    try:
        for turn_index, speaker in enumerate(speakers, 1):
            print(f"\n🎙️ {AI_NAMES[speaker]} 발언 요청")
            prompt = _turn_prompt(
                question=question,
                parsed=parsed,
                account_data=account_data,
                team_results=team_results,
                speaker=speaker,
                history=history,
                turn_index=turn_index,
            )
            config = types.GenerateContentConfig(
                temperature=0.35,
                max_output_tokens=220,
                response_mime_type="application/json",
            )
            result = ai_router.generate_content(prompt=prompt, config=config)
            raw = normalize_result(getattr(result, "text", result)).strip()
            try:
                item = json.loads(raw)
            except Exception:
                item = {"speaker": speaker, "speech": raw, "position": raw[:300], "response_to": ""}

            speech = str(item.get("speech", "")).strip()
            if not speech:
                speech = str(item.get("position", "")).strip()
            if not speech:
                continue

            label = AI_NAMES.get(speaker, speaker)
            line = f"{label}: {speech}"
            history.append(line)
            turns.append({
                "round": turn_index,
                "agent": speaker,
                "name": label,
                "speech": speech,
                "position": str(item.get("position", "")).strip(),
                "response_to": str(item.get("response_to", "")).strip(),
            })
            positions[speaker] = str(item.get("position", "")).strip()
            print("[MEETING_SPEECH] " + line)

        transcript = "\n".join(t["name"] + ": " + t["speech"] for t in turns)
        summary = " → ".join(
            f"{t['name']} {t['position']}" for t in turns if t.get("position")
        )
        print("\n✅ 실제 멀티턴 회의 완료")
        return {
            "original_question": question,
            "initial_results": team_results,
            "debate_results": turns,
            "final_positions": positions,
            "meeting_summary": summary,
            "conflicts": [t["response_to"] for t in turns if t.get("response_to")],
            "consensus": [],
            "important_corrections": [],
            "transcript": transcript,
        }

    except Exception as e:
        print(f"\n❌ 멀티턴 회의 실패: {type(e).__name__}: {e}")
        return {
            "original_question": question,
            "initial_results": team_results,
            "debate_results": turns,
            "final_positions": positions,
            "meeting_summary": "",
            "conflicts": [],
            "consensus": [],
            "important_corrections": [],
            "transcript": "\n".join(t["name"] + ": " + t["speech"] for t in turns),
            "error": str(e),
        }

