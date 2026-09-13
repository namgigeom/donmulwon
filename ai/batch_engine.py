import inspect
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from ai.data_cache import get_or_fetch, stats as cache_stats

ROLE_CONFIG = {
    "crow": {"name": "🐦 김선달", "prompt_ticker": "target_ticker"},
    "snake": {"name": "🐍 이묵", "prompt_ticker": "ticker"},
    "raccoon": {"name": "🦝 너부리", "prompt_ticker": "target_ticker"},
    "turtle": {"name": "🐢 현무", "prompt_ticker": "ticker"},
}

# yfinance/network 작업은 I/O bound라 소수의 worker로 병렬화한다.
DATA_MAX_WORKERS = 6
ROLE_MAX_WORKERS = 4


def _json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


@lru_cache(maxsize=32)
def _extract_prompt(function):
    """Prompt source parsing is expensive; cache it for the process lifetime."""
    source = inspect.getsource(function)
    match = re.search(r"prompt\s*=\s*f([\"']{3})(.*?)(?:\1)", source, re.S)
    if not match:
        raise RuntimeError("기존 AI 프롬프트를 추출하지 못했습니다.")
    return match.group(2)


def _render_prompt(template, ticker_label, data_text):
    prompt = template
    for key, value in (
        ("{data_text}", data_text),
        ("{ticker}", ticker_label),
        ("{target_ticker}", ticker_label),
    ):
        prompt = prompt.replace(key, value)
    return prompt


def _cached_call(namespace, value, function, *args):
    return get_or_fetch(namespace, value, lambda: function(*args))


def _parallel_map(tickers, worker, max_workers=DATA_MAX_WORKERS):
    """Run independent ticker operations concurrently while preserving order."""
    tickers = list(dict.fromkeys(tickers or []))
    if len(tickers) <= 1:
        return {t: worker(t) for t in tickers}

    workers = min(max_workers, len(tickers))
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker, ticker): ticker for ticker in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            results[ticker] = future.result()
    return {ticker: results[ticker] for ticker in tickers}


def _collect_crow_ticker(module, ticker):
    """Collect Crow's three independent yfinance datasets concurrently.

    This intentionally bypasses collect_data() when its implementation is
    sequential, while keeping the original collector functions and output shape.
    """
    company_fn = getattr(module, "get_company_data", None)
    news_fn = getattr(module, "get_news", None)
    financial_fn = getattr(module, "get_financials", None)
    if not all(callable(fn) for fn in (company_fn, news_fn, financial_fn)):
        collector = getattr(module, "collect_data", None)
        if not callable(collector):
            raise RuntimeError("김선달 데이터 수집 함수를 찾지 못했습니다.")
        return collector(ticker)

    jobs = {
        "company": ("crow.company", company_fn),
        "news": ("crow.news", news_fn),
        "financials": ("crow.financials", financial_fn),
    }
    result = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_cached_call, namespace, ticker, fn, ticker): key
            for key, (namespace, fn) in jobs.items()
        }
        for future in as_completed(futures):
            result[futures[future]] = future.result()
    return result


def _collect_role_data(module, role, tickers, account_data):
    tickers = list(dict.fromkeys(tickers or []))
    memory = {}
    try:
        loader = getattr(module, "load_memory", None)
        if callable(loader):
            memory = loader()
    except Exception:
        pass

    if role == "crow":
        stocks = _parallel_map(tickers, lambda t: _collect_crow_ticker(module, t))
        return {
            "role": role,
            "requested_tickers": tickers,
            "stocks": stocks,
            "memory": memory,
            "portfolio_context": account_data,
        }

    if role == "snake":
        collector = getattr(module, "get_market_data", None)
        if not callable(collector):
            raise RuntimeError("이묵 get_market_data를 찾지 못했습니다.")
        stocks = _parallel_map(
            tickers,
            lambda t: _cached_call("snake.get_market_data", t, collector, t),
        )
        return {
            "role": role,
            "requested_tickers": tickers,
            "stocks": stocks,
            "memory": memory,
            "portfolio_context": account_data,
        }

    if role == "raccoon":
        analyze_portfolio = getattr(module, "analyze_portfolio", None)
        find_holding = getattr(module, "find_holding", None)
        get_market_context = getattr(module, "get_market_context", None)
        get_stock_data = getattr(module, "get_stock_data", None)
        if not all(callable(x) for x in (analyze_portfolio, find_holding, get_market_context, get_stock_data)):
            raise RuntimeError("너부리의 계좌/시장 데이터 함수를 찾지 못했습니다.")

        # 계좌/시장 공통 데이터는 동시에 한 번만 가져온다.
        with ThreadPoolExecutor(max_workers=2) as executor:
            portfolio_future = executor.submit(
                _cached_call,
                "raccoon.analyze_portfolio",
                _json(account_data),
                analyze_portfolio,
                account_data,
            )
            market_future = executor.submit(
                _cached_call,
                "raccoon.get_market_context",
                "current",
                get_market_context,
            )
            portfolio = portfolio_future.result()
            market = market_future.result()

        def raccoon_stock(ticker):
            holding = _cached_call(
                "raccoon.find_holding",
                (_json(account_data), ticker),
                find_holding,
                account_data,
                ticker,
            )
            stock_data = _cached_call(
                "raccoon.get_stock_data",
                ticker,
                get_stock_data,
                ticker,
            )
            return {"holding": holding, "stock_data": stock_data}

        stocks = _parallel_map(tickers, raccoon_stock)
        return {
            "role": role,
            "requested_tickers": tickers,
            "stocks": stocks,
            "market_data": market,
            "portfolio_context": portfolio,
            "memory": memory,
        }

    if role == "turtle":
        get_market_data = getattr(module, "get_market_data", None)
        get_market_trends = getattr(module, "get_market_trends", None)
        get_stock_context = getattr(module, "get_stock_context", None)
        if not all(callable(x) for x in (get_market_data, get_market_trends, get_stock_context)):
            raise RuntimeError("현무의 시장 데이터 함수를 찾지 못했습니다.")

        # 서로 독립적인 시장 요청은 동시에 수행한다.
        with ThreadPoolExecutor(max_workers=2) as executor:
            market_future = executor.submit(
                _cached_call, "turtle.get_market_data", "current", get_market_data
            )
            trends_future = executor.submit(
                _cached_call, "turtle.get_market_trends", "current", get_market_trends
            )
            market = market_future.result()
            trends = trends_future.result()

        stocks = _parallel_map(
            tickers,
            lambda t: _cached_call(
                "turtle.get_stock_context", t, get_stock_context, t
            ),
        )
        return {
            "role": role,
            "requested_tickers": tickers,
            "market_data": market,
            "market_trends": trends,
            "stocks": stocks,
            "memory": memory,
        }

    raise ValueError(f"지원하지 않는 role: {role}")


def run_role_batch(module, role, tickers, account_data):
    """Run one LLM request for one specialist after parallel data collection."""
    if module is None:
        return None

    function_name = "analyze_macro" if role == "turtle" else "analyze_stock"
    function = getattr(module, function_name, None)
    if not callable(function):
        raise RuntimeError(f"{role}의 {function_name} 함수를 찾지 못했습니다.")

    data = _collect_role_data(module, role, tickers, account_data)
    data_text = _json(data)
    ticker_label = ", ".join(tickers) if tickers else "MARKET / PORTFOLIO"
    template = _extract_prompt(function)
    prompt = _render_prompt(template, ticker_label, data_text)
    prompt += f"""

==================================================
⚡ 돈물원 통합 분석 지시
==================================================
이번 회의의 분석 대상은 다음과 같다.
{ticker_label}
위 데이터에 포함된 모든 종목을 빠짐없이 구분해서 분석한다.
종목별 결론을 섞지 않는다.
데이터에 없는 수치를 만들지 않는다.
사용자가 매도/손절/익절 가격을 요청했다면 고정 퍼센트가 아니라 실제 변동성, 기술적 위치, 기업 상황, 시장환경, 계좌 상황을 근거로 판단한다.
이 응답은 다른 팀원과 최종 팀장에게 전달된다. 각 종목별로 가장 중요한 사실과 판단을 명확하게 구분한다.
"""

    router = getattr(module, "ai_router", None)
    if router is None or not hasattr(router, "generate_content"):
        raise RuntimeError(f"{role}의 ai_router를 찾지 못했습니다.")

    response = router.generate_content(model="gemini-3.6-flash", contents=prompt)
    return getattr(response, "text", str(response))


def run_team_batches(modules, tickers, account_data, max_workers=ROLE_MAX_WORKERS):
    """Run the four specialist analyses concurrently."""
    tickers = list(dict.fromkeys(tickers or []))
    results = {}
    jobs = {}
    roles = [
        ("crow", "🐦 김선달"),
        ("snake", "🐍 이묵"),
        ("raccoon", "🦝 너부리"),
        ("turtle", "🐢 현무"),
    ]

    with ThreadPoolExecutor(max_workers=min(max_workers, len(roles))) as executor:
        for role, name in roles:
            module = modules.get(role)
            if module is None:
                results[role] = None
                continue
            jobs[executor.submit(run_role_batch, module, role, tickers, account_data)] = (role, name)

        for future in as_completed(jobs):
            role, name = jobs[future]
            try:
                results[role] = future.result()
                print(f"✅ {name} 통합 분석 완료")
            except Exception as exc:
                print(f"❌ {name} 분석 실패: {type(exc).__name__}: {exc}")
                results[role] = None

    cache = cache_stats()
    print(f"📦 데이터 캐시: hit {cache['hits']} / miss {cache['misses']}")
    return results
