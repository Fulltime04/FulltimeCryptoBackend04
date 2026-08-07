import time

from django.conf import settings
from django.core.cache import cache

from .cryptocompare import (
    get_all_coins,
    compare_market,
)


from .utils import send_ws_update


class MarketUpdater:

    def __init__(self):
        self.previous_market = {}

        print("MarketUpdater Initialized")

    def fetch_market(self):
        market = []

        for page in range(1, 2):
            coins = get_all_coins(page)
            print(f"Page {page}: {len(coins)} coins")

            market.extend(coins)

        return market

    def compare(self, new_market):
        return compare_market(
            self.previous_market,
            new_market
        )


    def broadcast(self, changed_coins):

        print("broadcast() called")
        print("Changed:", len(changed_coins))

        if not changed_coins:
            return

        print(f"Broadcasting {len(changed_coins)} changed coins...")

        send_ws_update(
            group_name="market_group",
            data=changed_coins,
            event="market_update",
        )

    def run(self):

        print("=" * 50)
        print("MARKET UPDATER STARTED")
        print("=" * 50)

        # ---------------------------------------------
        # Fetch once so the cache is never empty
        # ---------------------------------------------
        try:
            print("Fetching initial market...")

            market = self.fetch_market()

            cache.set("market_page_1", market, 300)

            # Save as previous market
            self.previous_market = market

            print("Initial market cached.")

        except Exception as e:
            print("Initial Fetch Error:", e)

        # ---------------------------------------------
        # Live update loop
        # ---------------------------------------------
        counter = 0

        while True:

            counter += 1

            # print(f"Update #{counter}")

            connections = cache.get("market_connection", 0)

            if connections == 0:
                # print("No Market Viewers.")
                time.sleep(5)
                continue

            print(f"{connections} market viewers connected.")

            try:

                new_market = self.fetch_market()

                cache.set("market_page_1", new_market, 300)

                changed_coins = self.compare(new_market)

                self.broadcast(changed_coins)

                # IMPORTANT
                self.previous_market = new_market

            except Exception as e:
                print("Market Updater Error:", e)

            time.sleep(
                float(settings.MARKET_UPDATE_INTERVAL)
            )

