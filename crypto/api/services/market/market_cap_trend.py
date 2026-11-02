import requests
from django.conf import  settings
from ...models import MarketCapSnapShot
from django.core.exceptions import ValidationError

def collect_market_cap():
    url = "https://api.coingecko.com/api/v3/global"

    api_key = getattr(
        settings,
        "COINGECKO_API_KEY",
        "",
    )

    headers = {}

    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()
        payload = response.json()

        market_cap = payload["data"][
            "total_market_cap"
        ]["usd"]

        if market_cap is None:
            raise ValueError(
                "Market cap value is missing."
            )

        snapshot = MarketCapSnapShot.objects.create(
            market_cap_usd=market_cap,
        )

        return snapshot

    except (
        requests.RequestException,
        KeyError,
        TypeError,
        ValueError,
        ValidationError
    ) as err:
        raise RuntimeError(
            f'Market cap collection failed:\n{err}'
        ) from err



CMC_BASE_URL = "https://pro-api.coinmarketcap.com"


def get_cmc_headers():
    api_key = settings.COIN_MARKET_API_KEY

    if not api_key:
        raise RuntimeError(
            "COINMARKETCAP_API_KEY is not configured."
        )

    return {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }


def get_global_market_cap_history(
    start_time,
    end_time,
    interval="daily",
):
    url = (
        f"{CMC_BASE_URL}/v1/global-metrics/"
        "quotes/historical"
    )

    params = {
        "time_start": start_time.isoformat(),
        "time_end": end_time.isoformat(),
        "interval": interval,
    }

    response = requests.get(
        url,
        headers=get_cmc_headers(),
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("status", {}).get("error_code", 0) != 0:
        raise RuntimeError(
            payload["status"].get(
                "error_message",
                "CoinMarketCap API request failed.",
            )
        )

    quotes = payload.get("data", {}).get("quotes", [])

    return [
        {
            "timestamp": item["timestamp"],
            "market_cap": item["quote"]["USD"][
                "total_market_cap"
            ],
        }
        for item in quotes
        if item.get("quote", {}).get("USD", {}).get(
            "total_market_cap"
        ) is not None
    ]

