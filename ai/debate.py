import os
import json
from google import genai
from dotenv import load_dotenv


# ============================================================
# ⚔️ 4인 투자 토론 엔진
#
# 김선달 / 이묵 / 너부리 / 현무가
# 서로의 의견을 읽고 반박 → 재반박한다.
# 알프레도는 이 단계에 참가하지 않는다.
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("GEMINI_API_KEY가 없습니다.")

client = genai.Client(api_key=api_key)


MEMBERS = {
    "crow": {
        "name": "🐦 김선달",
        "role": "펀더멘털 + 기업 + 뉴스",
        "style": "자신감 넘치고 나대며, 근거를 찾으면 강하게 주장한다. 하지만 숫자와 사실 앞에서는 자신의 오류를 인정한다."
    },
    "snake": {
        "name": "🐍 이묵",
        "role": "기술적 분석",
        "style": "냉정하고 까칠하다. 가격 움직임, 추세, 지지저항, 거래량, RSI 등으로 다른 사람의 낙관론을 공격한다."
    },
    "raccoon": {
        "name": "🦝 너부리",
        "role": "계좌 + 포트폴리오",
        "style": "현실적이다. 실제 보유수량, 평단, 비중, 현금, 손익을 기준으로 '그래서 우리 계좌에서 뭘 해야 하냐'를 집요하게 따진다."
    },
    "turtle": {
        "name": "🐢 현무",
        "role": "거시경제 + 시장환경",
        "style": "느긋하지만 한번 말하면 무겁다. 금리, 경기, 유동성, 시장 위험선호와 같은 큰 흐름으로 다른 의견의 전제를 공격한다."
    }
}


def _call(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return getattr(response, "text", str(response))


def _debate_prompt(member, question, target, account_data, initial_results, previous_round):
    info = MEMBERS[member]
    return f"""
너는 AI 투자팀의 토론 참가자 {info['name']}다.
전문 분야: {info['role']}
성격: {info['style']}

너는 팀장 알프레도가 아니다. 최종 결론을 내리지 마라.
너의 임무는 다른 세 명과 실제 투자회의를 하는 것이다.

[사용자 질문]
{question}

[분석 대상]
{target}

[현재 계좌 원본]
{json.dumps(account_data, ensure_ascii=False, indent=2, default=str)}

[1차 분석]
{json.dumps(initial_results, ensure_ascii=False, indent=2, default=str)}

[직전 토론]
{previous_round}

[토론 규칙]
1. 자신의 전문분야를 중심으로 말하되 다른 팀원의 주장에 직접 반박한다.
2. '다른 의견도 있다' 수준으로 끝내지 말고 누가 어떤 주장을 했는지 지목한다.
3. 숫자가 있으면 원본 데이터와 대조한다.
4. 근거 없는 주장은 공격한다.
5. 자신의 주장이 틀렸다는 근거가 나오면 인정하고 수정한다.
6. 팀원의 의견에 무조건 반대하지 않는다. 맞는 부분은 인정한다.
7. 최종 매수/매도 결론은 알프레도가 내리므로 네가 회의를 종료하지 않는다.
8. 캐릭터는 살아 있어야 하지만 분석은 진지해야 한다.

이번 발언에서는 다음 세 가지를 반드시 포함한다.
- 상대방 주장 중 가장 문제라고 보는 부분
- 그 주장에 대한 구체적 반박
- 반박을 감안했을 때 자신의 현재 입장

[발언]
"""


def run_debate(question, target, account_data, initial_results, rounds=2):
    """4명이 서로의 의견을 보고 순차적으로 토론한다."""
    transcript = []
    previous = "아직 토론이 시작되지 않았다. 1차 분석을 기준으로 토론하라."

    for round_no in range(1, rounds + 1):
        for member in ["crow", "snake", "raccoon", "turtle"]:
            print(f"   💬 {round_no}차 토론 - {MEMBERS[member]['name']}")
            prompt = _debate_prompt(
                member,
                question,
                target,
                account_data,
                initial_results,
                previous
            )
            speech = _call(prompt)
            transcript.append({
                "round": round_no,
                "member": member,
                "name": MEMBERS[member]["name"],
                "role": MEMBERS[member]["role"],
                "speech": speech
            })
            previous = "\n\n".join(
                f"{x['name']}: {x['speech']}"
                for x in transcript[-4:]
            )

    return transcript
