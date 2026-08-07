from django.core.cache import cache

from .constants import (
    MARKET_CACHE_KEY,
    CACHE_TIMEOUT,
)


class MarketCache:

    def save(
        self,
        market,
    ):

        cache.set(
            MARKET_CACHE_KEY,
            market,
            CACHE_TIMEOUT,
        )

    def load(self):

        return cache.get(
            MARKET_CACHE_KEY,
            [],
        )

    def clear(self):

        cache.delete(
            MARKET_CACHE_KEY,
        )