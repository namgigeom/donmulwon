import os
import requests
from dotenv import load_dotenv


# ============================================================
# 환경변수
# ============================================================

load_dotenv()

CLIENT_ID = os.getenv("TOSS_CLIENT_ID")
CLIENT_SECRET = os.getenv("TOSS_CLIENT_SECRET")

BASE_URL = "https://openapi.tossinvest.com"


# ============================================================
# 토스 API
# ============================================================

def get_access_token():

    url = f"{BASE_URL}/oauth2/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(
        url,
        data=data
    )

    response.raise_for_status()

    return response.json()["access_token"]


def get_accounts(token):

    url = f"{BASE_URL}/api/v1/accounts"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    return response.json()


def get_holdings(token, account_seq):

    url = f"{BASE_URL}/api/v1/holdings"

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tossinvest-Account": str(account_seq)
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    return response.json()


def get_buying_power(token, account_seq, currency):

    url = f"{BASE_URL}/api/v1/buying-power"

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tossinvest-Account": str(account_seq)
    }

    params = {
        "currency": currency
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# WALLET 생성
# ============================================================

def build_wallet(
    holdings,
    usd_cash,
    krw_cash
):

    result = holdings["result"]

    stock_value = float(
        result["marketValue"]["amount"]["usd"]
    )

    total_purchase = float(
        result["totalPurchaseAmount"]["usd"]
    )

    profit_loss = float(
        result["profitLoss"]["amount"]["usd"]
    )

    profit_rate = float(
        result["profitLoss"]["rateAfterCost"]
    )

    daily_profit = float(
        result["dailyProfitLoss"]["amount"]["usd"]
    )

    daily_profit_rate = float(
        result["dailyProfitLoss"]["rate"]
    )


    # 현재는 KRW → USD 환산을 하지 않는다.
    # 사용자가 원한 대로 USD와 KRW를 별도로 보관한다.
    #
    # 따라서 총자산(USD)은
    # 주식 평가액 + USD 현금으로 계산한다.

    total_assets = (
        stock_value +
        usd_cash
    )


    return {

        "total_assets": total_assets,

        "stock_value": stock_value,

        "usd_cash": usd_cash,

        "krw_cash": krw_cash,

        "total_purchase": total_purchase,

        "profit_loss": profit_loss,

        "profit_rate": profit_rate,

        "daily_profit": daily_profit,

        "daily_profit_rate": daily_profit_rate
    }


# ============================================================
# STOCKS 생성
# ============================================================

def build_stocks(holdings):

    items = holdings["result"]["items"]

    stocks = []

    for item in items:

        quantity = float(
            item["quantity"]
        )

        market_value = float(
            item["marketValue"]["amount"]
        )

        stock = {

            "symbol": item["symbol"],

            "name": item["name"],

            "quantity": quantity,

            "last_price": float(
                item["lastPrice"]
            ),

            "average_price": float(
                item["averagePurchasePrice"]
            ),

            "purchase_amount": float(
                item["marketValue"]["purchaseAmount"]
            ),

            "market_value": market_value,

            "profit_loss": float(
                item["profitLoss"]["amount"]
            ),

            "profit_rate": float(
                item["profitLoss"]["rateAfterCost"]
            ),

            "daily_profit": float(
                item["dailyProfitLoss"]["amount"]
            ),

            "daily_profit_rate": float(
                item["dailyProfitLoss"]["rate"]
            ),

            "portfolio_weight": 0
        }

        stocks.append(stock)


    # --------------------------------------------------------
    # 포트폴리오 비중
    # --------------------------------------------------------

    total_value = sum(
        stock["market_value"]
        for stock in stocks
    )


    if total_value > 0:

        for stock in stocks:

            stock["portfolio_weight"] = (
                stock["market_value"] /
                total_value
            )


    return stocks


# ============================================================
# 전체 포트폴리오
# ============================================================

def get_portfolio():

    # --------------------------------------------------------
    # 인증
    # --------------------------------------------------------

    token = get_access_token()


    # --------------------------------------------------------
    # 계좌
    # --------------------------------------------------------

    accounts = get_accounts(
        token
    )

    account_list = accounts.get(
        "result",
        []
    )


    if not account_list:

        raise Exception(
            "연결된 토스 증권 계좌가 없습니다."
        )


    account = account_list[0]

    account_seq = account["accountSeq"]


    # --------------------------------------------------------
    # 보유 주식
    # --------------------------------------------------------

    holdings = get_holdings(
        token,
        account_seq
    )


    # --------------------------------------------------------
    # USD 매수 가능 금액
    # --------------------------------------------------------

    usd_result = get_buying_power(
        token,
        account_seq,
        "USD"
    )

    usd_cash = float(
        usd_result["result"]["cashBuyingPower"]
    )


    # --------------------------------------------------------
    # KRW 매수 가능 금액
    # --------------------------------------------------------

    krw_result = get_buying_power(
        token,
        account_seq,
        "KRW"
    )

    krw_cash = float(
        krw_result["result"]["cashBuyingPower"]
    )


    # --------------------------------------------------------
    # 데이터 생성
    # --------------------------------------------------------

    wallet = build_wallet(
        holdings,
        usd_cash,
        krw_cash
    )

    stocks = build_stocks(
        holdings
    )


    # --------------------------------------------------------
    # AI가 사용할 전체 데이터
    # --------------------------------------------------------

    portfolio = {

        "wallet": wallet,

        "stocks": stocks
    }


    return portfolio


# ============================================================
# 직접 실행 테스트
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("          🦝 PORTFOLIO DATA MANAGER")
    print("=" * 70)


    try:

        portfolio = get_portfolio()

        wallet = portfolio["wallet"]

        stocks = portfolio["stocks"]


        print()
        print("=" * 70)
        print("                    🏦 WALLET")
        print("=" * 70)

        print(
            f"총 자산       : "
            f"${wallet['total_assets']:,.2f}"
        )

        print(
            f"주식 평가액   : "
            f"${wallet['stock_value']:,.2f}"
        )

        print(
            f"USD 현금      : "
            f"${wallet['usd_cash']:,.2f}"
        )

        print(
            f"KRW 현금      : "
            f"₩{wallet['krw_cash']:,.0f}"
        )

        print(
            f"총 손익       : "
            f"${wallet['profit_loss']:+,.2f}"
        )

        print(
            f"총 수익률     : "
            f"{wallet['profit_rate'] * 100:+.2f}%"
        )


        print()
        print("=" * 70)
        print("                    📈 STOCKS")
        print("=" * 70)


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
                f"평가금액   : "
                f"${stock['market_value']:,.2f}"
            )

            print(
                f"손익       : "
                f"${stock['profit_loss']:+,.2f}"
            )

            print(
                f"수익률     : "
                f"{stock['profit_rate'] * 100:+.2f}%"
            )

            print(
                f"포트폴리오 : "
                f"{stock['portfolio_weight'] * 100:.2f}%"
            )


        print()
        print("=" * 70)
        print("              ✅ 데이터 준비 완료")
        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 오류 발생")
        print("=" * 70)

        print(e)