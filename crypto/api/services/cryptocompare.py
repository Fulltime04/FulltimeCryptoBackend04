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
        ],
        "icons": ["🟢", "📈", "💹", "🪙"],

    },

    "SELL": {
        "title": "Sales Completed",
        "messages": [
            "You successfully sold {quantity} {coin}. ${amount} has been credited to your account.",
            "Sale confirmed. {quantity} {coin} was sold and ${amount} has been added to your balance.",
            "Trade completed successfully. Your sale of {quantity} {coin} generated ${amount}.",
            "Order filled! ${amount} has been credited following the sale of {quantity} {coin}."
        ],
        "icons": ["🔴", "📉", "💸", "💰"],
    },

    "DEPOSIT": {
        "title": "Deposit Confirmed",
        "messages": [
            "Your deposit of ${amount} has been received and added to your wallet.",
            "Funds received! ${amount} is now available in your account.",
            "Deposit successful. Your wallet balance has been credited with ${amount}.",
            "We've confirmed your deposit of ${amount}. The funds are ready to use."
        ],
        "icons": ["💵", "🏦", "💳", "📥"],
    },

    "WITHDRAW": {
        "title": "Withdrawal Processed",
        "messages": [
            "Your withdrawal request for ${amount} has been processed successfully.",
            "Withdrawal completed. ${amount} has been sent from your account.",
            "Your request to withdraw ${amount} was approved and processed.",
            "Funds on the way! Your withdrawal of ${amount} has been initiated."
        ],
        "icons": ["💸", "📤", "🏧", "💰"],
    },

    "CURRENCY_CONVERTER": {
        "title": "Conversion Successful",
        "messages": [
            "{from_amount} {from_Currency} was successfully converted into {to_amount} {to_Currency}.",
            "Conversion complete. You received {to_amount} {to_Currency} from {from_amount} {from_Currency}.",
            "Exchange successful! {from_amount} {from_Currency} is now {to_amount} {to_Currency}.",
            "Your currency conversion has been completed at the current market rate."
        ],
        "icons": ["💱", "🔄", "🌍", "💹"],
    },

    "Coin_Exchange": {
    "title": "Exchange Successful",
    "messages": [
        "Successfully exchanged {amount} {from_coin_id} for {result_Amount} {to_coin_id}.",
        "Your crypto swap has been completed. You received {result_Amount} {to_coin_id} in exchange for {amount} {from_coin_id}.",
        "Exchange completed! {amount} {from_coin_id} has been converted to {result_Amount} {to_coin_id}.",
        "Trade executed successfully at the current market rate.",
        "Your assets have been swapped successfully. New balance updated.",
        "{result_Amount} {to_coin_id} has been credited to your wallet after exchanging {amount} {from_coin_id}.",
        "Coin exchange completed successfully. Thank you for trading with us!"
    ],
    "icons": ["💱", "🔄", "🪙", "📈", "✅", "🚀", "💹"],
    },

    "ALERT": {
        "title": "Price Alert Triggered",
        "messages": [
            "{coin} has reached your target price of ${price}.",
            "Market alert! {coin} is now trading at ${price}.",
            "Your price alert for {coin} has been triggered at ${price}.",
            "Good news! {coin} has hit the price level you were monitoring (${price})."
        ],
        "icons": ["🚨", "🔔", "⚠️", "📢"],
    },

    "SYSTEM": {
        "title": "System Notification",
        "messages": [
            "{message}",
            "Important update: {message}",
            "System announcement: {message}",
            "Attention: {message}"
        ],
        "icons": ["⚙️", "🛠️", "📡", "🔷"],
    },

    "MESSAGE": {
        "title": "New Message",
        "messages": [
            "{sender} sent you a new message.",
            "You have received a new message from {sender}.",
            "{sender} just contacted you. Open your inbox to read the message.",
            "A new message from {sender} is waiting in your inbox."
        ],
        "icons":  ["💬", "📩", "✉️", "📨"],
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



TRANSACTION_CARD_BANK = {

    "BUY": {
        "icons": [
            "🟢",
            "📈",
            "💹",
            "🪙",
            "🚀",
        ],

        "titles": [
            "Crypto Purchased",
            "Buy Order Completed",
            "Purchase Successful",
            "Investment Added",
            "Asset Acquired",
        ],

        "messages": [
            "Your purchase was completed successfully.",
            "Your investment has been added to your portfolio.",
            "Your crypto purchase has been confirmed.",
            "You successfully bought your selected cryptocurrency.",
            "Another step towards growing your portfolio!",
        ],

        "status": [
            "Completed",
            "Successful",
            "Confirmed",
            "Executed",
            "Processed",
            "Approved",
        ]
    },


    "SELL": {
        "icons": [
            "🔴",
            "📉",
            "💰",
            "💸",
            "🏦",
        ],

        "titles": [
            "Crypto Sold",
            "Sell Order Completed",
            "Sale Successful",
            "Asset Sold",
            "Trade Executed",
        ],

        "messages": [
            "Your sell order has been completed.",
            "Your cryptocurrency has been sold successfully.",
            "Funds from your sale have been credited.",
            "Your trade has been executed successfully.",
            "Sale completed without any issues.",
        ],

        "status": [
            "Completed",
            "Successful",
            "Executed",
            "Confirmed",
            "Processed",
        ]
    },


    "DEPOSIT": {
        "icons": [
            "💰",
            "🏦",
            "💵",
            "💳",
            "📥",
        ],

        "titles": [
            "Deposit Received",
            "Wallet Funded",
            "Deposit Successful",
            "Funds Added",
            "Balance Updated",
        ],

        "messages": [
            "Your funds have been added successfully.",
            "Your wallet balance has been updated.",
            "Deposit completed successfully.",
            "Your account has been funded.",
            "Funds received and available for trading.",
        ],

        "status": [
            "Successful",
            "Completed",
            "Approved",
            "Received",
            "Confirmed",
        ]
    },


    "WITHDRAW": {
        "icons": [
            "💸",
            "📤",
            "🏧",
            "💵",
            "🚚",
        ],

        "titles": [
            "Withdrawal Processed",
            "Funds Sent",
            "Withdrawal Successful",
            "Transfer Completed",
            "Cash Out Successful",
        ],

        "messages": [
            "Your withdrawal has been processed.",
            "Funds are on their way.",
            "Withdrawal completed successfully.",
            "Your transfer request has been fulfilled.",
            "Your funds have left your wallet.",
        ],

        "status": [
            "Completed",
            "Successful",
            "Processed",
            "Sent",
            "Confirmed",
        ]
    },


    "CURRENCY_CONVERTER": {
        "icons": [
            "🔄",
            "💱",
            "🌍",
            "💹",
            "🔁",
        ],

        "titles": [
            "Currency Converted",
            "Conversion Successful",
            "Exchange Completed",
            "Funds Converted",
            "Conversion Processed",
        ],

        "messages": [
            "Your currency conversion was successful.",
            "Exchange completed successfully.",
            "Your funds have been converted.",
            "Conversion completed instantly.",
            "Exchange processed successfully.",
        ],

        "status": [
            "Completed",
            "Successful",
            "Processed",
            "Confirmed",
        ]
    },


    "ALERT": {
        "icons": [
            "🔔",
            "📢",
            "⚡",
            "🚨",
            "📈",
        ],

        "titles": [
            "Price Alert",
            "Market Alert",
            "Target Reached",
            "Price Update",
            "Trading Alert",
        ],

        "messages": [
            "One of your price alerts has been triggered.",
            "A watched asset has reached your target.",
            "Market conditions have changed.",
            "Stay informed with the latest price movement.",
            "Your alert has been activated.",
        ],

        "status": [
            "Triggered",
            "Delivered",
            "Updated",
            "Active",
        ]
    },


    "MESSAGE": {
        "icons": [
            "💬",
            "📩",
            "✉️",
            "📨",
            "💙",
        ],

        "titles": [
            "New Message",
            "Inbox Update",
            "Conversation Started",
            "Message Received",
            "Someone Reached Out",
        ],

        "messages": [
            "Someone sent you a thoughtful message.",
            "You have a new conversation waiting.",
            "A new message has arrived in your inbox.",
            "Stay connected—someone just messaged you.",
            "Your inbox has something new for you.",
        ],

        "status": [
            "Delivered",
            "Received",
            "Unread",
            "Available",
        ]
    },


    "SYSTEM": {
        "icons": [
            "⚙️",
            "🛡️",
            "📢",
            "✨",
            "🔐",
        ],

        "titles": [
            "System Update",
            "Platform Notice",
            "Service Update",
            "Maintenance Notice",
            "Account Update",
        ],

        "messages": [
            "Everything is running smoothly.",
            "Your account remains secure.",
            "Thank you for choosing our platform.",
            "The platform has been updated successfully.",
            "We're constantly improving your experience.",
        ],

        "status": [
            "Completed",
            "Updated",
            "Delivered",
            "Successful",
        ]
    }

}



marketCapApiKey = settings.COIN_MARKET_API_KEY

def get_coin_marketCap(page):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    limit = 250
    start = (page - 1) * limit

    headers = {
        "X-CMC_PRO_API_KEY": marketCapApiKey
    }

    params = {
        "convert": "USD",
        "start": start,
        "limit": limit,
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    return response.json()["data"]


def get_cryptoCompare_coin(page):

    url = "https://min-api.cryptocompare.com/data/all/coinlist"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    coins = list(response.json()["Data"].values())
    limit = 250
    start = (page - 1) * limit
    end = start + limit

    return coins[start:end]


# def get_coin_gecko(page=1):
#
#     url = "https://api.coingecko.com/api/v3/coins/markets"
#
#     params = {
#         "vs_currency": "usd",
#         "per_page": 250,
#         "page": page,
#         "sparkline": "true",
#         "price_change_percentage": "24h,7d"
#     }
#
#     for attempt in range(3):
#
#         try:
#
#             response = requests.get(
#                 url,
#                 params=params,
#                 timeout=20
#             )
#
#             response.raise_for_status()
#
#             return response.json()
#
#         except requests.exceptions.RequestException as e:
#
#             print(f"Attempt {attempt + 1} failed:", e)
#
#             time.sleep(2)
#
#     return []





def get_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()["coins"]

    result = []

    for x in data:
        result.append(x["item"])

    return result




def get_trending():

    providers = [

        ("CoinGecko", get_trending_coins),

        # Future providers

    ]

    for name, provider in providers:

        try:

            print(f"Using {name}")

            return provider()

        except Exception as e:

            print(e)

    return []











