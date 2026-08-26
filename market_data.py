import os
import json
import time
import requests
from datetime import datetime


# ============================================================
# 🦝 RACCOON MARKET DATA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AI_PORTFOLIO_FILE = os.path.join(
    BASE_DIR,
    "ai_portfolio.json"
)

MARKET_DATA_FILE = os.path.join(
    BASE_DIR,
    "market_data.json"
)


# ============================================================
# 설정
# ============================================================

# Yahoo Finance의 공개 시세 API 사용
YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/"
)

TIMEOUT = 10


# ============================================================
# AI 포트폴리오 읽기
# ============================================================

def load_ai_portfolio():

    if not os.path.exists(
        AI_PORTFOLIO_FILE
    ):
        raise FileNotFoundError(
            "ai_portfolio.json을 찾을 수 없습니다."
        )

    with open(
        AI_PORTFOLIO_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# 종목 목록
# ============================================================

def get_symbols(portfolio):

    stocks = portfolio.get(
        "stocks",
        []
    )

    symbols = []

    for stock in stocks:

        symbol = stock.get(
            "symbol"
        )

        if symbol:
            symbols.append(
                symbol.upper()
            )

    return symbols


# ============================================================
# Yahoo Finance 시장 데이터
# ============================================================

def get_market_data(symbol):

    url = (
        YAHOO_URL
        + symbol
    )

    params = {
        "range": "1y",
        "interval": "1d"
    }

    headers = {
        "User-Agent":
            "Mozilla/5.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    result = data["chart"]["result"]

    if not result:
        raise Exception(
            f"{symbol}: 시장 데이터를 찾을 수 없습니다."
        )

    result = result[0]

    meta = result.get(
        "meta",
        {}
    )

    timestamps = result.get(
        "timestamp",
        []
    )

    indicators = result.get(
        "indicators",
        {}
    )

    quote_list = indicators.get(
        "quote",
        []
    )

    if not quote_list:
        raise Exception(
            f"{symbol}: 가격 데이터가 없습니다."
        )

    quote = quote_list[0]


    # --------------------------------------------------------
    # 현재 가격
    # --------------------------------------------------------

    current_price = meta.get(
        "regularMarketPrice"
    )

    previous_close = meta.get(
        "previousClose"
    )

    if current_price is None:

        closes = [
            x for x in quote.get(
                "close",
                []
            )
            if x is not None
        ]

        if closes:
            current_price = closes[-1]


    # --------------------------------------------------------
    # 전일 대비
    # --------------------------------------------------------

    change = None
    change_percent = None

    if (
        current_price is not None
        and previous_close is not None
        and previous_close != 0
    ):

        change = (
            current_price
            - previous_close
        )

        change_percent = (
            change
            / previous_close
        )


    # --------------------------------------------------------
    # 최근 거래 데이터
    # --------------------------------------------------------

    opens = quote.get(
        "open",
        []
    )

    highs = quote.get(
        "high",
        []
    )

    lows = quote.get(
        "low",
        []
    )

    closes = quote.get(
        "close",
        []
    )

    volumes = quote.get(
        "volume",
        []
    )


    # 마지막 유효 데이터
    latest_index = None

    for i in range(
        len(closes) - 1,
        -1,
        -1
    ):

        if closes[i] is not None:

            latest_index = i

            break


    latest_open = None
    latest_high = None
    latest_low = None
    latest_close = None
    latest_volume = None


    if latest_index is not None:

        latest_open = opens[
            latest_index
        ]

        latest_high = highs[
            latest_index
        ]

        latest_low = lows[
            latest_index
        ]

        latest_close = closes[
            latest_index
        ]

        latest_volume = volumes[
            latest_index
        ]


    # --------------------------------------------------------
    # 52주 고가 / 저가
    # --------------------------------------------------------

    valid_highs = [
        x for x in highs
        if x is not None
    ]

    valid_lows = [
        x for x in lows
        if x is not None
    ]

    high_52w = (
        max(valid_highs)
        if valid_highs
        else None
    )

    low_52w = (
        min(valid_lows)
        if valid_lows
        else None
    )


    # --------------------------------------------------------
    # 거래량 평균
    # --------------------------------------------------------

    valid_volumes = [
        x for x in volumes
        if x is not None
    ]

    average_volume = None

    if valid_volumes:

        recent_volumes = (
            valid_volumes[-20:]
        )

        average_volume = (
            sum(recent_volumes)
            / len(recent_volumes)
        )


    # --------------------------------------------------------
    # 52주 수익률
    # --------------------------------------------------------

    year_change = None

    if len(closes) > 1:

        first_valid = None

        for value in closes:

            if value is not None:

                first_valid = value

                break

        if (
            first_valid is not None
            and current_price is not None
            and first_valid != 0
        ):

            year_change = (
                current_price
                / first_valid
            ) - 1


    # --------------------------------------------------------
    # 데이터 반환
    # --------------------------------------------------------

    return {

        "symbol":
            symbol,

        "currency":
            meta.get(
                "currency",
                "USD"
            ),

        "exchange":
            meta.get(
                "exchangeName"
            ),

        "market_state":
            meta.get(
                "marketState"
            ),

        "current_price":
            current_price,

        "previous_close":
            previous_close,

        "change":
            change,

        "change_percent":
            change_percent,

        "today": {

            "open":
                latest_open,

            "high":
                latest_high,

            "low":
                latest_low,

            "close":
                latest_close,

            "volume":
                latest_volume
        },

        "52_week": {

            "high":
                high_52w,

            "low":
                low_52w,

            "change":
                year_change
        },

        "volume": {

            "latest":
                latest_volume,

            "average_20d":
                average_volume
        },

        "data_points":
            len(timestamps)
    }


# ============================================================
# 전체 시장 데이터
# ============================================================

def build_market_data():

    portfolio = load_ai_portfolio()

    symbols = get_symbols(
        portfolio
    )

    if not symbols:

        raise Exception(
            "ai_portfolio.json에서 "
            "종목을 찾을 수 없습니다."
        )


    market_data = {

        "generated_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "source":
            "Yahoo Finance",

        "stocks": {}
    }


    print()

    print(
        f"📡 총 {len(symbols)}개 "
        f"종목의 시장 데이터를 조회합니다."
    )


    for symbol in symbols:

        print()
        print(
            f"🔎 {symbol} 조회 중..."
        )

        try:

            data = get_market_data(
                symbol
            )

            market_data[
                "stocks"
            ][symbol] = data

            print(
                f"✅ {symbol} "
                f"${data['current_price']}"
            )

        except Exception as e:

            print(
                f"❌ {symbol} 오류: {e}"
            )

            market_data[
                "stocks"
            ][symbol] = {

                "symbol":
                    symbol,

                "error":
                    str(e)
            }


        # API 요청 간격
        time.sleep(0.5)


    return market_data


# ============================================================
# 저장
# ============================================================

def save_market_data(
    market_data
):

    with open(
        MARKET_DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            market_data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 요약 출력
# ============================================================

def print_summary(
    market_data
):

    print()
    print("=" * 70)
    print(
        "              📊 MARKET DATA"
    )
    print("=" * 70)


    stocks = market_data[
        "stocks"
    ]


    for symbol, data in stocks.items():

        print()

        if "error" in data:

            print(
                f"❌ {symbol}"
            )

            print(
                f"오류: "
                f"{data['error']}"
            )

            continue


        current_price = (
            data["current_price"]
        )

        change = (
            data["change"]
        )

        change_percent = (
            data["change_percent"]
        )

        volume = (
            data["volume"]["latest"]
        )

        high_52w = (
            data["52_week"]["high"]
        )

        low_52w = (
            data["52_week"]["low"]
        )


        print(
            f"📌 {symbol}"
        )

        print(
            f"현재가       : "
            f"${current_price:,.2f}"
        )


        if change is not None:

            print(
                f"전일 대비    : "
                f"${change:+,.2f}"
            )


        if change_percent is not None:

            print(
                f"등락률       : "
                f"{change_percent * 100:+.2f}%"
            )


        print(
            f"거래량       : "
            f"{volume:,}"
            if volume is not None
            else
            "거래량       : N/A"
        )


        print(
            f"52주 고가    : "
            f"${high_52w:,.2f}"
            if high_52w is not None
            else
            "52주 고가    : N/A"
        )


        print(
            f"52주 저가    : "
            f"${low_52w:,.2f}"
            if low_52w is not None
            else
            "52주 저가    : N/A"
        )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "          🦝 MARKET DATA BUILDER"
    )
    print("=" * 70)


    try:

        market_data = (
            build_market_data()
        )


        save_market_data(
            market_data
        )


        print_summary(
            market_data
        )


        print()
        print("=" * 70)
        print(
            "💾 market_data.json 저장 완료"
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