from toss_api import (
    get_access_token,
    get_accounts,
    get_holdings,
    get_buying_power
)


# ============================================================
# ▲ ▼ 방향 표시
# ============================================================

def arrow(value):

    if value > 0:
        return "▲"

    elif value < 0:
        return "▼"

    else:
        return "─"


# ============================================================
# 🏦 WALLET 데이터 정리
# ============================================================

def build_wallet(
    holdings,
    buying_power_usd,
    buying_power_krw
):

    result = holdings["result"]

    # --------------------------------------------------------
    # 주식 관련 자산
    # --------------------------------------------------------

    total_purchase = float(
        result["totalPurchaseAmount"]["usd"]
    )

    market_value = float(
        result["marketValue"]["amount"]["usd"]
    )

    market_value_after_cost = float(
        result["marketValue"]["amountAfterCost"]["usd"]
    )

    profit_loss = float(
        result["profitLoss"]["amount"]["usd"]
    )

    profit_loss_after_cost = float(
        result["profitLoss"]["amountAfterCost"]["usd"]
    )

    daily_profit = float(
        result["dailyProfitLoss"]["amount"]["usd"]
    )

    daily_profit_rate = float(
        result["dailyProfitLoss"]["rate"]
    )

    # --------------------------------------------------------
    # 수익률 직접 계산
    # --------------------------------------------------------

    if total_purchase != 0:

        profit_rate = (
            profit_loss / total_purchase
        )

        profit_rate_after_cost = (
            profit_loss_after_cost / total_purchase
        )

    else:

        profit_rate = 0
        profit_rate_after_cost = 0


    # --------------------------------------------------------
    # USD 현금
    # --------------------------------------------------------

    usd_result = buying_power_usd.get(
        "result",
        {}
    )

    usd_cash = float(
        usd_result.get(
            "cashBuyingPower",
            0
        )
    )


    # --------------------------------------------------------
    # KRW 현금
    # --------------------------------------------------------

    krw_result = buying_power_krw.get(
        "result",
        {}
    )

    krw_cash = float(
        krw_result.get(
            "cashBuyingPower",
            0
        )
    )


    # --------------------------------------------------------
    # 총자산
    #
    # 현재는 USD 기준으로 계산
    # KRW 현금은 환율을 붙이기 전까지 별도 표시
    # --------------------------------------------------------

    total_usd_assets = (
        market_value + usd_cash
    )


    # --------------------------------------------------------
    # 현금 비중
    # --------------------------------------------------------

    if total_usd_assets != 0:

        cash_ratio = (
            usd_cash / total_usd_assets
        )

    else:

        cash_ratio = 0


    return {

        # 주식
        "total_purchase": total_purchase,
        "market_value": market_value,
        "market_value_after_cost": market_value_after_cost,

        # 손익
        "profit_loss": profit_loss,
        "profit_loss_after_cost": profit_loss_after_cost,

        # 수익률
        "profit_rate": profit_rate,
        "profit_rate_after_cost": profit_rate_after_cost,

        # 오늘
        "daily_profit": daily_profit,
        "daily_profit_rate": daily_profit_rate,

        # 현금
        "usd_cash": usd_cash,
        "krw_cash": krw_cash,

        # 총자산
        "total_usd_assets": total_usd_assets,

        # 현금 비중
        "cash_ratio": cash_ratio
    }


# ============================================================
# 📈 STOCKS 데이터 정리
# ============================================================

def build_stocks(holdings):

    items = holdings["result"]["items"]

    stocks = []

    for item in items:

        purchase_amount = float(
            item["marketValue"]["purchaseAmount"]
        )

        market_value = float(
            item["marketValue"]["amount"]
        )

        profit_loss = float(
            item["profitLoss"]["amount"]
        )

        # ----------------------------------------------------
        # 종목별 수익률 직접 계산
        # ----------------------------------------------------

        if purchase_amount != 0:

            profit_rate = (
                profit_loss / purchase_amount
            )

        else:

            profit_rate = 0


        stock = {

            "symbol": item["symbol"],

            "name": item["name"],

            "quantity": float(
                item["quantity"]
            ),

            "last_price": float(
                item["lastPrice"]
            ),

            "average_price": float(
                item["averagePurchasePrice"]
            ),

            "purchase_amount": purchase_amount,

            "market_value": market_value,

            "profit_loss": profit_loss,

            "profit_rate": profit_rate,

            "daily_profit": float(
                item["dailyProfitLoss"]["amount"]
            ),

            "daily_profit_rate": float(
                item["dailyProfitLoss"]["rate"]
            )
        }

        stocks.append(stock)

    return stocks


# ============================================================
# 🏦 WALLET 출력
# ============================================================

def print_wallet(wallet):

    print()
    print("=" * 60)
    print("                    🏦 WALLET")
    print("=" * 60)

    # --------------------------------------------------------
    # 총자산
    # --------------------------------------------------------

    print(
        f"총 주식 평가액 : "
        f"${wallet['market_value']:,.2f}"
    )

    print(
        f"총 자산        : "
        f"${wallet['total_usd_assets']:,.2f}"
    )

    print()

    # --------------------------------------------------------
    # 현금
    # --------------------------------------------------------

    print(
        f"💵 USD 현금     : "
        f"${wallet['usd_cash']:,.2f}"
    )

    print(
        f"🇰🇷 KRW 현금     : "
        f"₩{wallet['krw_cash']:,.0f}"
    )

    print(
        f"현금 비중       : "
        f"{wallet['cash_ratio'] * 100:.2f}%"
    )

    print()

    # --------------------------------------------------------
    # 투자금 / 손익
    # --------------------------------------------------------

    print(
        f"총 투자금       : "
        f"${wallet['total_purchase']:,.2f}"
    )

    print(
        f"총 손익         : "
        f"${wallet['profit_loss']:+,.2f} "
        f"{arrow(wallet['profit_loss'])}"
    )

    print(
        f"총 수익률       : "
        f"{wallet['profit_rate'] * 100:+.2f}% "
        f"{arrow(wallet['profit_rate'])}"
    )

    print()

    # --------------------------------------------------------
    # 오늘
    # --------------------------------------------------------

    print(
        f"오늘 손익       : "
        f"${wallet['daily_profit']:+,.2f} "
        f"{arrow(wallet['daily_profit'])}"
    )

    print(
        f"오늘 수익률     : "
        f"{wallet['daily_profit_rate'] * 100:+.2f}% "
        f"{arrow(wallet['daily_profit_rate'])}"
    )


# ============================================================
# 📈 STOCKS 출력
# ============================================================

def print_stocks(stocks):

    print()
    print("=" * 60)
    print("                    📈 STOCKS")
    print("=" * 60)

    for stock in stocks:

        print()

        print(
            f"📌 {stock['symbol']} "
            f"({stock['name']})"
        )

        print(
            f"수량         : "
            f"{stock['quantity']:.6f}주"
        )

        print(
            f"현재가       : "
            f"${stock['last_price']:,.2f}"
        )

        print(
            f"평균매수가   : "
            f"${stock['average_price']:,.2f}"
        )

        print(
            f"평가금액     : "
            f"${stock['market_value']:,.2f}"
        )

        print(
            f"손익         : "
            f"${stock['profit_loss']:+,.2f} "
            f"{arrow(stock['profit_loss'])}"
        )

        print(
            f"수익률       : "
            f"{stock['profit_rate'] * 100:+.2f}% "
            f"{arrow(stock['profit_rate'])}"
        )

        print(
            f"오늘         : "
            f"${stock['daily_profit']:+,.2f} "
            f"{arrow(stock['daily_profit'])}"
        )


# ============================================================
# 🚀 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("          MY INVESTMENT PORTFOLIO")
    print("=" * 60)

    try:

        # ====================================================
        # 🔐 토스 API 인증
        # ====================================================

        token = get_access_token()

        print()
        print("✅ 토스 API 인증 성공")


        # ====================================================
        # 🏦 계좌 확인
        # ====================================================

        accounts = get_accounts(token)

        account_list = accounts.get(
            "result",
            []
        )

        if not account_list:

            print()
            print("❌ 연결된 계좌가 없습니다.")
            exit()


        account = account_list[0]

        account_seq = account["accountSeq"]

        print()
        print("✅ 계좌 확인 성공")
        print(
            f"계좌 순번 : {account_seq}"
        )


        # ====================================================
        # 📈 보유 주식
        # ====================================================

        print()
        print("보유 주식을 조회하는 중...")

        holdings = get_holdings(
            token,
            account_seq
        )


        # ====================================================
        # 💵 USD 현금
        # ====================================================

        print()
        print(
            "USD 매수 가능 금액을 조회하는 중..."
        )

        buying_power_usd = get_buying_power(
            token,
            account_seq,
            "USD"
        )


        # ====================================================
        # 🇰🇷 KRW 현금
        # ====================================================

        print()
        print(
            "KRW 매수 가능 금액을 조회하는 중..."
        )

        buying_power_krw = get_buying_power(
            token,
            account_seq,
            "KRW"
        )


        # ====================================================
        # 📊 데이터 정리
        # ====================================================

        wallet = build_wallet(
            holdings,
            buying_power_usd,
            buying_power_krw
        )

        stocks = build_stocks(
            holdings
        )


        # ====================================================
        # 🏦 Wallet 출력
        # ====================================================

        print_wallet(
            wallet
        )


        # ====================================================
        # 📈 Stocks 출력
        # ====================================================

        print_stocks(
            stocks
        )


        # ====================================================
        # 완료
        # ====================================================

        print()
        print("=" * 60)
        print("                  분석 준비 완료")
        print("=" * 60)


    except Exception as e:

        print()
        print("=" * 60)
        print("❌ 오류 발생")
        print("=" * 60)

        print(e)