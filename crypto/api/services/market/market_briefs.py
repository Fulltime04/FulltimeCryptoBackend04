import requests

from django.core.cache import cache



COINPAPRIKA_URL = "https://api.coinpaprika.com/v1/global"

COINGECKO_GLOBAL_URL = (
    "https://api.coingecko.com/api/v3/global"
)

COINGECKO_ETH_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
)



def fetch_market_global_data():

    try:

        paparika_response = requests.get(
            COINPAPRIKA_URL,
            timeout=10
        )

        paparika_response.raise_for_status()
        paparika = paparika_response.json()

        global_response = requests.get(
            COINGECKO_GLOBAL_URL,
            timeout=10
        )

        global_response.raise_for_status()
        global_data = global_response.json()["data"]

        eth_response = requests.get(
            COINGECKO_ETH_URL,
            params={
                "vs_currency": "usd",
                "ids": "ethereum",
            },
            timeout=10
        )

        btc_response = requests.get(
            COINGECKO_ETH_URL,
            params={
                "vs_currency": "usd",
                "ids": "bitcoin"
            },
            timeout=20
        )

        btc_response.raise_for_status()
        btc_data = btc_response.json()[0]

        print("BTC Data: ", btc_data)

        eth_response.raise_for_status()
        eth_data = eth_response.json()[0]

        dominance = global_data.get(
            "market_cap_percentage", "ethereum"
        )

        print("Global Data: ", global_data)

        market_brief = {
            "market_cap": paparika.get("market_cap_usd"),

            "volume_24h": paparika.get("volume_24h_usd"),

            "btc_dominance": dominance.get(
                "btc",
                paparika.get(
                    "bitcoin_dominance_percentage"
                ),
            ),

            # "btc_volume_24h": paparika.get(
            #     "btc_volume_24h",
            # ),

            "active_coins": global_data.get(
                "active_cryptocurrencies"
            ),

            "market_cap_change_24h": paparika.get(
                "market_cap_change_24h"
            ),

            "volume_24h_change_24h": paparika.get(
                "volume_24h_change_24h"
            ),

            "eth_dominance": dominance.get(
                "eth"
            ),

            "ethereum_price_usd": eth_data.get(
                "current_price"
            ),

            "ethereum_market_cap_usd": eth_data.get(
                "market_cap"
            ),
            "ethereum_volume_24h_usd": eth_data.get(
                "total_volume"
            ),

            "ethereum_change_24h_percentage": eth_data.get(
                "price_change_percentage_24h"
            ),

            "bitcoin_change_24h_percentage": btc_data.get(
                "price_change_percentage_24h"
            )
        }

        print("Market Brief Data: ", market_brief)

        return market_brief


    except (requests.RequestException, KeyError, ValueError,
            TypeError, IndexError) as e:
        print("Market Brief Error: ", {e})
        return None




def fetch_fear_greed():
    cache_key = "rockers_fear_greed"
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data

    url = "https://api.alternative.me/fng/"

    params = {
        "limit": 30,
        "format": "json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    print("My Alternative Response: ", response.json())

    records = response.json().get("data", [])

    if not records:
        raise ValueError("Fear & Greed API returned no data.")

    # API records are ordered newest first.
    current = records[0]

    history = [
        {

            "value": int(record["value"]),
            "classification": record["value_classification"],
            "timestamp": int(record["timestamp"]),
        }
        for record in records
    ]

    current_value = history[0]["value"]

    # Previous observation, usually yesterday's reading.
    previous_value = (
        history[1]["value"] if len(history) > 1 else None
    )

    # Average of the latest seven available observations.
    last_seven = history[:7]
    average_7d = round(
        sum(item["value"] for item in last_seven)
        / len(last_seven)
    )

    result = {
        "value": current_value,
        "classification": current["value_classification"],
        "timestamp": int(current["timestamp"]),
        "previous_value": previous_value,
        "change": (
            current_value - previous_value
            if previous_value is not None
            else None
        ),
        "average_7d": average_7d,
        "history": history,
        "source": "Alternative.me",
    }

    # The index is published daily; avoid repeatedly calling the API.
    cache.set(cache_key, result, 60 * 30)

    return result



