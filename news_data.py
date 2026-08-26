import json
import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote


# ============================================================
# 🦝 RACCOON NEWS DATA BUILDER
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "news_data.json")


# ============================================================
# 분석할 종목
# ============================================================

STOCKS = {
    "VOO": "VOO Vanguard S&P 500",
    "TTWO": "Take-Two Interactive TTWO",
    "JEPQ": "JEPQ ETF",
    "ALAB": "Astera Labs ALAB",
    "JOBY": "Joby Aviation JOBY"
}


# ============================================================
# Google News RSS
# ============================================================

def get_news(symbol, query, limit=5):

    encoded_query = quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/148.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    articles = []

    for item in root.findall(".//item"):

        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")
        source = item.findtext("source")

        if not title:
            continue

        articles.append({
            "symbol": symbol,
            "title": title.strip(),
            "source": source.strip() if source else "",
            "published": pub_date.strip() if pub_date else "",
            "url": link.strip() if link else ""
        })

        if len(articles) >= limit:
            break

    return articles


# ============================================================
# 전체 뉴스 수집
# ============================================================

def build_news():

    print()
    print("=" * 70)
    print("          🦝 NEWS DATA BUILDER")
    print("=" * 70)

    all_news = {}

    for symbol, query in STOCKS.items():

        print()
        print(f"🔎 {symbol} 뉴스 조회 중...")

        try:

            news = get_news(
                symbol,
                query,
                limit=5
            )

            all_news[symbol] = news

            print(
                f"✅ {symbol} "
                f"{len(news)}개 뉴스 수집"
            )

            for article in news:

                print(
                    f"   • {article['title']}"
                )

        except Exception as e:

            print(
                f"❌ {symbol} 뉴스 조회 실패"
            )

            print(
                f"   {e}"
            )

            all_news[symbol] = []

        # 너무 빠르게 연속 요청하지 않도록 잠깐 대기
        time.sleep(1)


    # ========================================================
    # AI가 읽기 좋은 구조
    # ========================================================

    result = {

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source": "Google News RSS",

        "stocks": all_news
    }


    # ========================================================
    # JSON 저장
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )


    return result


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    try:

        news_data = build_news()

        print()
        print("=" * 70)
        print("              📰 NEWS DATA")
        print("=" * 70)

        for symbol, articles in news_data["stocks"].items():

            print()
            print(f"📌 {symbol}")

            if not articles:

                print("   뉴스 없음")
                continue

            for article in articles:

                print()
                print(
                    f"   제목 : {article['title']}"
                )

                print(
                    f"   출처 : {article['source']}"
                )

                print(
                    f"   시간 : {article['published']}"
                )

                print(
                    f"   링크 : {article['url']}"
                )


        print()
        print("=" * 70)
        print(
            "💾 news_data.json 저장 완료"
        )
        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print("❌ 뉴스 수집 오류")
        print("=" * 70)

        print(type(e).__name__)
        print(e)