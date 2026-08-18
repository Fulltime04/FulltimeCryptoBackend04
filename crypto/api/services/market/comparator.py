import requests


class MarketComparator:

    def __init__(self):
        self.session = requests.Session()

    def compare(self, previous_market, current_market):

        changed_coins = []

        previous_lookup = {
            coin["id"]: coin
            for coin in previous_market
        }

        for coin in current_market:

            old_coin = previous_lookup.get(coin["id"])

            # New coin
            if old_coin is None:

                changed_coins.append(coin)

                continue

            changed = self.get_changed_fields(
                old_coin,
                coin
            )

            if changed:

                changed["id"] = coin["id"]

                changed_coins.append(changed)

        return changed_coins


    def get_changed_fields(self, old, new):

        changed = {}

        fields = [
            "current_price",
            "market_cap",
            "total_supply",
            "total_volume",
            "price_change_percentage_24h",
            "atl",
            "ath",
            "circulating_supply",
            "max_supply",
        ]

        for field in fields:

            if old.get(field) != new.get(field):

                changed[field] = new.get(field)

        return changed

