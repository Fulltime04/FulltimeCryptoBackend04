from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.core.cache import cache
from django.conf import settings



def index(request):
    cache_key = 'list_coins_Keys'
    cache_data = cache.get(cache_key)
    if cache_data:
        return JsonResponse(cache_data, safe=False)

    try:
       url = "https://api.coingecko.com/api/v3/coins/markets"
       response = requests.get(url, params={
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1
    })

       data = response.json()

       cache.set(cache_key, data)
       return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False)




from .services.cryptocompare import (get_chart_data2)

def chart_data2(request, coin, days):
    try:

        data = get_chart_data2(
            coin,
            days
        )

        return JsonResponse(data, safe=False)

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=400,

        )


import requests
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.models import User

def convert_currencies(request):
    amount = request.GET.get("amount", "1")
    from_Currency = request.GET.get("from_Currency", "USD")
    to_Currency = request.GET.get("to_Currency", "NGN")

    amount = int(amount)

    cache_key = f"{from_Currency}_rates"
    data = cache.get(cache_key)

    try:
        if not data:
            url = f"https://open.er-api.com/v6/latest/{from_Currency}"
            res = requests.get(url)
            data = res.json()

            cache.set(cache_key, data, timeout=300)  # 5 mins

        rates = data["rates"].get(to_Currency)
        result = amount * rates


        return JsonResponse({
            "rates": rates,
            "result": round(result, 2)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return JsonResponse({"error": str(e)}, status=500)


Exchange_Api_Key = settings.EXCHANGE_RATE_API_KEY

CURRENCY_TO_COUNTRY = {
    "USD": "us",
    "AED": "ae",
    "AFN": "af",
    "ALL": "al",
    "AMD": "am",
    "ANG": "cw",
    "AOA": "ao",
    "ARS": "ar",
    "AUD": "au",
    "AWG": "aw",
    "AZN": "az",
    "BAM": "ba",
    "BBD": "bb",
    "BDT": "bd",
    "BGN": "bg",
    "BHD": "bh",
    "BIF": "bi",
    "BMD": "bm",
    "BND": "bn",
    "BOB": "bo",
    "BRL": "br",
    "BSD": "bs",
    "BTN": "bt",
    "BWP": "bw",
    "BYN": "by",
    "BZD": "bz",
    "CAD": "ca",
    "CDF": "cd",
    "CHF": "ch",
    "CLF": "cl",
    "CLP": "cl",
    "CNH": "cn",
    "CNY": "cn",
    "COP": "co",
    "CRC": "cr",
    "CUP": "cu",
    "CVE": "cv",
    "CZK": "cz",
    "DJF": "dj",
    "DKK": "dk",
    "DOP": "do",
    "DZD": "dz",
    "EGP": "eg",
    "ERN": "er",
    "ETB": "et",
    "EUR": "eu",
    "FJD": "fj",
    "FKP": "fk",
    "FOK": "fo",
    "GBP": "gb",
    "GEL": "ge",
    "GGP": "gg",
    "GHS": "gh",
    "GIP": "gi",
    "GMD": "gm",
    "GNF": "gn",
    "GTQ": "gt",
    "GYD": "gy",
    "HKD": "hk",
    "HNL": "hn",
    "HRK": "hr",
    "HTG": "ht",
    "HUF": "hu",
    "IDR": "id",
    "ILS": "il",
    "IMP": "im",
    "INR": "in",
    "IQD": "iq",
    "IRR": "ir",
    "ISK": "is",
    "JEP": "je",
    "JMD": "jm",
    "JOD": "jo",
    "JPY": "jp",
    "KES": "ke",
    "KGS": "kg",
    "KHR": "kh",
    "KID": "ki",
    "KMF": "km",
    "KRW": "kr",
    "KWD": "kw",
    "KYD": "ky",
    "KZT": "kz",
    "LAK": "la",
    "LBP": "lb",
    "LKR": "lk",
    "LRD": "lr",
    "LSL": "ls",
    "LYD": "ly",
    "MAD": "ma",
    "MDL": "md",
    "MGA": "mg",
    "MKD": "mk",
    "MMK": "mm",
    "MNT": "mn",
    "MOP": "mo",
    "MRU": "mr",
    "MUR": "mu",
    "MVR": "mv",
    "MWK": "mw",
    "MXN": "mx",
    "MYR": "my",
    "MZN": "mz",
    "NAD": "na",
    "NGN": "ng",
    "NIO": "ni",
    "NOK": "no",
    "NPR": "np",
    "NZD": "nz",
    "OMR": "om",
    "PAB": "pa",
    "PEN": "pe",
    "PGK": "pg",
    "PHP": "ph",
    "PKR": "pk",
    "PLN": "pl",
    "PYG": "py",
    "QAR": "qa",
    "RON": "ro",
    "RSD": "rs",
    "RUB": "ru",
    "RWF": "rw",
    "SAR": "sa",
    "SBD": "sb",
    "SCR": "sc",
    "SDG": "sd",
    "SEK": "se",
    "SGD": "sg",
    "SHP": "sh",
    "SLE": "sl",
    "SLL": "sl",
    "SOS": "so",
    "SRD": "sr",
    "SSP": "ss",
    "STN": "st",
    "SYP": "sy",
    "SZL": "sz",
    "THB": "th",
    "TJS": "tj",
    "TMT": "tm",
    "TND": "tn",
    "TOP": "to",
    "TRY": "tr",
    "TTD": "tt",
    "TVD": "tv",
    "TWD": "tw",
    "TZS": "tz",
    "UAH": "ua",
    "UGX": "ug",
    "UYU": "uy",
    "UZS": "uz",
    "VES": "ve",
    "VND": "vn",
    "VUV": "vu",
    "WST": "ws",
    "XAF": "cm",
    "XCD": "ag",
    "XCG": "cw",
    "XDR": "un",
    "XOF": "sn",
    "XPF": "pf",
    "YER": "ye",
    "ZAR": "za",
    "ZMW": "zm",
    "ZWG": "zw",
    "ZWL": "zw"
}

def exchangerates(request):
    cache_key = f"exchangerates"
    cache_data = cache.get(cache_key)

    if cache_data:
        return JsonResponse(cache_data, safe=False)

    try:
        url = "https://v6.exchangerate-api.com/v6/{}/latest/USD".format(Exchange_Api_Key)

        response = requests.get(url)
        data = response.json()

        newdata = []
        data = data["conversion_rates"]

        for x in data:
            newdata.append({
                'flagUrl': f"https://flagcdn.com/w40/{CURRENCY_TO_COUNTRY[x]}.png",
                "data": x
            })

        cache.set(cache_key, newdata, timeout=300)

        return JsonResponse(newdata, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
