import time

from django.conf import settings
from django.core.cache import cache

from .fetcher import MarketFetcher
from .comparator import MarketComparator
from .cache import MarketCache
from .broadcaster import MarketBroadcaster

from .constants import ACTIVE_MARKET_PAGE_KEY


class MarketUpdater:

    def __init__(self):

        self.fetcher = MarketFetcher()

        self.comparator = MarketComparator()

        self.market_cache = MarketCache()

        self.broadcaster = MarketBroadcaster()

        self.previous_market = {}

    def run(self):

        while True:

            # ---------------------------------------------
            # GET CURRENTLY ACTIVE PAGE
            # ---------------------------------------------

            page = cache.get(
                ACTIVE_MARKET_PAGE_KEY,
                1,
            )

            # ---------------------------------------------
            # FETCH THAT PAGE
            # ---------------------------------------------

            new_market = (
                self.fetcher.get_market_page(
                    page=page
                )
            )

            if new_market is None:

                time.sleep(
                    settings.MARKET_UPDATE_INTERVAL
                )

                continue

            # ---------------------------------------------
            # PREVIOUS DATA FOR THIS PAGE
            # ---------------------------------------------

            previous_market = (
                self.previous_market.get(
                    page,
                    self.market_cache.load(page)
                )
            )

            # ---------------------------------------------
            # COMPARE
            # ---------------------------------------------

            changed = self.comparator.compare(
                previous_market,
                new_market,
            )

            # ---------------------------------------------
            # SAVE PAGE
            # ---------------------------------------------

            self.market_cache.save(
                page,
                new_market,
            )

            # ---------------------------------------------
            # BROADCAST
            # ---------------------------------------------

            if changed:

                self.broadcaster.broadcast(
                    changed
                )

            # ---------------------------------------------
            # REMEMBER THIS PAGE
            # ---------------------------------------------

            self.previous_market[
                page
            ] = new_market

            # ---------------------------------------------
            # WAIT
            # ---------------------------------------------

            time.sleep(
                settings.MARKET_UPDATE_INTERVAL
            )