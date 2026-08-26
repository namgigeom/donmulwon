import json
import os
from datetime import datetime


# ============================================================
# 설정
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATE_FILE = os.path.join(
    BASE_DIR,
    "portfolio_state.json"
)


# ============================================================
# 숫자 안전 변환
# ============================================================

def safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


# ============================================================
# 이전 상태 불러오기
# ============================================================

def load_previous_state():

    if not os.path.exists(STATE_FILE):

        return None

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        print(
            f"⚠️ 이전 상태 파일을 읽을 수 없습니다: {e}"
        )

        return None


# ============================================================
# 현재 상태 저장
# ============================================================

def save_current_state(portfolio):

    wallet = portfolio["wallet"]
    stocks = portfolio["stocks"]

    state = {

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "wallet": {

            "total_assets":
                safe_float(
                    wallet["total_assets"]
                ),

            "stock_value":
                safe_float(
                    wallet["stock_value"]
                ),

            "usd_cash":
                safe_float(
                    wallet["usd_cash"]
                ),

            "krw_cash":
                safe_float(
                    wallet["krw_cash"]
                ),

            "total_purchase":
                safe_float(
                    wallet["total_purchase"]
                ),

            "profit_loss":
                safe_float(
                    wallet["profit_loss"]
                ),

            "profit_rate":
                safe_float(
                    wallet["profit_rate"]
                ),

            "daily_profit":
                safe_float(
                    wallet["daily_profit"]
                ),

            "daily_profit_rate":
                safe_float(
                    wallet["daily_profit_rate"]
                )
        },

        "stocks": {}

    }


    for stock in stocks:

        symbol = stock["symbol"]

        state["stocks"][symbol] = {

            "symbol": symbol,

            "name":
                stock["name"],

            "quantity":
                safe_float(
                    stock["quantity"]
                ),

            "last_price":
                safe_float(
                    stock["last_price"]
                ),

            "average_price":
                safe_float(
                    stock["average_price"]
                ),

            "market_value":
                safe_float(
                    stock["market_value"]
                ),

            "profit_loss":
                safe_float(
                    stock["profit_loss"]
                ),

            "profit_rate":
                safe_float(
                    stock["profit_rate"]
                ),

            "daily_profit":
                safe_float(
                    stock["daily_profit"]
                ),

            "portfolio_weight":
                safe_float(
                    stock["portfolio_weight"]
                )
        }


    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 변화 감지
# ============================================================

def detect_changes(previous, current):

    changes = []


    # ========================================================
    # 최초 실행
    # ========================================================

    if previous is None:

        changes.append({

            "type": "INITIAL",

            "message":
                "최초 실행 - 현재 상태를 기준점으로 저장"
        })

        return changes


    # ========================================================
    # WALLET
    # ========================================================

    old_wallet = previous.get(
        "wallet",
        {}
    )

    new_wallet = current["wallet"]


    # --------------------------------------------------------
    # 총자산
    # --------------------------------------------------------

    old_assets = safe_float(
        old_wallet.get(
            "total_assets",
            0
        )
    )

    new_assets = safe_float(
        new_wallet["total_assets"]
    )

    asset_change = (
        new_assets -
        old_assets
    )


    if abs(asset_change) > 0.000001:

        changes.append({

            "type": "ASSET_CHANGE",

            "old": old_assets,

            "new": new_assets,

            "change": asset_change
        })


    # --------------------------------------------------------
    # USD 현금
    # --------------------------------------------------------

    old_usd = safe_float(
        old_wallet.get(
            "usd_cash",
            0
        )
    )

    new_usd = safe_float(
        new_wallet["usd_cash"]
    )

    usd_change = (
        new_usd -
        old_usd
    )


    if abs(usd_change) > 0.000001:

        changes.append({

            "type": "USD_CASH_CHANGE",

            "old": old_usd,

            "new": new_usd,

            "change": usd_change
        })


    # --------------------------------------------------------
    # KRW 현금
    # --------------------------------------------------------

    old_krw = safe_float(
        old_wallet.get(
            "krw_cash",
            0
        )
    )

    new_krw = safe_float(
        new_wallet["krw_cash"]
    )

    krw_change = (
        new_krw -
        old_krw
    )


    if abs(krw_change) > 0.5:

        changes.append({

            "type": "KRW_CASH_CHANGE",

            "old": old_krw,

            "new": new_krw,

            "change": krw_change
        })


    # ========================================================
    # STOCKS
    # ========================================================

    old_stocks = previous.get(
        "stocks",
        {}
    )

    new_stocks = {}

    for stock in current["stocks"]:

        new_stocks[
            stock["symbol"]
        ] = stock


    all_symbols = (
        set(old_stocks.keys())
        |
        set(new_stocks.keys())
    )


    for symbol in sorted(all_symbols):

        old_stock = old_stocks.get(
            symbol
        )

        new_stock = new_stocks.get(
            symbol
        )


        # ====================================================
        # 신규 종목
        # ====================================================

        if old_stock is None and new_stock is not None:

            changes.append({

                "type": "NEW_POSITION",

                "symbol":
                    symbol,

                "name":
                    new_stock["name"],

                "quantity":
                    safe_float(
                        new_stock["quantity"]
                    )
            })

            continue


        # ====================================================
        # 완전 매도
        # ====================================================

        if old_stock is not None and new_stock is None:

            changes.append({

                "type": "CLOSED_POSITION",

                "symbol":
                    symbol,

                "name":
                    old_stock.get(
                        "name",
                        ""
                    ),

                "quantity":
                    safe_float(
                        old_stock.get(
                            "quantity",
                            0
                        )
                    )
            })

            continue


        if old_stock is None or new_stock is None:

            continue


        # ====================================================
        # 수량 변화
        # ====================================================

        old_quantity = safe_float(
            old_stock.get(
                "quantity",
                0
            )
        )

        new_quantity = safe_float(
            new_stock["quantity"]
        )

        quantity_change = (
            new_quantity -
            old_quantity
        )


        if abs(quantity_change) > 0.000001:

            if quantity_change > 0:

                changes.append({

                    "type": "BUY",

                    "symbol":
                        symbol,

                    "name":
                        new_stock["name"],

                    "old_quantity":
                        old_quantity,

                    "new_quantity":
                        new_quantity,

                    "quantity_change":
                        quantity_change
                })

            else:

                changes.append({

                    "type": "SELL",

                    "symbol":
                        symbol,

                    "name":
                        new_stock["name"],

                    "old_quantity":
                        old_quantity,

                    "new_quantity":
                        new_quantity,

                    "quantity_change":
                        quantity_change
                })


        # ====================================================
        # 가격 변화
        # ====================================================

        old_price = safe_float(
            old_stock.get(
                "last_price",
                0
            )
        )

        new_price = safe_float(
            new_stock["last_price"]
        )

        price_change = (
            new_price -
            old_price
        )


        # 수량 변화가 없을 때만
        # 순수한 가격 변화로 판단

        if (
            abs(price_change) > 0.000001
            and
            abs(quantity_change) <= 0.000001
        ):

            changes.append({

                "type": "PRICE_CHANGE",

                "symbol":
                    symbol,

                "name":
                    new_stock["name"],

                "old_price":
                    old_price,

                "new_price":
                    new_price,

                "price_change":
                    price_change
            })


        # ====================================================
        # 포트폴리오 비중 변화
        # ====================================================

        old_weight = safe_float(
            old_stock.get(
                "portfolio_weight",
                0
            )
        )

        new_weight = safe_float(
            new_stock["portfolio_weight"]
        )

        weight_change = (
            new_weight -
            old_weight
        )


        if abs(weight_change) >= 0.005:

            changes.append({

                "type": "WEIGHT_CHANGE",

                "symbol":
                    symbol,

                "name":
                    new_stock["name"],

                "old_weight":
                    old_weight,

                "new_weight":
                    new_weight,

                "weight_change":
                    weight_change
            })


    return changes


# ============================================================
# 변화 출력
# ============================================================

def print_changes(changes):

    print()
    print("=" * 70)
    print("                 🦝 PORTFOLIO CHANGE")
    print("=" * 70)


    if not changes:

        print()
        print("변화 없음")

        return


    for change in changes:

        change_type = change["type"]


        # ----------------------------------------------------
        # 최초 실행
        # ----------------------------------------------------

        if change_type == "INITIAL":

            print()
            print("🆕 최초 실행")

            print(
                change["message"]
            )


        # ----------------------------------------------------
        # 매수
        # ----------------------------------------------------

        elif change_type == "BUY":

            print()
            print(
                f"🟢 매수 감지 : "
                f"{change['symbol']} "
                f"({change['name']})"
            )

            print(
                f"수량 : "
                f"{change['old_quantity']:.6f}"
                f" → "
                f"{change['new_quantity']:.6f}"
            )

            print(
                f"변화 : "
                f"+{change['quantity_change']:.6f}주"
            )


        # ----------------------------------------------------
        # 매도
        # ----------------------------------------------------

        elif change_type == "SELL":

            print()
            print(
                f"🔴 매도 감지 : "
                f"{change['symbol']} "
                f"({change['name']})"
            )

            print(
                f"수량 : "
                f"{change['old_quantity']:.6f}"
                f" → "
                f"{change['new_quantity']:.6f}"
            )

            print(
                f"변화 : "
                f"{change['quantity_change']:.6f}주"
            )


        # ----------------------------------------------------
        # 신규 종목
        # ----------------------------------------------------

        elif change_type == "NEW_POSITION":

            print()
            print(
                f"🆕 신규 종목 : "
                f"{change['symbol']} "
                f"({change['name']})"
            )

            print(
                f"수량 : "
                f"{change['quantity']:.6f}주"
            )


        # ----------------------------------------------------
        # 완전 매도
        # ----------------------------------------------------

        elif change_type == "CLOSED_POSITION":

            print()
            print(
                f"🔴 종목 청산 : "
                f"{change['symbol']} "
                f"({change['name']})"
            )

            print(
                f"기존 수량 : "
                f"{change['quantity']:.6f}주"
            )


        # ----------------------------------------------------
        # 가격 변화
        # ----------------------------------------------------

        elif change_type == "PRICE_CHANGE":

            direction = (
                "▲"
                if change["price_change"] > 0
                else "▼"
            )

            print()
            print(
                f"📈 가격 변화 : "
                f"{change['symbol']} "
                f"({change['name']})"
            )

            print(
                f"현재가 : "
                f"${change['old_price']:.2f}"
                f" → "
                f"${change['new_price']:.2f}"
            )

            print(
                f"변화 : "
                f"${change['price_change']:+.2f} "
                f"{direction}"
            )


        # ----------------------------------------------------
        # 총자산 변화
        # ----------------------------------------------------

        elif change_type == "ASSET_CHANGE":

            direction = (
                "▲"
                if change["change"] > 0
                else "▼"
            )

            print()
            print("💼 총자산 변화")

            print(
                f"${change['old']:,.2f}"
                f" → "
                f"${change['new']:,.2f}"
            )

            print(
                f"변화 : "
                f"${change['change']:+,.2f} "
                f"{direction}"
            )


        # ----------------------------------------------------
        # USD 현금 변화
        # ----------------------------------------------------

        elif change_type == "USD_CASH_CHANGE":

            direction = (
                "▲"
                if change["change"] > 0
                else "▼"
            )

            print()
            print("💵 USD 현금 변화")

            print(
                f"${change['old']:,.2f}"
                f" → "
                f"${change['new']:,.2f}"
            )

            print(
                f"변화 : "
                f"${change['change']:+,.2f} "
                f"{direction}"
            )


        # ----------------------------------------------------
        # KRW 현금 변화
        # ----------------------------------------------------

        elif change_type == "KRW_CASH_CHANGE":

            direction = (
                "▲"
                if change["change"] > 0
                else "▼"
            )

            print()
            print("🇰🇷 KRW 현금 변화")

            print(
                f"₩{change['old']:,.0f}"
                f" → "
                f"₩{change['new']:,.0f}"
            )

            print(
                f"변화 : "
                f"₩{change['change']:+,.0f} "
                f"{direction}"
            )


        # ----------------------------------------------------
        # 비중 변화
        # ----------------------------------------------------

        elif change_type == "WEIGHT_CHANGE":

            direction = (
                "▲"
                if change["weight_change"] > 0
                else "▼"
            )

            print()
            print(
                f"⚖️ 비중 변화 : "
                f"{change['symbol']}"
            )

            print(
                f"비중 : "
                f"{change['old_weight'] * 100:.2f}%"
                f" → "
                f"{change['new_weight'] * 100:.2f}%"
            )

            print(
                f"변화 : "
                f"{change['weight_change'] * 100:+.2f}%p "
                f"{direction}"
            )


# ============================================================
# monitor.py에서 사용할 메인 함수
# ============================================================

def process_portfolio(portfolio):

    previous = load_previous_state()

    current = {

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "wallet":
            portfolio["wallet"],

        "stocks": {}
    }


    for stock in portfolio["stocks"]:

        current["stocks"][
            stock["symbol"]
        ] = {

            "symbol":
                stock["symbol"],

            "name":
                stock["name"],

            "quantity":
                safe_float(
                    stock["quantity"]
                ),

            "last_price":
                safe_float(
                    stock["last_price"]
                ),

            "average_price":
                safe_float(
                    stock["average_price"]
                ),

            "market_value":
                safe_float(
                    stock["market_value"]
                ),

            "profit_loss":
                safe_float(
                    stock["profit_loss"]
                ),

            "profit_rate":
                safe_float(
                    stock["profit_rate"]
                ),

            "daily_profit":
                safe_float(
                    stock["daily_profit"]
                ),

            "portfolio_weight":
                safe_float(
                    stock["portfolio_weight"]
                )
        }


    changes = detect_changes(
        previous,
        current
    )


    save_current_state(
        current
    )


    return changes, current


# ============================================================
# 직접 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("              🦝 CHANGE DETECTOR")
    print("=" * 70)

    previous = load_previous_state()


    if previous is None:

        print()
        print("📭 이전 포트폴리오 기록이 없습니다.")

    else:

        print()
        print("📂 이전 포트폴리오 기록을 찾았습니다.")

        print(
            f"기록 시간 : "
            f"{previous.get('timestamp', '알 수 없음')}"
        )