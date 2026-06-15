import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

API_KEY = settings.CRYPTOCOMPARE_API_KEY



def get_chart_data2(coin, days):
    days = int(days)
    cache_key = f"{coin}_{days}_data"
    cache_data = cache.get(cache_key)

    if cache_data:
        return cache_data

    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": days
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    chart_data = response.json()

    cache.set(cache_key, chart_data, timeout=300)

    return chart_data
