import os
import requests
from dotenv import load_dotenv


# ============================================================
# 1. 환경변수
# ============================================================

load_dotenv()

CLIENT_ID = os.getenv("TOSS_CLIENT_ID")
CLIENT_SECRET = os.getenv("TOSS_CLIENT_SECRET")

BASE_URL = "https://openapi.tossinvest.com"


# ============================================================
# 2. Access Token 발급
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

    result = response.json()

    return result["access_token"]


# ============================================================
# 3. 계좌 목록 조회
# ============================================================

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


# ============================================================
# 4. 보유 주식 조회
# ============================================================

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


# ============================================================
# 5. 매수 가능 금액 조회
#
# currency:
# USD = 미국 주식용
# KRW = 원화
# ============================================================

def get_buying_power(
    token,
    account_seq,
    currency="USD"
):

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
# 6. 프로그램 시작
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("        TOSS SECURITIES ACCOUNT TEST")
    print("=" * 60)


    try:

        # ====================================================
        # 🔐 인증
        # ====================================================

        token = get_access_token()

        print()
        print("✅ 토스 API 인증 성공")


        # ====================================================
        # 🏦 계좌 조회
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
        print(f"계좌 순번 : {account_seq}")


        # ====================================================
        # 📈 보유 주식 조회
        # ====================================================

        print()
        print("보유 주식을 조회하는 중...")

        holdings = get_holdings(
            token,
            account_seq
        )

        print()
        print("=" * 60)
        print("                 📈 보유 주식")
        print("=" * 60)

        print(holdings)


        # ====================================================
        # 💵 USD 매수 가능 금액
        # ====================================================

        print()
        print("USD 매수 가능 금액을 조회하는 중...")

        buying_power_usd = get_buying_power(
            token,
            account_seq,
            "USD"
        )

        print()
        print("=" * 60)
        print("             💵 USD 매수 가능 금액")
        print("=" * 60)

        print(buying_power_usd)


        # ====================================================
        # 🇰🇷 KRW 매수 가능 금액
        # ====================================================

        print()
        print("KRW 매수 가능 금액을 조회하는 중...")

        buying_power_krw = get_buying_power(
            token,
            account_seq,
            "KRW"
        )

        print()
        print("=" * 60)
        print("             🇰🇷 KRW 매수 가능 금액")
        print("=" * 60)

        print(buying_power_krw)


        # ====================================================
        # 완료
        # ====================================================

        print()
        print("=" * 60)
        print("                  테스트 완료")
        print("=" * 60)


    # ========================================================
    # HTTP 오류
    # ========================================================

    except requests.exceptions.HTTPError as e:

        print()
        print("=" * 60)
        print("❌ 토스 API 요청 오류")
        print("=" * 60)

        print(e)

        if e.response is not None:

            print()
            print("토스 서버 응답:")

            try:

                print(
                    e.response.json()
                )

            except:

                print(
                    e.response.text
                )


    # ========================================================
    # 기타 오류
    # ========================================================

    except Exception as e:

        print()
        print("=" * 60)
        print("❌ 프로그램 실행 중 오류")
        print("=" * 60)

        print(e)