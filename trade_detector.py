import os
import json
from datetime import datetime


# ============================================================
# 🦝 TRADE DETECTOR
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATE_FILE = os.path.join(
    BASE_DIR,
    "portfolio_state.json"
)

TRADE_HISTORY_FILE = os.path.join(
    BASE_DIR,
    "trade_history.json"
)


# ============================================================
# JSON 불러오기
# ============================================================

def load_json(file_path):

    if not os.path.exists(file_path):
        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(f"❌ JSON 읽기 오류: {e}")

        return None


# ============================================================
# JSON 저장
# ============================================================

def save_json(file_path, data):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 종목 데이터를 dictionary 형태로 변환
# ============================================================

def stocks_to_dict(stocks):

    result = {}


    # --------------------------------------------------------
    # stocks가 리스트인 경우
    # --------------------------------------------------------

    if isinstance(stocks, list):

        for stock in stocks:

            if not isinstance(stock, dict):
                continue

            symbol = stock.get("symbol")

            if symbol:

                result[symbol] = stock


    # --------------------------------------------------------
    # stocks가 dictionary인 경우
    # --------------------------------------------------------

    elif isinstance(stocks, dict):

        for symbol, stock in stocks.items():

            if isinstance(stock, dict):

                if "symbol" not in stock:

                    stock["symbol"] = symbol

                result[symbol] = stock


    return result


# ============================================================
# 포트폴리오에서 stocks 추출
# ============================================================

def get_stocks(portfolio):

    if not isinstance(portfolio, dict):
        return {}


    stocks = portfolio.get(
        "stocks",
        []
    )


    return stocks_to_dict(
        stocks
    )


# ============================================================
# 거래 감지
# ============================================================

def detect_trades(
    previous,
    current
):

    trades = []


    previous_stocks = get_stocks(
        previous
    )

    current_stocks = get_stocks(
        current
    )


    # ========================================================
    # 현재 존재하는 종목 확인
    # ========================================================

    for symbol, current_stock in current_stocks.items():

        current_quantity = float(
            current_stock.get(
                "quantity",
                0
            )
        )


        # ----------------------------------------------------
        # 신규 종목
        # ----------------------------------------------------

        if symbol not in previous_stocks:

            if current_quantity > 0:

                trades.append({

                    "time":
                        datetime.now().isoformat(
                            timespec="seconds"
                        ),

                    "type":
                        "BUY",

                    "action":
                        "NEW_POSITION",

                    "symbol":
                        symbol,

                    "name":
                        current_stock.get(
                            "name",
                            ""
                        ),

                    "quantity":
                        current_quantity,

                    "previous_quantity":
                        0,

                    "current_quantity":
                        current_quantity,

                    "price":
                        current_stock.get(
                            "last_price",
                            0
                        ),

                    "message":
                        f"{symbol} 신규 매수 감지"
                })

            continue


        # ----------------------------------------------------
        # 기존 종목
        # ----------------------------------------------------

        previous_stock = previous_stocks[
            symbol
        ]


        previous_quantity = float(
            previous_stock.get(
                "quantity",
                0
            )
        )


        quantity_change = (
            current_quantity
            -
            previous_quantity
        )


        # ----------------------------------------------------
        # 추가 매수
        # ----------------------------------------------------

        if quantity_change > 0:

            trades.append({

                "time":
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),

                "type":
                    "BUY",

                "action":
                    "ADD_POSITION",

                "symbol":
                    symbol,

                "name":
                    current_stock.get(
                        "name",
                        ""
                    ),

                "quantity":
                    quantity_change,

                "previous_quantity":
                    previous_quantity,

                "current_quantity":
                    current_quantity,

                "price":
                    current_stock.get(
                        "last_price",
                        0
                    ),

                "message":
                    f"{symbol} 추가 매수 감지"
            })


        # ----------------------------------------------------
        # 일부 매도
        # ----------------------------------------------------

        elif quantity_change < 0:

            sold_quantity = abs(
                quantity_change
            )


            trades.append({

                "time":
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),

                "type":
                    "SELL",

                "action":
                    "REDUCE_POSITION",

                "symbol":
                    symbol,

                "name":
                    current_stock.get(
                        "name",
                        ""
                    ),

                "quantity":
                    sold_quantity,

                "previous_quantity":
                    previous_quantity,

                "current_quantity":
                    current_quantity,

                "price":
                    current_stock.get(
                        "last_price",
                        0
                    ),

                "message":
                    f"{symbol} 일부 매도 감지"
            })


    # ========================================================
    # 기존 종목이 사라진 경우
    # ========================================================

    for symbol, previous_stock in previous_stocks.items():

        if symbol not in current_stocks:

            previous_quantity = float(
                previous_stock.get(
                    "quantity",
                    0
                )
            )


            if previous_quantity > 0:

                trades.append({

                    "time":
                        datetime.now().isoformat(
                            timespec="seconds"
                        ),

                    "type":
                        "SELL",

                    "action":
                        "CLOSE_POSITION",

                    "symbol":
                        symbol,

                    "name":
                        previous_stock.get(
                            "name",
                            ""
                        ),

                    "quantity":
                        previous_quantity,

                    "previous_quantity":
                        previous_quantity,

                    "current_quantity":
                        0,

                    "price":
                        0,

                    "message":
                        f"{symbol} 전량 매도 감지"
                })


    return trades


# ============================================================
# 거래 기록 저장
# ============================================================

def save_trade_history(trades):

    history = load_json(
        TRADE_HISTORY_FILE
    )


    if history is None:

        history = []


    if not isinstance(history, list):

        history = []


    history.extend(
        trades
    )


    save_json(
        TRADE_HISTORY_FILE,
        history
    )


# ============================================================
# 거래 결과 출력
# ============================================================

def print_trades(trades):

    print()

    print("=" * 70)
    print("                 🚨 거래 감지 결과")
    print("=" * 70)


    if not trades:

        print()

        print(
            "📭 새로운 거래가 감지되지 않았습니다."
        )

        return


    for trade in trades:

        print()


        if trade["type"] == "BUY":

            print("🟢 매수 감지")

        else:

            print("🔴 매도 감지")


        print(
            f"종목       : "
            f"{trade['symbol']}"
        )

        print(
            f"종류       : "
            f"{trade['action']}"
        )

        print(
            f"수량       : "
            f"{trade['quantity']:.6f}주"
        )

        print(
            f"이전 수량  : "
            f"{trade['previous_quantity']:.6f}주"
        )

        print(
            f"현재 수량  : "
            f"{trade['current_quantity']:.6f}주"
        )

        print(
            f"가격       : "
            f"${float(trade.get('price', 0)):,.2f}"
        )

        print(
            f"메시지     : "
            f"{trade['message']}"
        )

        print(
            f"시간       : "
            f"{trade['time']}"
        )


# ============================================================
# 현재 포트폴리오와 이전 포트폴리오 비교
# ============================================================

def detect_current_portfolio(
    current_portfolio
):

    print("=" * 70)
    print("              🦝 TRADE DETECTOR")
    print("=" * 70)


    previous_portfolio = load_json(
        STATE_FILE
    )


    # ========================================================
    # 이전 기록 없음
    # ========================================================

    if previous_portfolio is None:

        print()

        print(
            "📭 이전 포트폴리오 기록이 없습니다."
        )

        print()

        print(
            "현재 포트폴리오를 기준점으로 사용합니다."
        )

        return []


    # ========================================================
    # 거래 감지
    # ========================================================

    trades = detect_trades(
        previous_portfolio,
        current_portfolio
    )


    # ========================================================
    # 결과 출력
    # ========================================================

    print_trades(
        trades
    )


    # ========================================================
    # 거래 기록 저장
    # ========================================================

    if trades:

        save_trade_history(
            trades
        )

        print()

        print(
            "💾 거래 기록 저장 완료"
        )


    return trades


# ============================================================
# 직접 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("              🦝 TRADE DETECTOR")
    print("=" * 70)


    current_portfolio = load_json(
        STATE_FILE
    )


    if current_portfolio is None:

        print()

        print(
            "📭 portfolio_state.json이 없습니다."
        )

        print()

        print(
            "먼저 monitor.py를 실행해주세요."
        )


    else:

        print()

        print(
            "현재 저장된 포트폴리오를"
        )

        print(
            "기준으로 거래 감지를 테스트합니다."
        )


        print()

        detect_current_portfolio(
            current_portfolio
        )