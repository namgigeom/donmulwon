import os
import json
from datetime import datetime

from portfolio_data import get_portfolio


# ============================================================
# 🦝 AI PORTFOLIO DATA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AI_DATA_FILE = os.path.join(
    BASE_DIR,
    "ai_portfolio.json"
)

TRADE_HISTORY_FILE = os.path.join(
    BASE_DIR,
    "trade_history.json"
)


# ============================================================
# 거래 기록 불러오기
# ============================================================

def load_trade_history():

    if not os.path.exists(
        TRADE_HISTORY_FILE
    ):
        return []

    try:

        with open(
            TRADE_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        # 리스트 형태
        if isinstance(data, list):
            return data

        # 딕셔너리 안에 trades가 있는 경우
        if isinstance(data, dict):

            trades = data.get(
                "trades",
                []
            )

            if isinstance(trades, list):
                return trades

        return []

    except Exception as e:

        print(
            f"⚠️ 거래 기록 읽기 오류: {e}"
        )

        return []


# ============================================================
# AI용 데이터 생성
# ============================================================

def build_ai_portfolio():

    # --------------------------------------------------------
    # 현재 포트폴리오
    # --------------------------------------------------------

    portfolio = get_portfolio()

    wallet = portfolio["wallet"]

    stocks = portfolio["stocks"]


    # --------------------------------------------------------
    # 거래 기록
    # --------------------------------------------------------

    trade_history = load_trade_history()


    # --------------------------------------------------------
    # AI가 보기 쉽게 종목 정렬
    # --------------------------------------------------------

    stocks_sorted = sorted(
        stocks,
        key=lambda x: x["portfolio_weight"],
        reverse=True
    )


    # --------------------------------------------------------
    # AI 데이터
    # --------------------------------------------------------

    ai_data = {

        "generated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "wallet": {

            "total_assets":
                wallet["total_assets"],

            "stock_value":
                wallet["stock_value"],

            "usd_cash":
                wallet["usd_cash"],

            "krw_cash":
                wallet["krw_cash"],

            "total_purchase":
                wallet["total_purchase"],

            "profit_loss":
                wallet["profit_loss"],

            "profit_rate":
                wallet["profit_rate"],

            "daily_profit":
                wallet["daily_profit"],

            "daily_profit_rate":
                wallet["daily_profit_rate"]
        },

        "stocks": [],

        "recent_trades": trade_history[-20:]
    }


    # ========================================================
    # 종목 데이터
    # ========================================================

    for stock in stocks_sorted:

        ai_stock = {

            "symbol":
                stock["symbol"],

            "name":
                stock["name"],

            "quantity":
                stock["quantity"],

            "last_price":
                stock["last_price"],

            "average_price":
                stock["average_price"],

            "purchase_amount":
                stock["purchase_amount"],

            "market_value":
                stock["market_value"],

            "profit_loss":
                stock["profit_loss"],

            "profit_rate":
                stock["profit_rate"],

            "daily_profit":
                stock["daily_profit"],

            "daily_profit_rate":
                stock["daily_profit_rate"],

            "portfolio_weight":
                stock["portfolio_weight"]
        }


        ai_data["stocks"].append(
            ai_stock
        )


    return ai_data


# ============================================================
# AI 데이터 저장
# ============================================================

def save_ai_portfolio(ai_data):

    with open(
        AI_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            ai_data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 출력
# ============================================================

def print_ai_portfolio(ai_data):

    wallet = ai_data["wallet"]

    stocks = ai_data["stocks"]

    trades = ai_data["recent_trades"]


    print()
    print("=" * 70)
    print("              🤖 AI PORTFOLIO DATA")
    print("=" * 70)


    print()
    print("[WALLET]")

    print(
        f"총자산       : "
        f"${wallet['total_assets']:,.2f}"
    )

    print(
        f"주식 평가액  : "
        f"${wallet['stock_value']:,.2f}"
    )

    print(
        f"USD 현금     : "
        f"${wallet['usd_cash']:,.2f}"
    )

    print(
        f"KRW 현금     : "
        f"₩{wallet['krw_cash']:,.0f}"
    )

    print(
        f"총 투자금    : "
        f"${wallet['total_purchase']:,.2f}"
    )

    print(
        f"총 손익      : "
        f"${wallet['profit_loss']:+,.2f}"
    )

    print(
        f"총 수익률    : "
        f"{wallet['profit_rate'] * 100:+.2f}%"
    )

    print(
        f"오늘 손익    : "
        f"${wallet['daily_profit']:+,.2f}"
    )

    print(
        f"오늘 수익률  : "
        f"{wallet['daily_profit_rate'] * 100:+.2f}%"
    )


    print()
    print("[STOCKS]")


    for stock in stocks:

        print()
        print(
            f"종목: {stock['symbol']}"
        )

        print(
            f"회사명: {stock['name']}"
        )

        print(
            f"수량: "
            f"{stock['quantity']:.6f}주"
        )

        print(
            f"현재가: "
            f"${stock['last_price']:,.4f}"
        )

        print(
            f"평균매수가: "
            f"${stock['average_price']:,.4f}"
        )

        print(
            f"평가금액: "
            f"${stock['market_value']:,.2f}"
        )

        print(
            f"손익: "
            f"${stock['profit_loss']:+,.2f}"
        )

        print(
            f"수익률: "
            f"{stock['profit_rate'] * 100:+.2f}%"
        )

        print(
            f"오늘 손익: "
            f"${stock['daily_profit']:+,.2f}"
        )

        print(
            f"포트폴리오 비중: "
            f"{stock['portfolio_weight'] * 100:.2f}%"
        )


    print()
    print("[RECENT TRADES]")

    if not trades:

        print(
            "최근 거래 없음"
        )

    else:

        for trade in trades[-10:]:

            print(
                trade
            )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("          🦝 AI PORTFOLIO DATA BUILDER")
    print("=" * 70)


    try:

        print()
        print(
            "📡 토스 계좌에서 "
            "최신 데이터를 가져오는 중..."
        )


        ai_data = build_ai_portfolio()


        save_ai_portfolio(
            ai_data
        )


        print_ai_portfolio(
            ai_data
        )


        print()
        print("=" * 70)
        print(
            "💾 ai_portfolio.json 저장 완료"
        )
        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 오류 발생")
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )