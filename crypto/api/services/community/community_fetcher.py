import requests
from django.conf import settings


class CommunityFetcher:
    BASE_URL = "https://pro-api.coinmarketcap.com"

    headers = {
        "Accepts": "application/json",
    }

    def __init__(self):
        self.headers = {
            **self.headers,
            "X-CMC_PRO_API_KEY": settings.COIN_MARKET_API_KEY,
        }


    def fetch_top_posts(self, symbol="BTC"):
        url = f"{self.BASE_URL}/v1/content/posts/top"

        params = {
            "symbol": symbol,
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=10,
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()



    def fetch_trending_tokens(self):

        url = f"{self.BASE_URL}/v1/community/trending/token"

        response = requests.get(url, headers=self.headers, timeout=10)

        response.raise_for_status()

        return response.json()