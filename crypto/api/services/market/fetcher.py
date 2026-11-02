import logging
import time

import requests

from .constants import (
    COINGECKO_URL,
    DEFAULT_PAGE,
    DEFAULT_PER_PAGE,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
)

logger = logging.getLogger(__name__)


class MarketFetcher:

    def __init__(self):
        self.session = requests.Session()

    # ---------------------------------------------------------
    # INITIAL MARKET
    # ---------------------------------------------------------

    def fetch_initial_market(
        self,
        page=DEFAULT_PAGE,
        per_page=DEFAULT_PER_PAGE,
    ):

        params = {
            "page": page,
            "per_page": per_page,
            "vs_currency": "usd",
            "price_change_percentage": "24h,7d",
            "sparkline": True,
        }

        return self._fetch(
            COINGECKO_URL,
            params,
            page
        )

    # ---------------------------------------------------------
    # MARKET UPDATE
    # ---------------------------------------------------------

    def fetch_update_market(
        self,
        page=DEFAULT_PAGE,
        per_page=DEFAULT_PER_PAGE,
    ):

        params = {
            "page": page,
            "per_page": per_page,
            "vs_currency": "usd",
            "price_change_percentage": "24h",
        }

        return self._fetch(
            COINGECKO_URL,
            params,
            page
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search_coins(self, query):

        search_url = "https://api.coingecko.com/api/v3/search"

        params = {
            "query": query
        }

        try:

            response = self.session.get(
                search_url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            return data.get("coins", [])

        except requests.exceptions.RequestException as error:

            logger.warning(
                "CoinGecko search failed: %s",
                error,
            )

            return []

    # ---------------------------------------------------------
    # COMMON FETCH METHOD
    # ---------------------------------------------------------

    def fetch_coins_by_ids(self, coin_ids):

        if not coin_ids:
            return []

        params = {
            "vs_currency": "usd",
            "ids": ",".join(coin_ids),
            "price_change_percentage": "24h",
        }

        try:

            response = self.session.get(
                COINGECKO_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as error:

            logger.warning(
                "Failed to fetch searched coins: %s",
                error,
            )

            return []


    def _fetch(
        self,
        url,
        params,
        page=None,
    ):

        for attempt in range(
            1,
            MAX_RETRIES + 1
        ):

            try:

                logger.info(
                    "Fetching page %s (Attempt %s/%s)",
                    page,
                    attempt,
                    MAX_RETRIES,
                )

                response = self.session.get(
                    url,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                market = response.json()

                logger.info(
                    "Fetched %s coins",
                    len(market),
                )

                return market

            except requests.exceptions.RequestException as error:

                logger.warning(
                    "CoinGecko request failed "
                    "(Attempt %s/%s): %s",
                    attempt,
                    MAX_RETRIES,
                    error,
                )

                if attempt < MAX_RETRIES:

                    time.sleep(
                        RETRY_DELAY
                    )

        logger.error(
            "Failed to fetch market data."
        )

        return None

    # ---------------------------------------------------------
    # PUBLIC METHOD FOR MARKET UPDATER
    # ---------------------------------------------------------

    def get_market_page(self, page=DEFAULT_PAGE,per_page=DEFAULT_PER_PAGE):

        return self.fetch_update_market(
            page=page,
            per_page=per_page
        )



class MarketSnapshotFetcher:

    def __init__(self):
        self.url = (
            "https://api.coingecko.com/api/v3/coins/markets"
        )

    def get_market_snapshot(self):

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 15,
            "page": 1,
            "price_change_percentage": "24h",
        }

        for attempt in range(1, 4):

            try:

                print(
                    f"Fetching snapshot "
                    f"(Attempt {attempt}/3)"
                )

                response = requests.get(
                    self.url,
                    params=params,
                    timeout=15
                )

                response.raise_for_status()

                coins = response.json()

                print(
                    f"Snapshot fetched: "
                    f"{len(coins)} coins"
                )

                return [
                    {
                        "id": coin["id"],
                        "symbol": coin["symbol"].upper(),
                        "name": coin["name"],
                        "image": coin["image"],
                        "price": coin["current_price"],
                        "change_24h": coin.get(
                            "price_change_percentage_24h"
                        ),
                        "market_cap": coin["market_cap"],
                        "volume_24h": coin["total_volume"],
                    }
                    for coin in coins
                ]

            except requests.exceptions.SSLError as e:

                print(
                    f"SSL error on attempt "
                    f"{attempt}: {e}"
                )

            except requests.exceptions.RequestException as e:

                print(
                    f"Request error on attempt "
                    f"{attempt}: {e}"
                )

            if attempt < 3:
                time.sleep(3)

        print(
            "Snapshot request failed after "
            "3 attempts."
        )

        return []