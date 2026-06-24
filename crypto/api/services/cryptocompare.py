import random

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



NOTIFICATION_BANK = {

    "BUY": {
        "title": "Purchase Completed",
        "messages": [
            "Your purchase of {quantity} {coin} was completed successfully. ${amount} has been deducted from your wallet.",
            "Order executed successfully. You acquired {quantity} {coin} for ${amount}.",
            "Trade confirmed! {quantity} {coin} has been added to your portfolio at a total cost of ${amount}.",
            "Purchase successful. Your account has been updated with {quantity} {coin} and charged ${amount}."
        ]
    },

    "SELL": {
        "title": "Sale Completed",
        "messages": [
            "You successfully sold {quantity} {coin}. ${amount} has been credited to your account.",
            "Sale confirmed. {quantity} {coin} was sold and ${amount} has been added to your balance.",
            "Trade completed successfully. Your sale of {quantity} {coin} generated ${amount}.",
            "Order filled! ${amount} has been credited following the sale of {quantity} {coin}."
        ]
    },

    "DEPOSIT": {
        "title": "Deposit Confirmed",
        "messages": [
            "Your deposit of ${amount} has been received and added to your wallet.",
            "Funds received! ${amount} is now available in your account.",
            "Deposit successful. Your wallet balance has been credited with ${amount}.",
            "We've confirmed your deposit of ${amount}. The funds are ready to use."
        ]
    },

    "WITHDRAW": {
        "title": "Withdrawal Processed",
        "messages": [
            "Your withdrawal request for ${amount} has been processed successfully.",
            "Withdrawal completed. ${amount} has been sent from your account.",
            "Your request to withdraw ${amount} was approved and processed.",
            "Funds on the way! Your withdrawal of ${amount} has been initiated."
        ]
    },

    "CURRENCY_CONVERTER": {
        "title": "Conversion Successful",
        "messages": [
            "{from_amount} {from_currency} was successfully converted into {to_amount} {to_currency}.",
            "Conversion complete. You received {to_amount} {to_currency} from {from_amount} {from_currency}.",
            "Exchange successful! {from_amount} {from_currency} is now {to_amount} {to_currency}.",
            "Your currency conversion has been completed at the current market rate."
        ]
    },

    "ALERT": {
        "title": "Price Alert Triggered",
        "messages": [
            "{coin} has reached your target price of ${price}.",
            "Market alert! {coin} is now trading at ${price}.",
            "Your price alert for {coin} has been triggered at ${price}.",
            "Good news! {coin} has hit the price level you were monitoring (${price})."
        ]
    },

    "SYSTEM": {
        "title": "System Notification",
        "messages": [
            "{message}",
            "Important update: {message}",
            "System announcement: {message}",
            "Attention: {message}"
        ]
    },

    "MESSAGE": {
        "title": "New Message",
        "messages": [
            "{sender} sent you a new message.",
            "You have received a new message from {sender}.",
            "{sender} just contacted you. Open your inbox to read the message.",
            "A new message from {sender} is waiting in your inbox."
        ]
    }
}


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