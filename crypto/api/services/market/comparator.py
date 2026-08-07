import requests


class MarketComparator:
    def __init__(self):
        self.session = requests.Session()


    def compare(self, previous_market, current_market):
        changed_Coins = []

        previous_lookup = {
            coin['id']: coin for coin in previous_market
        }

        for coin in current_market:
            older_coins = previous_lookup.get(coin["id"])

            if older_coins is None:

                changed_Coins.append(coin)

                continue

            if self.has_changed(older_coins, coin):

                changed_Coins.append(coin)


        return changed_Coins


    def has_changed(self, old, new):
        return {
            old["current_price"] != new["current_price"]
            or old["market_cap"] != new["market_cap"]
            or old["total_supply"] != new["total_supply"]
            or old["total_volume"] != new["total_volume"]
            or old["price_change_percentage_24h"] != new["price_change_percentage_24h"]
            or old["atl"] != new["atl"]
            or old["ath"] != new["ath"]
            or old["circulating_supply"] != new["circulating_supply"]
            or old["max_supply"] != new["max_supply"]
        }

