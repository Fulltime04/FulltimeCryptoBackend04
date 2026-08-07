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
    """
    Responsible for fetching cryptocurrency market data.

    Responsibilities:
        - Connect to CoinGecko
        - Request market data
        - Retry on temporary failures

    Does NOT:
        - Compare market data
        - Cache market data
        - Broadcast WebSocket updates
    """

    def __init__(self):
        self.session = requests.Session()

    def fetch_market_data(
        self,
        page=DEFAULT_PAGE,
        per_page=DEFAULT_PER_PAGE,
    ):
        """
        Fetch one page of market data from CoinGecko.
        """

        params = {
            "page": page,
            "per_page": per_page,
            "vs_currency": "usd",
            "price_change_percentage": "24h,7d",
        }

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                logger.info(
                    "Fetching page %s (Attempt %s/%s)",
                    page,
                    attempt,
                    MAX_RETRIES,
                )

                response = self.session.get(
                    COINGECKO_URL,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                market = response.json()

                print(market[0].keys())
                print("sparkline_in_7d" in market[0])
                
                logger.info(
                    "Fetched %s coins from page %s",
                    len(market),
                    page,
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

                # Don't sleep after the final attempt
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        logger.error(
            "Failed to fetch market data after %s attempts.",
            MAX_RETRIES,
        )

        return []

    def get_market_page(self, page):
        """
        Public method used by MarketUpdater.
        """

        return self.fetch_market_data(page=page)