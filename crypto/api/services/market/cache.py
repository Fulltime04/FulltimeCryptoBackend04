from django.core.cache import cache

from .constants import (
    CACHE_TIMEOUT,
    PAGINATED_CACHE_TIMEOUT,
    CACHE_LOCK_TIMEOUT
)


class MarketCache:

    def save(
        self,
        page,
        data,
        timeout=None,
    ):

        if timeout is None:
            timeout = (
                CACHE_TIMEOUT
                if page == 1 else PAGINATED_CACHE_TIMEOUT
            )

        cache.set(
            f'market_page_{page}',
            data,
            timeout,
        )


    def load(self,page):

        return cache.get(
            f'market_page_{page}',
            [],
        )


    def clear(self,page):

        cache.delete(
            f'market_page_{page}',
        )

    def acquire_lock(self, page):

        return cache.add(
            f'market_page_lock_{page}',
            True,
            CACHE_LOCK_TIMEOUT,

        )

    def release_lock(self, page):

        cache.delete(
            f"market_page_lock_{page}",
        )