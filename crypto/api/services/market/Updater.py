import time

from django.conf import settings

from .fetcher import MarketFetcher
from .comparator import MarketComparator
from .cache import MarketCache
from .broadcaster import MarketBroadcaster


class MarketUpdater:

    def __init__(self):

        self.fetcher = MarketFetcher()

        self.comparator = MarketComparator()

        self.cache = MarketCache()

        self.broadcaster = MarketBroadcaster()

        self.previous_market = self.cache.load()

    def run(self):

        while True:

            new_market = self.fetcher.get_market_page(
                page=1
            )

            changed = self.comparator.compare(
                self.previous_market,
                new_market,
            )

            self.cache.save(
                new_market
            )

            self.broadcaster.broadcast(
                changed
            )

            self.previous_market = new_market

            time.sleep(
                settings.MARKET_UPDATE_INTERVAL
            )