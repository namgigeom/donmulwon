import os
import sys
import json
import importlib
import time
import re
from datetime import datetime
from dotenv import load_dotenv

if getattr(sys, "frozen", False): BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else: BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
AI_DIR=os.path.join(BASE_DIR,"ai"); HISTORY_DIR=os.path.join(AI_DIR,"analysis_history"); AI_PORTFOLIO_FILE=os.path.join(BASE_DIR,"ai_portfolio.json"); GUI_STATE_FILE=os.path.join(BASE_DIR,"meeting_state.json")
os.makedirs(AI_DIR,exist_ok=True); os.makedirs(HISTORY_DIR,exist_ok=True)
KNOWN_TICKERS={"REKR":"Rekor Systems","ALAB":"Astera Labs","VOO":"Vanguard S&P 500 ETF","TTWO":"Take-Two Interactive","JEPQ":"JPMorgan Nasdaq Equity Premium Income ETF","JOBY":"Joby Aviation","TSLA":"Tesla","NVDA":"NVIDIA","AAPL":"Apple","MSFT":"Microsoft","GOOGL":"Alphabet","AMZN":"Amazon","META":"Meta"}
TICKER_ALIASES={"조비":"JOBY","조비에비에이션":"JOBY","조비 에비에이션":"JOBY","joby aviation":"JOBY","아스테라":"ALAB","아스테라랩스":"ALAB","아스테라 랩스":"ALAB","astera labs":"ALAB","리코":"REKR","리커":"REKR","리코 시스템즈":"REKR","리코르":"REKR","rekor systems":"REKR","브이오오":"VOO","s&p500":"VOO","s&p 500":"VOO","제프큐":"JEPQ","제이이피큐":"JEPQ","테슬라":"TSLA","엔비디아":"NVDA","애플":"AAPL","마이크로소프트":"MSFT","마소":"MSFT","알파벳":"GOOGL","구글":"GOOGL","아마존":"AMZN","메타":"META","테이크투":"TTWO","테이크 투":"TTWO"}

def set_gui_state(stage):
    """GUI character layer bridge. The GUI polls this tiny file without blocking the AI worker."""
    try:
        tmp=GUI_STATE_FILE+".tmp"
        with open(tmp,"w",encoding="utf-8") as f: json.dump({"stage":stage,"updated":time.time()},f,ensure_ascii=False)
        os.replace(tmp,GUI_STATE_FILE)
    except Exception as e: print(f"⚠️ GUI 상태 전달 실패: {e}")

def load_ai_modules():
    modules={}; original_key=os.environ.get("GEMINI_API_KEY")
    if not original_key: os.environ["GEMINI_API_KEY"]="DUMMY_IMPORT_ONLY_KEY"
    try:
        for name in ["crow","snake","raccoon","turtle","cat"]:
            try: modules[name]=importlib.import_module(f"ai.{name}")
            except Exception as e: print(f"⚠️ {name}.py 불러오기 실패: {type(e).__name__}: {e}"); modules[name]=None
    finally:
        if original_key is None: os.environ.pop("GEMINI_API_KEY",None)
        else: os.environ["GEMINI_API_KEY"]=original_key
    return modules

def save_json(path,data):
    try:
        with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2,default=str)
        return True
    except Exception as e: print(f"⚠️ JSON 저장 실패: {type(e).__name__}: {e}"); return False


def is_valid_ai_result(value):
    if not isinstance(value, str) or not value.strip():
        return False
    t=" ".join(value.lower().split())
    invalid_markers=(
        "safety categories:", "unauthorized advice", "user safety:", "safety category:",
        "here's a thinking process", "analyze user input", "identify the core task",
        "key constraints", "deconstruct the output rules", "final answer:"
    )
    if any(marker in t for marker in invalid_markers):
        return False
    # 분석 결과가 지나치게 영어 위주인 경우도 정상 결과로 취급하지 않는다.
    hangul=sum("가" <= ch <= "힣" for ch in value)
    latin=sum("a" <= ch.lower() <= "z" for ch in value)
    if hangul == 0 and latin > 80:
        return False
    return True

def normalize_result(result):
    if result is None:return ""
    if isinstance(result,str):
        return result.replace("\x00","").replace("<unk>","")
    try:
        return json.dumps(result,ensure_ascii=False,indent=2,default=str).replace("\x00","").replace("<unk>","")
    except Exception:
        return str(result).replace("\x00","").replace("<unk>","")

def extract_team_voice(team_results):
    """각 전문 AI가 자기 분석에서 직접 작성한 '한마디'를 보존한다."""
    specs = [
        ("turtle", "🐢 현무", r"##\s*🐢\s*현무[^\n]*한마디"),
        ("crow", "🐦 김선달", r"##\s*🐦\s*김선달[^\n]*한마디"),
        ("snake", "🐍 이묵", r"##\s*🐍\s*이묵[^\n]*한마디"),
        ("raccoon", "🦝 너부리", r"##\s*🦝\s*너부리[^\n]*한마디"),
    ]
    lines = []
    for key, label, heading in specs:
        raw = normalize_result(team_results.get(key, "")).strip()
        if not raw:
            continue
        opinion = ""
        match = re.search(
            heading + r"\s*\n(.*?)(?=\n={10,}|\n##\s|\Z)",
            raw,
            flags=re.S,
        )
        if match:
            opinion = match.group(1).strip()
        if not opinion:
            candidates = [x.strip(" -*#") for x in raw.splitlines() if x.strip()]
            if candidates:
                opinion = candidates[-1]
        if opinion:
            opinion = re.sub(r"\n{3,}", "\n\n", opinion).strip()
            lines.append(f"### {label}의 의견\n{opinion}")
    return "\n\n".join(lines)

def save_meeting_file(name,data):
    path=os.path.join(HISTORY_DIR,f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"); save_json(path,data); return path

def extract_tickers(text):
    if not text:return []
    upper,lower=text.upper(),text.lower(); found=[ticker for ticker in KNOWN_TICKERS if ticker in upper]; found += [ticker for alias,ticker in TICKER_ALIASES.items() if alias.lower() in lower]; return list(dict.fromkeys(found))

def detect_intent(text,tickers):
    t=(text or "").lower(); portfolio=["내 계좌","내계좌","내 포트폴리오","내포트폴리오","계좌","포트폴리오","보유종목","보유 종목","전체 자산","비중","내 자산","계좌 전체","계좌상태","계좌 상태"]; market=["미국 증시","미국시장","미국 시장","시장 분위기","시장 상황","매크로","금리","나스닥","s&p","vix","연준","fed"]; trading=["사도","살까","매수","매수해","들어가","진입","팔까","팔아","팔아야","매도","얼마에 팔","얼마에팔","손절","익절","목표가"]; comparison=["비교","뭐가 나아","뭐가 좋아","둘 중","어느 게","어떤 게","어느쪽"]
    if any(x in t for x in portfolio):return "portfolio_stock" if tickers else "portfolio"
    if any(x in t for x in market):return "market"
    if len(tickers)>=2 or any(x in t for x in comparison):return "comparison"
    if tickers:return "stock_decision" if any(x in t for x in trading) else "stock_analysis"
    return "general"

def parse_question(question):
    tickers=extract_tickers(question); return {"question":question,"tickers":tickers,"intent":detect_intent(question,tickers),"primary_ticker":tickers[0] if tickers else None,"timestamp":datetime.now().isoformat()}

def show_request(parsed):
    print("\n"+"="*70); print("🧠 질문 분석"); print("="*70); print(f"사용자 질문 : {parsed['question']}"); print(f"분석 유형   : {parsed['intent']}"); print("분석 종목   : "+(", ".join(parsed["tickers"]) if parsed["tickers"] else "전체 시장 / 포트폴리오"))

def get_account_data():
    print("\n🏦 토스증권 계좌정보를 확인하는 중...")
    try:
        toss_api=importlib.import_module("toss_api"); account_data=toss_api.get_account_data()
        if not account_data:raise RuntimeError("토스 API에서 계좌정보가 비어 있습니다.")
        print("✅ 실제 토스 계좌정보 확보 완료"); return account_data
    except Exception as e:
        print(f"❌ 토스 계좌정보 조회 실패: {type(e).__name__}: {e}"); return {"status":"계좌정보 조회 실패","error":str(e),"account":{},"holdings":[],"cash":{}}

def run_meeting(parsed,modules,account_data):
    from ai.batch_engine import run_team_batches
    from ai.data_cache import clear as clear_data_cache
    clear_data_cache()
    set_gui_state("collect")
    print("[PROGRESS 3] 계좌/시장 데이터 준비")
    tickers = list(dict.fromkeys(parsed.get("tickers", []) or []))
    if not tickers:
        try:
            holding_items = account_data.get("holdings", {}).get("result", {}).get("items", [])
            account_tickers = [
                str(item.get("symbol") or "").upper().strip()
                for item in holding_items
                if item.get("symbol")
            ]
            tickers = list(dict.fromkeys(account_tickers))
            if tickers:
                print("📋 전체 계좌 분석이므로 보유종목을 자동 분석 대상으로 포함:", ", ".join(tickers))
        except Exception as exc:
            print(f"⚠️ 보유종목 목록 추출 실패: {type(exc).__name__}: {exc}")
    print("\n"+"="*70); print("⚔️ AI TRADING TEAM 회의"); print("="*70); print("🎯 분석 대상:",", ".join(tickers) if tickers else "전체 시장 / 포트폴리오"); print("⚡ 4명 독립 분석: 역할별 1회 호출 + 병렬 실행")
    started=time.time()
    team_results=run_team_batches(modules,tickers,account_data,max_workers=4)
    print("[PROGRESS 60] 4명 독립 분석 종료")
    elapsed = time.time()-started
    success_roles = [key for key, value in team_results.items() if is_valid_ai_result(value)]
    print(f"⏱️ 4인 독립 분석 완료 ({elapsed:.1f}초) | 성공 {len(success_roles)}/4")
    if not success_roles:
        set_gui_state("error")
        details = []
        for key, value in team_results.items():
            if is_valid_ai_result(value):
                continue
            role_error = getattr(run_team_batches, "last_errors", {}).get(key, "원인 미상")
            details.append(f"{key}=실패({role_error})")
        detail_text = ", ".join(details) if details else "실패 원인 미상"
        raise RuntimeError(
            "4명 전문 AI가 모두 응답하지 못했습니다. "
            f"역할별 상태: {detail_text}. "
            "각 역할의 콘솔 로그에서 최종 fallback 오류를 확인하세요."
        )
    # Keep the team physically in the meeting while the debate runs.
    set_gui_state("meeting")
    print("[PROGRESS 65] ⚔️ 통합 회의 시작")
    try:
        debate_module=importlib.import_module("ai.debate"); print("\n⚔️ 4인 통합 토론 시작 (1회)")
        debate_started=time.time(); debate_result=debate_module.run_debate(modules=modules,parsed=parsed,account_data=account_data,team_results=team_results); print(f"⏱️ 통합 토론 완료 ({time.time()-debate_started:.1f}초)")
        print("[PROGRESS 80] ⚔️ 통합 회의 완료")
    except Exception as e:
        print(f"❌ 통합 토론 오류: {type(e).__name__}: {e}"); debate_result={"initial_results":team_results,"final_positions":dict(team_results),"meeting_summary":"통합 토론이 완료되지 않아 각 전문 AI의 독립 분석을 보존합니다.","conflicts":[],"consensus":[],"important_corrections":[],"transcript":"","error":str(e)}
    package={"request":parsed,"account_data":account_data,"team_results":team_results,"debate":debate_result,"timestamp":datetime.now().isoformat()}; save_meeting_file("team_meeting",package)
    cat_result=None; cat=modules.get("cat")
    if cat is not None and callable(getattr(cat,"analyze",None)):
        set_gui_state("verdict"); print("[PROGRESS 85] 🐱 알프레도 최종 검증 시작")
        print("\n🐱 알프레도 최종 검증 시작 (1회)"); ticker_label=", ".join(tickers) if tickers else "전체 시장 / 포트폴리오"; cat_filename_label=re.sub(r'[<>:"/\\|?*]','_',ticker_label).strip(" .") or "MARKET"
        instruction=f"""
[최종 사용자 화면 출력 규칙]
너는 돈물원 트레이딩 팀의 최종 팀장이다.
현재 계좌 원본, 4명의 독립 분석, 통합 토론을 교차검증하되 사용자에게는 긴 연구보고서를 출력하지 않는다.
사용자가 실제로 질문한 대상은: {ticker_label}
위 대상 각각을 빠뜨리지 말고 별도로 판단한다.
행동은 적극 매수 / 조건부 매수 / 추가매수 / 보유 / 관망 / 일부매도 / 전량매도 / 비중조절 중 근거에 맞게 선택한다.
손절·익절·매도가를 요청했다면 +10%, +20% 같은 고정 비율을 사용하지 않는다. 실제 변동성, ATR, 지지/저항, 추세, 기업 상황, 실적, 뉴스, 시장환경, 평균매수가와 계좌 비중을 종합한다.
가격 근거가 부족하면 숫자를 만들지 말고 '확인 필요'라고 한다.
최종 답변은 1) 알프레도 판단 2) 종목별 행동+현재가 3) 종목별 핵심 기준 가격 4) 핵심 이유 2~4개 5) 네 AI의 핵심 의견 1줄씩 순서로 압축한다.
"""
        team_for_cat={key:{"file":None,"content":normalize_result(value)} for key,value in team_results.items()}
        try:
            cat_started=time.time()
            cat_result=cat.analyze(question=parsed["question"]+"\n\n"+instruction,ticker=cat_filename_label,team_analyses=team_for_cat,account_context=account_data)
            cat_result=normalize_result(cat_result).strip()
            # Gemini/Router가 빈 text를 반환하는 경우 GUI가 "최종 판단 없음"으로
            # 끝나지 않도록 한 번만 재요청한다. 기존 분석 데이터는 그대로 사용한다.
            if not cat_result:
                print("⚠️ 알프레도 응답 본문이 비어 있어 최종 검증을 1회 재시도합니다.")
                retry_instruction=instruction+"\\n\\n[재시도 규칙] 반드시 빈 응답을 반환하지 말고 최종 판단을 일반 텍스트로 작성한다. 데이터가 부족한 항목은 '확인 필요'라고 명시한다."
                cat_result=cat.analyze(question=parsed["question"]+"\\n\\n"+retry_instruction,ticker=cat_filename_label,team_analyses=team_for_cat,account_context=account_data)
                cat_result=normalize_result(cat_result).strip()
            print(f"⏱️ 알프레도 검증 완료 ({time.time()-cat_started:.1f}초)")
            print("[PROGRESS 95] 🐱 알프레도 검증 완료")
        except Exception as e:
            print(f"❌ 알프레도 오류: {type(e).__name__}: {e}")
            cat_result=""
    else: print("❌ 알프레도 모듈을 사용할 수 없습니다.")
    alfredo_text=normalize_result(cat_result).strip()

    # 전문 AI의 원문 한마디는 최종 판단 본문에 무조건 붙이지 않는다.
    # 알프레도 응답이 실패했을 때 팀원 한마디만 남는 문제를 방지한다.
    team_voice = extract_team_voice(team_results)

    if not is_valid_ai_result(alfredo_text):
        alfredo_text = ""

    if not alfredo_text:
        debate_summary = normalize_result(debate_result.get("meeting_summary","")).strip()
        positions = debate_result.get("final_positions", {}) or {}
        position_lines = []
        for key, label in [("crow","🐦 김선달"),("snake","🐍 이묵"),("raccoon","🦝 너부리"),("turtle","🐢 현무")]:
            value = normalize_result(positions.get(key, "")).strip()
            if value:
                position_lines.append(f"- {label}: {value[:300]}")

        alfredo_text = (
            "# 🐱 알프레도 총괄 판단\n\n"
            "## 최종 판단\n"
            "알프레도의 최종 검증 응답이 정상적으로 생성되지 않았다. "
            "아래 내용은 회의에서 확보된 자료를 보존한 것이다. "
            "새로운 수치나 판단을 추측하지 않는다.\n\n"
            "## ⚔️ 회의 핵심\n"
            + (debate_summary[:1800] if debate_summary else "확인 가능한 통합 회의 요약이 없습니다.")
            + "\n\n## 전문 AI 최종 입장\n"
            + ("\n".join(position_lines) if position_lines else "각 팀원의 최종 입장을 확인할 수 없습니다.")
            + "\n\n※ 상세 최종 판단은 다음 분석에서 다시 확인 필요."
        )

    # 전문 AI 한마디는 최종 판단과 분리해 회의 로그에서만 사용한다.
    final_data={**package,"alfredo":alfredo_text}; final_path=save_meeting_file("final_meeting",final_data)
    print("\n"+"━"*70); print("🐱 알프레도 최종 판단"); print("━"*70); print(alfredo_text); print("━"*70); print(f"💾 최종 회의록: {final_path}")
    print("[PROGRESS 100] 분석 파이프라인 완료")
    set_gui_state("return")
    return final_data

def build_ai_portfolio_snapshot(account_data):
    """Convert one Toss API response into the normalized portfolio contract used by AI/GUI modules."""
    try:
        from portfolio_data import build_wallet, build_stocks
        holdings = account_data.get("holdings", {})
        cash = account_data.get("cash", {})
        usd_result = cash.get("USD", {}).get("result", {})
        krw_result = cash.get("KRW", {}).get("result", {})
        usd_cash = float(usd_result.get("cashBuyingPower", 0) or 0)
        krw_cash = float(krw_result.get("cashBuyingPower", 0) or 0)
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "wallet": build_wallet(holdings, usd_cash, krw_cash),
            "stocks": build_stocks(holdings),
        }
    except Exception as exc:
        print(f"⚠️ 포트폴리오 정규화 실패: {type(exc).__name__}: {exc}")
        return {"generated_at": datetime.now().isoformat(timespec="seconds"), "wallet": {}, "stocks": [], "raw_account_data": account_data}


def run_analysis(question):
    question=(question or "").strip()
    if not question:raise ValueError("분석 질문이 비어 있습니다.")
    # Immediately call the team into the office, even outside normal office hours.
    set_gui_state("summon")
    modules=load_ai_modules(); parsed=parse_question(question); show_request(parsed); account_data=get_account_data(); save_json(AI_PORTFOLIO_FILE,build_ai_portfolio_snapshot(account_data))
    try:return run_meeting(parsed,modules,account_data)
    except Exception:
        set_gui_state("return"); raise

def main():
    print("\n"+"="*70); print("🏦 AI TRADING TEAM / 돈물원"); print("⚡ 빠른 통합 투자 분석 시스템"); print("="*70); modules=load_ai_modules(); print("\n📋 AI 모듈 상태")
    for key,name in [("crow","🐦 김선달"),("snake","🐍 이묵"),("raccoon","🦝 너부리"),("turtle","🐢 현무"),("cat","🐱 알프레도")]:print(("✅" if modules.get(key) else "❌")+" "+name)
    while True:
        question=input("\n👤 사용자: ").strip()
        if not question:print("⚠️ 질문을 입력해주세요."); continue
        if question.lower() in {"exit","quit","종료"}:print("🏦 돈물원을 종료합니다."); break
        run_analysis(question)

if __name__=="__main__":
    try:main()
    except KeyboardInterrupt:print("\n⚠️ 사용자가 프로그램을 종료했습니다.")
    except Exception as e:print(f"\n❌ 프로그램 실행 중 치명적 오류: {type(e).__name__}: {e}")
