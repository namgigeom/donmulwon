import os
import json
import importlib
import time
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.join(BASE_DIR, "ai")
HISTORY_DIR = os.path.join(AI_DIR, "analysis_history")
AI_PORTFOLIO_FILE = os.path.join(BASE_DIR, "ai_portfolio.json")
os.makedirs(AI_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

KNOWN_TICKERS = {
    "REKR": "Rekor Systems", "ALAB": "Astera Labs", "VOO": "Vanguard S&P 500 ETF",
    "TTWO": "Take-Two Interactive", "JEPQ": "JPMorgan Nasdaq Equity Premium Income ETF",
    "JOBY": "Joby Aviation", "TSLA": "Tesla", "NVDA": "NVIDIA", "AAPL": "Apple",
    "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon", "META": "Meta",
}
TICKER_ALIASES = {
    "조비": "JOBY", "조비에비에이션": "JOBY", "조비 에비에이션": "JOBY", "joby aviation": "JOBY",
    "아스테라": "ALAB", "아스테라랩스": "ALAB", "아스테라 랩스": "ALAB", "astera labs": "ALAB",
    "리코": "REKR", "리커": "REKR", "리코 시스템즈": "REKR", "리코르": "REKR", "rekor systems": "REKR",
    "브이오오": "VOO", "s&p500": "VOO", "s&p 500": "VOO", "제프큐": "JEPQ", "제이이피큐": "JEPQ",
    "테슬라": "TSLA", "엔비디아": "NVDA", "애플": "AAPL", "마이크로소프트": "MSFT", "마소": "MSFT",
    "알파벳": "GOOGL", "구글": "GOOGL", "아마존": "AMZN", "메타": "META", "테이크투": "TTWO", "테이크 투": "TTWO",
}


def load_ai_modules():
    modules = {}
    for name in ["crow", "snake", "raccoon", "turtle", "cat"]:
        try:
            modules[name] = importlib.import_module(f"ai.{name}")
        except Exception as e:
            print(f"⚠️ {name}.py 불러오기 실패: {e}")
            modules[name] = None
    return modules


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        print(f"⚠️ JSON 저장 실패: {path} / {e}")
        return False


def normalize_result(result):
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


def extract_tickers(text):
    if not text:
        return []
    upper, lower = text.upper(), text.lower()
    found = [t for t in KNOWN_TICKERS if t in upper]
    found += [t for alias, t in TICKER_ALIASES.items() if alias.lower() in lower]
    return list(dict.fromkeys(found))


def detect_intent(text, tickers):
    t = (text or "").lower()
    portfolio = ["내 계좌", "내계좌", "내 포트폴리오", "내포트폴리오", "계좌", "포트폴리오", "보유종목", "보유 종목", "전체 자산", "비중", "내 자산", "계좌 전체", "계좌 상태", "계좌상태"]
    market = ["미국 증시", "미국시장", "미국 시장", "시장 분위기", "시장 상황", "매크로", "금리", "나스닥", "s&p", "vix", "연준", "fed"]
    trading = ["사도", "살까", "매수", "매수해", "들어가", "진입", "팔까", "팔아", "팔아야", "매도", "얼마에 팔", "얼마에팔", "손절", "익절", "목표가"]
    if any(x in t for x in portfolio): return "portfolio_stock" if tickers else "portfolio"
    if any(x in t for x in market): return "market"
    if len(tickers) >= 2 or any(x in t for x in ["비교", "뭐가 나아", "뭐가 좋아", "둘 중", "어느 게", "어떤 게"]): return "comparison"
    if tickers: return "stock_decision" if any(x in t for x in trading) else "stock_analysis"
    return "general"


def parse_question(question):
    tickers = extract_tickers(question)
    return {
        "question": question, "tickers": tickers,
        "intent": detect_intent(question, tickers),
        "primary_ticker": tickers[0] if tickers else None,
        "timestamp": datetime.now().isoformat(),
    }


def get_account_data():
    print("\n🏦 토스증권 계좌정보를 확인하는 중...")
    try:
        toss_api = importlib.import_module("toss_api")
        data = toss_api.get_account_data()
        if not data:
            raise RuntimeError("토스 API에서 계좌정보가 비어 있습니다.")
        print("✅ 실제 토스 계좌정보 확보 완료")
        return data
    except Exception as e:
        print(f"❌ 토스 계좌정보 조회 실패: {type(e).__name__}: {e}")
        return {"status": "계좌정보 조회 실패", "error": str(e), "account": {}, "holdings": []}


def show_request(parsed):
    print("\n" + "=" * 70)
    print("🧠 질문 분석")
    print(f"사용자 질문 : {parsed['question']}")
    print(f"분석 유형   : {parsed['intent']}")
    print("분석 종목   : " + (", ".join(parsed["tickers"]) if parsed["tickers"] else "전체 시장 / 포트폴리오") )
    print("=" * 70)


def save_meeting_file(name, data):
    path = os.path.join(HISTORY_DIR, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    save_json(path, data)
    return path


def run_meeting(parsed, modules, account_data):
    from ai.batch_engine import run_team_batches

    tickers = parsed.get("tickers", [])
    print("\n" + "=" * 70)
    print("⚔️ AI TRADING TEAM 회의")
    print("=" * 70)
    print("🎯 분석 대상:", ", ".join(tickers) if tickers else "전체 시장 / 포트폴리오")
    print("🧠 독립 분석은 역할별 1회 호출 + 병렬 실행합니다.")

    started = time.time()
    team_results = run_team_batches(modules, tickers, account_data, max_workers=4)
    print(f"⏱️ 4인 독립 분석 완료 ({time.time() - started:.1f}초)")

    # 통합 토론: 이미 계산된 4명의 결과만 사용. 기존 ROUND 1/2 재호출 금지.
    try:
        debate_module = importlib.import_module("ai.debate")
        print("\n⚔️ 4인 통합 토론 시작 (1회)")
        debate_result = debate_module.run_debate(
            modules=modules,
            parsed=parsed,
            account_data=account_data,
            team_results=team_results,
        )
    except Exception as e:
        print(f"❌ 통합 토론 오류: {type(e).__name__}: {e}")
        debate_result = {"initial_results": team_results, "final_positions": {}, "transcript": "", "debate_results": []}

    package = {"request": parsed, "account_data": account_data, "team_results": team_results, "debate": debate_result, "timestamp": datetime.now().isoformat()}
    save_meeting_file("team_meeting", package)

    # 알프레도는 정확히 한 번 최종 검증한다.
    cat_result = None
    cat = modules.get("cat")
    if cat is not None and callable(getattr(cat, "run_discussion", None)):
        print("\n🐱 알프레도 최종 검증 시작 (1회)")
        final_instruction = """
[돈물원 최종 사용자 출력 규칙]
너는 최종 팀장이다. 내부 검증은 충분히 하되 사용자 화면에는 핵심만 보여준다.
연구보고서처럼 길게 쓰지 말고 종목별 결론을 먼저 제시한다.
각 종목은 다음 중 실제 근거에 맞는 행동을 선택한다: 매수 / 추가매수 / 보유 / 일부매도 / 전량매도 / 관망 / 비중조절.
사용자가 매도·손절·익절 가격을 물었다면 실제 변동성, ATR/기술적 위치, 지지·저항, 기업 상황, 뉴스, 시장환경, 계좌 비중과 평균매수가를 종합하여 가격을 계산한다.
+10%, +20% 같은 고정 규칙을 임의로 적용하지 않는다.
가격을 계산할 근거가 부족하면 억지 숫자를 만들지 말고 확인 필요라고 한다.
최종 화면은 다음 순서로 압축한다:
1) 🐱 알프레도 최종 판단
2) 종목별 한 줄 행동
3) 종목별 현재가/핵심 기준 가격(가능한 경우)
4) 가장 중요한 이유 2~4개
5) 각 AI의 한마디를 짧게 1줄씩
상세 회의록을 장황하게 반복하지 않는다.
"""
        context = {
            "user_question": parsed["question"], "parsed": parsed,
            "account_data": account_data, "team_results": team_results,
            "debate": debate_result, "final_output_instruction": final_instruction,
        }
        try:
            cat_result = cat.run_discussion(
                discussion_prompt=json.dumps(context, ensure_ascii=False, indent=2, default=str),
                team_results=team_results, account_data=account_data, parsed=parsed,
            )
        except Exception as e:
            print(f"❌ 알프레도 오류: {type(e).__name__}: {e}")

    final_data = {**package, "alfredo": normalize_result(cat_result)}
    final_path = save_meeting_file("final_meeting", final_data)

    print("\n" + "━" * 70)
    print("🐱 알프레도 최종 판단")
    print("━" * 70)
    print(normalize_result(cat_result) if cat_result else "❌ 최종 판단을 생성하지 못했습니다.")
    print("━" * 70)
    print(f"💾 최종 회의록: {final_path}")
    return final_data


def main():
    print("\n" + "=" * 70)
    print("🏦 AI TRADING TEAM / 돈물원")
    print("빠른 통합 투자 분석 시스템")
    print("=" * 70)
    modules = load_ai_modules()
    for key, name in [("crow", "🐦 김선달"), ("snake", "🐍 이묵"), ("raccoon", "🦝 너부리"), ("turtle", "🐢 현무"), ("cat", "🐱 알프레도")]:
        print(("✅" if modules.get(key) else "❌") + " " + name)

    while True:
        question = input("\n👤 사용자: ").strip()
        if not question:
            print("⚠️ 질문을 입력해주세요.")
            continue
        if question.lower() in {"exit", "quit", "종료"}:
            print("🏦 돈물원을 종료합니다.")
            break
        parsed = parse_question(question)
        show_request(parsed)
        account_data = get_account_data()
        save_json(AI_PORTFOLIO_FILE, account_data)
        run_meeting(parsed, modules, account_data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 사용자가 프로그램을 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 치명적 오류: {type(e).__name__}: {e}")
