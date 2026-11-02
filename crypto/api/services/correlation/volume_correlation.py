
import requests
from math import sqrt
from django.core.cache import cache


KRAKEN_URL = "https://api.kraken.com/0/public/OHLC"

# Convert common Binance-style symbols to Kraken pairs.
KRAKEN_PAIRS = {
    "BTCUSDT": "XBTUSD",
    "BTCUSD": "XBTUSD",
    "ETHUSDT": "ETHUSD",
    "ETHUSD": "ETHUSD",
    "SOLUSDT": "SOLUSD",
    "SOLUSD": "SOLUSD",
    "XRPUSDT": "XRPUSD",
    "XRPUSD": "XRPUSD",
    "ADAUSDT": "ADAUSD",
    "ADAUSD": "ADAUSD",
    "DOGEUSDT": "DOGEUSD",
    "DOGEUSD": "DOGEUSD",
}


def calculate_correlation(x, y):
    if len(x) != len(y) or len(x) < 2:
        return None

    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)

    numerator = sum(
        (a - x_mean) * (b - y_mean)
        for a, b in zip(x, y)
    )

    denominator = sqrt(
        sum((a - x_mean) ** 2 for a in x) *
        sum((b - y_mean) ** 2 for b in y)
    )

    if denominator == 0:
        return None

    return numerator / denominator


def get_volume_price_correlation(symbol="BTCUSDT", days=1):

    allowed_days = {
        1: 24,
        7: 168,
        30: 720
    }

    if days not in allowed_days:
        raise ValueError("Unsupported time range.")

    symbol = symbol.upper().strip()

    pair = KRAKEN_PAIRS.get(symbol)

    if not pair:
        raise ValueError(f"Unsupported Kraken market symbol: {symbol}")

    cache_key = f"kraken_correlation_{symbol}_{days}"

    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data

    hours = allowed_days[days]

    response = requests.get(
        KRAKEN_URL,
        params={
            "pair": pair,
            "interval": 60
        },
        timeout=20
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("error"):
        raise ValueError(
            ", ".join(payload["error"])
        )

    result_data = payload.get("result", {})

    pair_key = next(
        (key for key in result_data if key != "last"),
        None
    )

    if not pair_key:
        raise ValueError("No market data returned by Kraken.")

    candles = result_data[pair_key]

    # Kraken includes the current, unfinished candle.
    # Remove it before calculating returns.
    candles = candles[:-1]

    # Keep enough completed candles for the selected period.
    candles = candles[-(hours + 1):]

    if len(candles) < 3:
        raise ValueError("Insufficient market data returned.")

    observations = []

    for index in range(1, len(candles)):

        previous = candles[index - 1]
        current = candles[index]

        previous_close = float(previous[4])
        current_close = float(current[4])

        volume = float(current[6])

        if previous_close <= 0:
            continue

        price_change = (
            (current_close - previous_close) /
            previous_close
        ) * 100

        observations.append({
            "timestamp": int(current[0]) * 1000,
            "volume": volume,
            "price_change": round(price_change, 4),
            "close": current_close
        })

    volumes = [
        item["volume"] for item in observations
    ]

    changes = [
        item["price_change"] for item in observations
    ]

    correlation = calculate_correlation(
        volumes,
        changes
    )

    if correlation is None:
        raise ValueError("Insufficient variation in market data.")

    result = {
        "success": True,
        "symbol": symbol,
        "provider": "Kraken",
        "range": f"{days}d",
        "interval": "1h",
        "correlation": round(correlation, 4),
        "data_points": len(observations),
        "data": observations
    }

    cache.set(cache_key, result, timeout=300)

    return result
