import os
import json
import time
from datetime import datetime

from portfolio_data import get_portfolio
from trade_detector import detect_trades, save_trade_history


# ============================================================
# 🦝 RACCOON PORTFOLIO MONITOR
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATE_FILE = os.path.join(
    BASE_DIR,
    "portfolio_state.json"
)


CHECK_INTERVAL = 60


# ============================================================
# JSON 불러오기
# ============================================================

def load_state():

    if not os.path.exists(STATE_FILE):
        return None

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            f"⚠️ 상태 파일 읽기 오류: {e}"
        )

        return None


# ============================================================
# 현재 상태 저장
# ============================================================

def save_state(portfolio):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            portfolio,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 화살표
# ============================================================

def arrow(value):

    if value > 0:
        return "▲"

    elif value < 0:
        return "▼"

    return "─"


# ============================================================
# 현재 포트폴리오 출력
# ============================================================

def print_portfolio(portfolio):

    wallet = portfolio["wallet"]

    stocks = portfolio["stocks"]


    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    print()
    print("=" * 70)
    print("                 📡 CURRENT PORTFOLIO")
    print("=" * 70)

    print(
        f"시간         : {now}"
    )

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
        f"총 손익      : "
        f"${wallet['profit_loss']:+,.2f} "
        f"{arrow(wallet['profit_loss'])}"
    )

    print(
        f"오늘 손익    : "
        f"${wallet['daily_profit']:+,.2f} "
        f"{arrow(wallet['daily_profit'])}"
    )


# ============================================================
# 거래 결과 출력
# ============================================================

def print_trades(trades):

    if not trades:
        return


    print()
    print("=" * 70)
    print("                 🚨 TRADE DETECTED")
    print("=" * 70)


    for trade in trades:

        if trade["type"] == "BUY":

            icon = "🟢"

        else:

            icon = "🔴"


        print()
        print(
            f"{icon} {trade['type']} "
            f"{trade['symbol']}"
        )

        print(
            f"종류         : "
            f"{trade['action']}"
        )

        print(
            f"수량         : "
            f"{trade['quantity']:.6f}주"
        )

        print(
            f"이전 수량    : "
            f"{trade['previous_quantity']:.6f}주"
        )

        print(
            f"현재 수량    : "
            f"{trade['current_quantity']:.6f}주"
        )

        print(
            f"가격         : "
            f"${float(trade.get('price', 0)):,.2f}"
        )

        print(
            f"메시지       : "
            f"{trade['message']}"
        )


# ============================================================
# 한 번의 모니터링
# ============================================================

def monitor_once():

    print()
    print("📡 토스 계좌 확인 중...")


    # --------------------------------------------------------
    # 최신 포트폴리오 조회
    # --------------------------------------------------------

    current_portfolio = get_portfolio()


    # --------------------------------------------------------
    # 현재 포트폴리오 출력
    # --------------------------------------------------------

    print_portfolio(
        current_portfolio
    )


    # --------------------------------------------------------
    # 이전 상태 불러오기
    # --------------------------------------------------------

    previous_portfolio = load_state()


    # ========================================================
    # 최초 실행
    # ========================================================

    if previous_portfolio is None:

        print()
        print("=" * 70)
        print("                 🆕 최초 실행")
        print("=" * 70)

        print(
            "현재 포트폴리오를 기준점으로 저장합니다."
        )

        save_state(
            current_portfolio
        )

        print()
        print(
            "💾 현재 상태 저장 완료"
        )

        return


    # ========================================================
    # 거래 감지
    # ========================================================

    trades = detect_trades(
        previous_portfolio,
        current_portfolio
    )


    # --------------------------------------------------------
    # 거래가 있는 경우
    # --------------------------------------------------------

    if trades:

        print_trades(
            trades
        )

        save_trade_history(
            trades
        )

        print()
        print(
            "💾 거래 기록 저장 완료"
        )


    # --------------------------------------------------------
    # 거래가 없는 경우
    # --------------------------------------------------------

    else:

        print()
        print(
            "📭 거래 변화 없음"
        )


    # ========================================================
    # 현재 상태 저장
    # ========================================================

    save_state(
        current_portfolio
    )

    print()
    print(
        "💾 현재 상태 갱신 완료"
    )


# ============================================================
# 메인 모니터링
# ============================================================

def main():

    print("=" * 70)
    print("              🦝 RACCOON PORTFOLIO MONITOR")
    print("=" * 70)

    print()
    print(
        f"⏱️ {CHECK_INTERVAL}초마다 "
        "토스 계좌를 확인합니다."
    )

    print()
    print(
        "종료하려면 Ctrl + C"
    )


    while True:

        try:

            monitor_once()


            print()
            print("=" * 70)

            print(
                f"다음 확인까지 "
                f"{CHECK_INTERVAL}초 대기..."
            )

            print("=" * 70)


            time.sleep(
                CHECK_INTERVAL
            )


        except KeyboardInterrupt:

            print()
            print()
            print("=" * 70)
            print(
                "🛑 모니터링을 종료합니다."
            )
            print("=" * 70)

            break


        except Exception as e:

            print()
            print("=" * 70)
            print("❌ 모니터링 오류")
            print("=" * 70)

            print(
                f"{type(e).__name__}: {e}"
            )

            print()
            print(
                f"{CHECK_INTERVAL}초 후 "
                "다시 시도합니다."
            )

            time.sleep(
                CHECK_INTERVAL
            )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    main()