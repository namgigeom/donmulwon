import os
import json
from datetime import datetime

from dotenv import load_dotenv

from toss_api import (
    get_access_token,
    get_accounts,
    get_holdings,
    get_buying_power
)


# ============================================================
# 설정
# ============================================================

load_dotenv()

HISTORY_FILE = "portfolio_history.json"


# ============================================================
# ▲ ▼ 표시
# ============================================================

def arrow(value):

    if value > 0:
        return "▲"

    elif value < 0:
        return "▼"

    return "─"


# ============================================================
# 숫자 변환
# ============================================================

def to_float(value):

    try:
        return float(value)

    except:
        return 0.0


# ============================================================
# 포트폴리오 데이터 생성
# ============================================================

def build_portfolio(holdings, usd_cash, krw_cash):

    result = holdings["result"]

    # --------------------------------------------------------
    # 주식 평가액
    # --------------------------------------------------------

    stock_value = to_float(
        result["marketValue"]["amount"]["usd"]
    )

    # --------------------------------------------------------
    # 총 투자금
    # --------------------------------------------------------

    total_purchase = to_float(
        result["totalPurchaseAmount"]["usd"]
    )

    # --------------------------------------------------------
    # 총 손익
    # --------------------------------------------------------

    profit_loss = to_float(
        result["profitLoss"]["amount"]["usd"]
    )

    # --------------------------------------------------------
    # 중요
    #
    # 토스 API의 profitLoss.rate를 사용하지 않는다.
    #
    # 우리가 직접 계산한다.
    # --------------------------------------------------------

    if total_purchase != 0:

        profit_rate = (
            profit_loss / total_purchase
        )

    else:

        profit_rate = 0.0


    # --------------------------------------------------------
    # 오늘 손익
    # --------------------------------------------------------

    daily_profit = to_float(
        result["dailyProfitLoss"]["amount"]["usd"]
    )


    # --------------------------------------------------------
    # 오늘 수익률
    #
    # 토스 API의 daily rate도 그대로 사용하지 않고
    # 오늘 기준으로 계산할 수 있는 데이터가 있으면
    # 추후 개선한다.
    #
    # 현재는 토스 API 값을 사용.
    # --------------------------------------------------------

    daily_profit_rate = to_float(
        result["dailyProfitLoss"]["rate"]
    )


    # --------------------------------------------------------
    # 총 자산
    #
    # 미국주식 + USD 현금
    #
    # KRW는 아직 USD 환산하지 않는다.
    # --------------------------------------------------------

    total_assets_usd = (
        stock_value + usd_cash
    )


    # --------------------------------------------------------
    # 현금 비중
    # --------------------------------------------------------

    if total_assets_usd != 0:

        cash_ratio = (
            usd_cash / total_assets_usd
        )

    else:

        cash_ratio = 0.0


    # --------------------------------------------------------
    # 종목
    # --------------------------------------------------------

    stocks = []

    items = result.get("items", [])


    for item in items:

        market_value = to_float(
            item["marketValue"]["amount"]
        )

        stock_profit = to_float(
            item["profitLoss"]["amount"]
        )

        purchase_amount = to_float(
            item["marketValue"]["purchaseAmount"]
        )


        # ----------------------------------------------------
        # 종목별 수익률도 직접 계산
        # ----------------------------------------------------

        if purchase_amount != 0:

            stock_profit_rate = (
                stock_profit / purchase_amount
            )

        else:

            stock_profit_rate = 0.0


        # ----------------------------------------------------
        # 포트폴리오 비중
        # ----------------------------------------------------

        if total_assets_usd != 0:

            portfolio_weight = (
                market_value / total_assets_usd
            )

        else:

            portfolio_weight = 0.0


        stock = {

            "symbol":
                item["symbol"],

            "name":
                item["name"],

            "quantity":
                to_float(item["quantity"]),

            "last_price":
                to_float(item["lastPrice"]),

            "average_price":
                to_float(
                    item["averagePurchasePrice"]
                ),

            "purchase_amount":
                purchase_amount,

            "market_value":
                market_value,

            "profit_loss":
                stock_profit,

            "profit_rate":
                stock_profit_rate,

            "daily_profit":
                to_float(
                    item["dailyProfitLoss"]["amount"]
                ),

            "daily_profit_rate":
                to_float(
                    item["dailyProfitLoss"]["rate"]
                ),

            "portfolio_weight":
                portfolio_weight
        }

        stocks.append(stock)


    # --------------------------------------------------------
    # 전체 데이터
    # --------------------------------------------------------

    portfolio = {

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "total_assets":
            total_assets_usd,

        "stock_value":
            stock_value,

        "usd_cash":
            usd_cash,

        "krw_cash":
            krw_cash,

        "cash_ratio":
            cash_ratio,

        "total_purchase":
            total_purchase,

        "profit_loss":
            profit_loss,

        "profit_rate":
            profit_rate,

        "daily_profit":
            daily_profit,

        "daily_profit_rate":
            daily_profit_rate,

        "stocks":
            stocks
    }


    return portfolio


# ============================================================
# 히스토리 불러오기
# ============================================================

def load_history():

    if not os.path.exists(
        HISTORY_FILE
    ):

        return []


    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            history = json.load(f)


            if isinstance(
                history,
                list
            ):

                return history


    except Exception:

        pass


    return []


# ============================================================
# 기존 기록 수익률 재계산
# ============================================================

def repair_history(history):

    repaired = 0


    for record in history:

        total_purchase = to_float(
            record.get(
                "total_purchase",
                0
            )
        )

        profit_loss = to_float(
            record.get(
                "profit_loss",
                0
            )
        )


        if total_purchase != 0:

            correct_rate = (
                profit_loss /
                total_purchase
            )

        else:

            correct_rate = 0.0


        old_rate = to_float(
            record.get(
                "profit_rate",
                0
            )
        )


        # 값이 다르면 수정

        if abs(
            old_rate - correct_rate
        ) > 0.000001:

            record["profit_rate"] = (
                correct_rate
            )

            repaired += 1


    return repaired


# ============================================================
# 히스토리 저장
# ============================================================

def save_history(
    portfolio,
    history
):

    history.append(
        portfolio
    )


    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 지갑 출력
# ============================================================

def print_wallet(
    portfolio
):

    print()
    print("=" * 70)
    print("                 🏦 현재 자산")
    print("=" * 70)

    print(
        f"총자산       : "
        f"${portfolio['total_assets']:,.2f}"
    )

    print(
        f"주식 평가액 : "
        f"${portfolio['stock_value']:,.2f}"
    )

    print(
        f"USD 현금    : "
        f"${portfolio['usd_cash']:,.2f}"
    )

    print(
        f"KRW 현금    : "
        f"₩{portfolio['krw_cash']:,.0f}"
    )

    print(
        f"현금 비중   : "
        f"{portfolio['cash_ratio'] * 100:.2f}%"
    )

    print(
        f"총 투자금   : "
        f"${portfolio['total_purchase']:,.2f}"
    )

    print(
        f"총 손익     : "
        f"${portfolio['profit_loss']:+,.2f} "
        f"{arrow(portfolio['profit_loss'])}"
    )

    print(
        f"총 수익률   : "
        f"{portfolio['profit_rate'] * 100:+.2f}% "
        f"{arrow(portfolio['profit_rate'])}"
    )

    print(
        f"오늘 손익   : "
        f"${portfolio['daily_profit']:+,.2f} "
        f"{arrow(portfolio['daily_profit'])}"
    )

    print(
        f"오늘 수익률 : "
        f"{portfolio['daily_profit_rate'] * 100:+.2f}% "
        f"{arrow(portfolio['daily_profit_rate'])}"
    )


# ============================================================
# 종목 출력
# ============================================================

def print_stocks(
    portfolio
):

    print()
    print("=" * 70)
    print("                 📈 현재 종목")
    print("=" * 70)


    # --------------------------------------------------------
    # 비중 높은 순서
    # --------------------------------------------------------

    stocks = sorted(
        portfolio["stocks"],
        key=lambda x:
            x["portfolio_weight"],
        reverse=True
    )


    for stock in stocks:

        print()

        print(
            f"📌 {stock['symbol']} "
            f"({stock['name']})"
        )

        print(
            f"수량       : "
            f"{stock['quantity']:.6f}주"
        )

        print(
            f"현재가     : "
            f"${stock['last_price']:,.2f}"
        )

        print(
            f"평균매수가 : "
            f"${stock['average_price']:,.2f}"
        )

        print(
            f"평가금액   : "
            f"${stock['market_value']:,.2f}"
        )

        print(
            f"손익       : "
            f"${stock['profit_loss']:+,.2f} "
            f"{arrow(stock['profit_loss'])}"
        )

        print(
            f"수익률     : "
            f"{stock['profit_rate'] * 100:+.2f}% "
            f"{arrow(stock['profit_rate'])}"
        )

        print(
            f"오늘       : "
            f"${stock['daily_profit']:+,.2f} "
            f"{arrow(stock['daily_profit'])}"
        )

        print(
            f"포트폴리오 : "
            f"{stock['portfolio_weight'] * 100:.2f}%"
        )


# ============================================================
# 최근 기록 출력
# ============================================================

def print_history(
    history,
    count=5
):

    print()
    print("=" * 70)
    print("                 📊 최근 자산 기록")
    print("=" * 70)


    recent = history[-count:]


    for record in reversed(
        recent
    ):

        print()

        print(
            f"시간 : "
            f"{record.get('timestamp', '-')}"
        )

        print(
            f"총자산       : "
            f"${to_float(record.get('total_assets', 0)):,.2f}"
        )

        print(
            f"주식 평가액  : "
            f"${to_float(record.get('stock_value', 0)):,.2f}"
        )

        print(
            f"USD 현금     : "
            f"${to_float(record.get('usd_cash', 0)):,.2f}"
        )

        print(
            f"KRW 현금     : "
            f"₩{to_float(record.get('krw_cash', 0)):,.0f}"
        )

        print(
            f"총 투자금    : "
            f"${to_float(record.get('total_purchase', 0)):,.2f}"
        )

        print(
            f"총 손익      : "
            f"${to_float(record.get('profit_loss', 0)):+,.2f} "
            f"{arrow(to_float(record.get('profit_loss', 0)))}"
        )

        print(
            f"총 수익률    : "
            f"{to_float(record.get('profit_rate', 0)) * 100:+.2f}% "
            f"{arrow(to_float(record.get('profit_rate', 0)))}"
        )


# ============================================================
# 🚀 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("              📊 PORTFOLIO HISTORY")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # 토스 API
        # ----------------------------------------------------

        print()
        print("토스 계좌를 확인하는 중...")


        token = get_access_token()

        accounts = get_accounts(
            token
        )

        account_list = accounts.get(
            "result",
            []
        )


        if not account_list:

            raise Exception(
                "연결된 토스 계좌가 없습니다."
            )


        account = account_list[0]

        account_seq = account[
            "accountSeq"
        ]


        # ----------------------------------------------------
        # 보유 주식
        # ----------------------------------------------------

        holdings = get_holdings(
            token,
            account_seq
        )


        # ----------------------------------------------------
        # 매수 가능 금액
        # ----------------------------------------------------

        print()
        print(
            "USD 매수 가능 금액을 조회하는 중..."
        )

        usd_power = get_buying_power(
            token,
            account_seq,
            "USD"
        )


        print(
            "KRW 매수 가능 금액을 조회하는 중..."
        )

        krw_power = get_buying_power(
            token,
            account_seq,
            "KRW"
        )


        usd_cash = to_float(
            usd_power["result"][
                "cashBuyingPower"
            ]
        )

        krw_cash = to_float(
            krw_power["result"][
                "cashBuyingPower"
            ]
        )


        # ----------------------------------------------------
        # 포트폴리오 생성
        # ----------------------------------------------------

        portfolio = build_portfolio(
            holdings,
            usd_cash,
            krw_cash
        )


        # ----------------------------------------------------
        # 기존 기록 불러오기
        # ----------------------------------------------------

        history = load_history()


        # ----------------------------------------------------
        # 기존 잘못된 수익률 자동 수정
        # ----------------------------------------------------

        repaired = repair_history(
            history
        )


        if repaired > 0:

            with open(
                HISTORY_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    history,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            print()
            print(
                f"🔧 기존 기록 {repaired}개 "
                f"수익률을 재계산했습니다."
            )


        # ----------------------------------------------------
        # 현재 기록 추가
        # ----------------------------------------------------

        save_history(
            portfolio,
            history
        )


        print()
        print(
            "✅ 현재 포트폴리오 저장 완료"
        )


        # ----------------------------------------------------
        # 현재 자산
        # ----------------------------------------------------

        print_wallet(
            portfolio
        )


        # ----------------------------------------------------
        # 현재 종목
        # ----------------------------------------------------

        print_stocks(
            portfolio
        )


        # ----------------------------------------------------
        # 최근 기록
        # ----------------------------------------------------

        print_history(
            history,
            count=5
        )


        print()
        print("=" * 70)
        print("                ✅ 기록 완료")
        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 오류 발생")
        print("=" * 70)

        print(e)