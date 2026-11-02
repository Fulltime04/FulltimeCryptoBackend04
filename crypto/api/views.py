
import random
import time
from decimal import Decimal

import requests

from django.conf import settings
from django.contrib.messages.api import success
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from requests import Response

from django.views.decorators.http import require_GET
from datetime import timedelta
from django.utils import timezone




# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from rest_framework.response import Response
from rest_framework import status


# ============================================================
# LOCAL MODELS
# ============================================================

from .models import (
    Wallet,
    CoinHolding,
    Transaction,
    Notifications,
    NewsArticle,
    MarketCapSnapShot
)


# ============================================================
# SERVICES
# ============================================================

from .services.cryptocompare import (
    NOTIFICATION_BANK,
    CURRENCY_TO_COUNTRY,
    TRANSACTION_CARD_BANK,
    get_chart_data2,
    get_trending_coins,
)

from .services.market.market_cap_trend import (
    get_global_market_cap_history
)

from .services.utils import (
    send_wallet_update,
    send_notification_update,
    get_wallet_stats,
    send_transaction_update,
)

from .services.market.fetcher import (
    MarketFetcher,
)

from .services.market.market_briefs import (
    fetch_market_global_data,
    fetch_fear_greed,
)

from .services.market.constants import (
    DEFAULT_PER_PAGE,
    CACHE_LOCK_WAIT,
    ACTIVE_MARKET_PAGE_KEY,
)

from .services.market.cache import (
    MarketCache,
)


from .services.correlation.volume_correlation import get_volume_price_correlation


# ============================================================
# CUSTOM USER MODEL
# ============================================================

User = get_user_model()


# ============================================================
# API KEYS
# ============================================================

marketCapApiKey = settings.COIN_MARKET_API_KEY

Exchange_Api_Key = settings.EXCHANGE_RATE_API_KEY


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def create_Notification(
    user,
    notification_type,
    **kwargs
):
    """
    Create a notification for the authenticated user.
    """

    template = NOTIFICATION_BANK[notification_type]

    title = template["title"]

    message = random.choice(
        template["messages"]
    ).format(**kwargs)

    icons = random.choice(
        template["icons"]
    )

    notify = Notifications.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        icons=icons,
    )

    return notify


def createTransaction(
    user,
    transactionType,
    **kwargs
):
    """
    Create a transaction record for the authenticated user.
    """

    template = TRANSACTION_CARD_BANK[
        transactionType
    ]

    transact = Transaction.objects.create(
        user=user,
        type=transactionType,

        icon=random.choice(
            template["icons"]
        ),

        title=random.choice(
            template["titles"]
        ),

        message=random.choice(
            template["messages"]
        ).format(**kwargs),

        status=random.choice(
            template["status"]
        ),

        **kwargs
    )

    return transact


# ============================================================
# WALLET — DEPOSIT
# ============================================================


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def deposit(request):

    try:

        print("Deposit Request: ", request.data)

        amount = Decimal(
            request.data.get("amount")
        )

        # IMPORTANT:
        # We no longer search for "fulltime".
        #
        # request.user is the user authenticated
        # by the JWT access token.

        user = request.user

        if not amount:
            return JsonResponse({
                "success": False,
                "error": "Amount is required."
            }, status=400)

        amount = Decimal(amount)

        if amount <= 0:
            return JsonResponse({
                "success": False,
                "error": "Amount must be greater than 0."
            }, status=400)

        wallet, created = Wallet.objects.get_or_create(
            user=user
        )

        wallet.balance += amount
        wallet.save()

        transact = createTransaction(
            user=user,
            transactionType="DEPOSIT",
            amount=amount
        )

        transaction_count = Transaction.objects.filter(
            user=user
        ).count()

        notify = create_Notification(
            user=user,
            notification_type="DEPOSIT",
            amount=amount,
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        send_wallet_update(
            user=user,
            transaction_type="DEPOSIT",
            amount=amount
        )

        send_notification_update(
            user,
            notify,
            count
        )

        send_transaction_update(
            user,
            transact,
            transaction_count
        )

        return JsonResponse({
            "success": True,
            "balance": str(wallet.balance)
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# ============================================================
# WALLET — WITHDRAW
# ============================================================


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def withdraw(request):

    try:

        amount = Decimal(
            request.data.get("amount")
        )

        user = request.user

        if amount <= 0:
            return JsonResponse({
                "success": False,
                "error": "Amount must be greater than 0."
            }, status=400)

        wallet = Wallet.objects.select_for_update().get(
            user=user
        )

        if wallet.balance < amount:

            return JsonResponse({
                "success": False,
                "error": "Insufficient balance"
            }, status=400)

        wallet.balance -= amount
        wallet.save()

        transact = createTransaction(
            user=user,
            transactionType="WITHDRAW",
            amount=amount
        )

        transaction_count = Transaction.objects.filter(
            user=user
        ).count()

        notify = create_Notification(
            user=user,
            notification_type="WITHDRAW",
            amount=amount,
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        send_wallet_update(
            user=user,
            transaction_type="WITHDRAW",
            amount=amount,
        )

        send_notification_update(
            user,
            notify,
            count
        )

        send_transaction_update(
            user,
            transact,
            transaction_count
        )

        return JsonResponse({
            "success": True,
            "balance": str(wallet.balance)
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# ============================================================
# BUY COIN
# ============================================================


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def buy_coin(request):

    try:

        user = request.user

        coin = request.data.get("coin")

        quantity = Decimal(
            request.data.get("quantity")
        )

        current_price = Decimal(
            request.data.get("price")
        )

        if not coin:
            return JsonResponse({
                "success": False,
                "error": "Coin is required."
            }, status=400)

        if quantity <= 0:
            return JsonResponse({
                "success": False,
                "error": "Quantity must be greater than 0"
            }, status=400)

        if current_price <= 0:
            return JsonResponse({
                "success": False,
                "error": "Invalid coin price"
            }, status=400)

        wallet = Wallet.objects.select_for_update().get(
            user=user
        )

        # ====================================================
        # TOTAL COST
        # ====================================================

        total_cost = (
            quantity *
            current_price
        )

        if wallet.balance < total_cost:
            return JsonResponse({
                "success": False,
                "error": "Insufficient balance"
            }, status=400)

        # ====================================================
        # FEE
        # ====================================================

        fee_rate = Decimal("0.001")

        fee = (
            total_cost *
            fee_rate
        )

        total_cost_with_fee = (
            total_cost +
            fee
        )

        # ====================================================
        # HOLDING
        # ====================================================

        holding, created = (
            CoinHolding.objects
            .select_for_update()
            .get_or_create(
                user=user,
                coin=coin,
                defaults={
                    "quantity": Decimal("0"),
                    "average_buy_price": Decimal("0")
                }
            )
        )

        old_qty = holding.quantity

        old_avg = (
            holding.average_buy_price
        )

        new_total_qty = (
            old_qty +
            quantity
        )

        # ====================================================
        # WEIGHTED AVERAGE PRICE
        # ====================================================

        if new_total_qty > 0:

            holding.average_buy_price = (
                (
                    old_qty * old_avg
                )
                +
                (
                    quantity *
                    current_price
                )
            ) / new_total_qty

        holding.quantity = new_total_qty

        holding.save()

        # ====================================================
        # DEDUCT WALLET
        # ====================================================

        wallet.balance -= (
            total_cost_with_fee
        )

        wallet.save()

        # ====================================================
        # CREATE TRANSACTION
        # ====================================================

        transact = createTransaction(
            user=user,
            transactionType="BUY",
            coin=coin,
            amount=total_cost,
            quantity=quantity,
            price_per_coin=current_price,
            fee=fee,
            Coin_quantity_balance=new_total_qty,
        )

        transaction_count = Transaction.objects.filter(
            user=user
        ).count()

        # ====================================================
        # CREATE NOTIFICATION
        # ====================================================

        notify = create_Notification(
            user=user,
            notification_type="BUY",
            amount=total_cost,
            quantity=quantity,
            coin=coin,
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        # ====================================================
        # WEBSOCKET UPDATES
        # ====================================================

        send_wallet_update(
            user=user,
            transaction_type="BUY",
            amount=total_cost,
            coin=coin,
            quantity=quantity
        )

        send_notification_update(
            user,
            notify,
            count
        )

        send_transaction_update(
            user,
            transact,
            transaction_count
        )

        return JsonResponse({
            "success": True,
            "balance": str(
                wallet.balance
            ),
            "quantity": str(
                holding.quantity
            ),
            "average_buy_price": str(
                holding.average_buy_price
            ),
            "fee": str(fee),
            "cost": str(
                total_cost_with_fee
            ),
            "Coin_quantity_balance": str(
                transact.Coin_quantity_balance
            ),
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# ============================================================
# SELL COIN
# ============================================================


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def sell_coin(request):

    try:

        user = request.user

        coin = request.data.get(
            "coin",
            "btc"
        )

        current_price = Decimal(
            request.data.get(
                "price",
                "0"
            )
        )

        quantity = Decimal(
            request.data.get(
                "quantity",
                "0"
            )
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if quantity <= 0:
            return JsonResponse({
                "success": False,
                "error": "Quantity must be greater than 0"
            }, status=400)

        if current_price <= 0:
            return JsonResponse({
                "success": False,
                "error": "Invalid coin price"
            }, status=400)

        # ====================================================
        # FIND HOLDING
        # ====================================================

        holding = (
            CoinHolding.objects
            .select_for_update()
            .filter(
                user=user,
                coin=coin
            )
            .first()
        )

        if not holding:

            return JsonResponse({
                "success": False,
                "error": f"You do not own any {coin}"
            }, status=400)

        if holding.quantity < quantity:

            return JsonResponse({
                "success": False,
                "error": (
                    "Insufficient coin balance. "
                    f"You own {holding.quantity} {coin} "
                    f"but tried to sell {quantity}."
                )
            }, status=400)

        # ====================================================
        # CALCULATIONS
        # ====================================================

        avg_buy_price = (
            holding.average_buy_price
        )

        gross_amount = (
            quantity *
            current_price
        )

        fee_rate = Decimal("0.001")

        fee = (
            gross_amount *
            fee_rate
        )

        received = (
            gross_amount -
            fee
        )

        cost_basis = (
            quantity *
            avg_buy_price
        )

        profit = (
            received -
            cost_basis
        )

        # ====================================================
        # UPDATE WALLET
        # ====================================================

        wallet = (
            Wallet.objects
            .select_for_update()
            .get(user=user)
        )

        wallet.balance += received

        wallet.save()

        # ====================================================
        # UPDATE HOLDING
        # ====================================================

        old_quantity = (
            holding.quantity
        )

        holding.quantity -= quantity

        if holding.quantity <= 0:

            holding.delete()

            remaining_quantity = Decimal("0")

        else:

            holding.save()

            remaining_quantity = (
                holding.quantity
            )

        # ====================================================
        # TRANSACTION
        # ====================================================

        transact = createTransaction(
            user=user,
            transactionType="SELL",
            coin=coin,
            amount=received,
            quantity=quantity,
            price_per_coin=current_price,
            profit=profit,
            fee=fee,
            Coin_quantity_balance=remaining_quantity
        )

        transaction_count = Transaction.objects.filter(
            user=user
        ).count()

        # ====================================================
        # NOTIFICATION
        # ====================================================

        notify = create_Notification(
            user=user,
            notification_type="SELL",
            amount=received,
            quantity=quantity,
            coin=coin
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        # ====================================================
        # WEBSOCKET
        # ====================================================

        send_wallet_update(
            user=user,
            transaction_type="SELL",
            amount=received,
            coin=coin,
            quantity=quantity
        )

        send_notification_update(
            user,
            notify,
            count
        )

        send_transaction_update(
            user,
            transact,
            transaction_count
        )

        return JsonResponse({
            "success": True,
            "coin": coin,
            "sold_quantity": str(
                quantity
            ),
            "remaining_quantity": str(
                remaining_quantity
            ),
            "balance": str(
                wallet.balance
            ),
            "received": str(
                received
            ),
            "profit": str(
                profit
            ),
            "fee": str(
                fee
            ),
            "avg_buy_price": str(
                avg_buy_price
            ),
            "Coin_quantity_balance": str(
                transact.Coin_quantity_balance
            ),
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# ============================================================
# WALLET DATA
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_data(request):

    try:

        user = request.user

        data = get_wallet_stats(
            user
        )

        return JsonResponse({
            "success": True,
            **data
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


# ============================================================
# COINGECKO — BASIC MARKET
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def index(request):

    cache_key = "list_coins_Keys"

    cache_data = cache.get(
        cache_key
    )

    if cache_data:

        return JsonResponse(
            cache_data,
            safe=False
        )

    try:

        url = (
            "https://api.coingecko.com/"
            "api/v3/coins/markets"
        )

        response = requests.get(
            url,
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 250,
                "page": 1,
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=503)


# ============================================================
# CHART DATA
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def chart_data2(
    request,
    coin,
    days
):

    try:

        data = get_chart_data2(
            coin,
            days
        )

        return JsonResponse(
            data,
            safe=False
        )

    except requests.exceptions.HTTPError as e:

        if (
            e.response
            and e.response.status_code == 429
        ):

            return JsonResponse({
                "success": False,
                "error": "Rate_limit_exceeded"
            }, status=429)

        return JsonResponse({
            "error": str(e)
        }, status=400)


# ============================================================
# CURRENCY CONVERTER
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def convert_currencies(request):

    user = request.user

    amount = request.GET.get(
        "amount",
        "1"
    )

    from_Currency = request.GET.get(
        "from_Currency",
        "USD"
    )

    to_Currency = request.GET.get(
        "to_Currency",
        "NGN"
    )

    try:

        amount = Decimal(
            amount
        )

        cache_key = (
            f"{from_Currency}_rates"
        )

        data = cache.get(
            cache_key
        )

        if not data:

            url = (
                f"https://open.er-api.com/"
                f"v6/latest/{from_Currency}"
            )

            res = requests.get(
                url,
                timeout=10
            )

            res.raise_for_status()

            data = res.json()

            cache.set(
                cache_key,
                data,
                timeout=300
            )

        rates = data["rates"].get(
            to_Currency
        )

        if rates is None:

            return JsonResponse({
                "success": False,
                "error": "Currency not supported."
            }, status=400)

        result = (
            amount *
            Decimal(str(rates))
        )

        notify = create_Notification(
            user=user,
            notification_type="CURRENCY_CONVERTER",
            from_amount=amount,
            from_Currency=from_Currency,
            to_amount=result,
            to_Currency=to_Currency,
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        send_notification_update(
            user,
            notify,
            count
        )

        return JsonResponse({
            "success": True,
            "rates": rates,
            "result": round(
                result,
                2
            )
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


# ============================================================
# EXCHANGE RATES
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def exchangerates(request):

    cache_key = "exchangerates"

    cache_data = cache.get(
        cache_key
    )

    if cache_data:

        return JsonResponse(
            cache_data,
            safe=False
        )

    try:

        url = (
            "https://v6.exchangerate-api.com/"
            f"v6/{Exchange_Api_Key}/latest/USD"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        conversion_rates = data[
            "conversion_rates"
        ]

        newdata = []

        for currency in conversion_rates:

            country_code = (
                CURRENCY_TO_COUNTRY.get(
                    currency
                )
            )

            flag_url = None

            if country_code:

                flag_url = (
                    f"https://flagcdn.com/"
                    f"w40/{country_code}.png"
                )

            newdata.append({
                "flagUrl": flag_url,
                "data": currency
            })

        cache.set(
            cache_key,
            newdata,
            timeout=300
        )

        return JsonResponse(
            newdata,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ============================================================
# TRENDING
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def Trending(request):

    cache_key = "trending"

    cache_data = cache.get(
        cache_key
    )

    if cache_data:

        return JsonResponse(
            cache_data,
            safe=False
        )

    try:

        url = (
            "https://api.coingecko.com/"
            "api/v3/search/trending"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=503)


# ============================================================
# POPULAR
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def Popular(request):

    cache_key = "popular"

    cache_data = cache.get(
        cache_key
    )

    if cache_data:

        return JsonResponse(
            cache_data,
            safe=False
        )

    try:

        url = (
            "https://api.coingecko.com/"
            "api/v3/coins/markets"
        )

        response = requests.get(
            url,
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 12,
                "page": 1,
                "sparkline": "true",
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=503)


# ============================================================
# NOTIFICATIONS
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification(request):

    try:

        user = request.user

        notifications = (
            Notifications.objects
            .filter(user=user)
            .order_by("-created_at")
        )

        data = [

            {
                "id": n.id,
                "notification_type": n.type,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "icons": n.icons,
                "created_at": n.created_at.isoformat(),
            }

            for n in notifications
        ]

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ============================================================
# NOTIFICATION COUNT
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_count(request):

    user = request.user

    count = Notifications.objects.filter(
        user=user
    ).count()

    return JsonResponse({
        "count": count
    })


# ============================================================
# TRANSACTION COUNT
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_counter(request):

    user = request.user

    count = Transaction.objects.filter(
        user=user
    ).count()

    return JsonResponse({
        "count": count
    })


# ============================================================
# ALL TRANSACTIONS
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def AllTransactions(request):

    try:

        user = request.user

        transactions = (
            Transaction.objects
            .filter(user=user)
            .order_by("-created_at")
        )

        data = []

        for item in transactions:

            data.append({

                "id": item.id,

                "type": item.type,

                "icon": item.icon,

                "title": item.title,

                "message": item.message,

                "status": item.status,

                "coin": (
                    item.coin
                    if item.coin
                    else ""
                ),

                "quantity": (
                    str(item.quantity)
                    if item.quantity
                    else ""
                ),

                "Coin_quantity_balance": (
                    str(
                        item.Coin_quantity_balance
                    )
                    if item.Coin_quantity_balance
                    else ""
                ),

                "price_per_coin": (
                    str(
                        item.price_per_coin
                    )
                    if item.price_per_coin
                    else ""
                ),

                "amount": str(
                    item.amount
                ),

                "fee": (
                    str(item.fee)
                    if item.fee
                    else ""
                ),

                "created_at": (
                    item.created_at.isoformat()
                ),
            })

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ============================================================
# COIN MARKET CAPS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def coinMarketCaps(request):

    cache_key = "coinMarketCaps"

    cache_data = cache.get(
        cache_key
    )

    if cache_data:

        return JsonResponse(
            cache_data,
            safe=False
        )

    try:

        url = (
            "https://pro-api.coinmarketcap.com/"
            "v1/cryptocurrency/listings/latest"
        )

        headers = {
            "X-CMC_PRO_API_KEY":
                marketCapApiKey
        }

        params = {
            "limit": 1000
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        myData = data["data"]

        cache.set(
            cache_key,
            myData,
            timeout=300
        )

        return JsonResponse(
            myData,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ============================================================
# COIN CONVERSION
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def coinConversion(request):

    user = request.user

    amount = request.GET.get(
        "amount"
    )

    from_coin_id = request.GET.get(
        "fromCoinId"
    )

    to_coin_id = request.GET.get(
        "toCoinId"
    )

    fromName = request.GET.get(
        "fromName"
    )

    toName = request.GET.get(
        "toName"
    )

    try:

        url = (
            "https://pro-api.coinmarketcap.com/"
            "v2/tools/price-conversion"
        )

        headers = {
            "X-CMC_PRO_API_KEY":
                marketCapApiKey
        }

        params = {
            "amount": amount,
            "id": from_coin_id,
            "convert_id": to_coin_id,
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        result_Amount = (
            data["data"]
            ["quote"]
            [to_coin_id]
            ["price"]
        )

        notify = create_Notification(
            user=user,
            notification_type="Coin_Exchange",
            amount=amount,
            from_coin_id=fromName,
            result_Amount=result_Amount,
            to_coin_id=toName,
        )

        count = Notifications.objects.filter(
            user=user
        ).count()

        send_notification_update(
            user,
            notify,
            count
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ============================================================
# ALL COINS / PAGINATED MARKET
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def all_coins(request):

    try:

        page = int(
            request.GET.get(
                "page",
                1
            )
        )

        if page < 1:
            page = 1

    except ValueError:

        return JsonResponse({
            "success": False,
            "error": "Invalid page."
        }, status=400)

    cache.set(
        ACTIVE_MARKET_PAGE_KEY,
        page,
        None
    )

    market_cache = MarketCache()

    # ========================================================
    # CACHE HIT
    # ========================================================

    data = cache.get(
        f"market_page_{page}"
    )

    if data:

        return JsonResponse(
            data,
            safe=False
        )

    # ========================================================
    # ACQUIRE LOCK
    # ========================================================

    lock_acquired = (
        market_cache.acquire_lock(
            page
        )
    )

    # ========================================================
    # WE GOT THE LOCK
    # ========================================================

    if lock_acquired:

        try:

            data = market_cache.load(
                page
            )

            if data:

                return JsonResponse(
                    data,
                    safe=False
                )

            # ------------------------------------------------
            # FETCH MARKET DATA
            # ------------------------------------------------

            fetcher = MarketFetcher()

            data = fetcher.get_market_page(
                page=page,
                per_page=DEFAULT_PER_PAGE,
            )

            if data is None:

                return JsonResponse({
                    "error": (
                        "Unable to fetch "
                        "market data."
                    ),
                    "page": page,
                }, status=503)

            # ------------------------------------------------
            # SAVE CACHE
            # ------------------------------------------------

            market_cache.save(
                page,
                data
            )

            return JsonResponse(
                data,
                safe=False
            )

        finally:

            market_cache.release_lock(
                page
            )

    # ========================================================
    # SOMEONE ELSE IS FETCHING
    # ========================================================

    waited = 0

    while waited < 30:

        data = market_cache.load(
            page
        )

        if data:

            return JsonResponse(
                data,
                safe=False
            )

        time.sleep(
            CACHE_LOCK_WAIT
        )

        waited += CACHE_LOCK_WAIT

    return JsonResponse({
        "error": (
            "Market data is currently "
            "being fetched."
        ),
        "page": page,
    }, status=503)


# ============================================================
# TRENDING COINS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def list_Trending(request):

    cache_key = "trending_coins"

    cached = cache.get(
        cache_key
    )

    if cached:

        return JsonResponse(
            cached,
            safe=False
        )

    try:

        data = get_trending_coins()

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return JsonResponse(
            data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=503)


# ============================================================
# SEARCH COINS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def search_coins(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if not query:

        return JsonResponse({
            "success": True,
            "coins": []
        })

    fetcher = MarketFetcher()

    # ========================================================
    # SEARCH
    # ========================================================

    search_results = (
        fetcher.search_coins(
            query
        )
    )

    if search_results is None:

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to search "
                "coins right now."
            ),
            "code": "SEARCH_FAILED"
        }, status=503)

    if not search_results:

        return JsonResponse({
            "success": True,
            "coins": []
        })

    # ========================================================
    # COIN IDS
    # ========================================================

    coin_ids = [

        coin["id"]

        for coin in search_results[:10]

        if coin.get("id")

    ]

    if not coin_ids:

        return JsonResponse({
            "success": True,
            "coins": []
        })

    # ========================================================
    # MARKET DATA
    # ========================================================

    market_coins = (
        fetcher.fetch_coins_by_ids(
            coin_ids
        )
    )

    if market_coins is None:

        return JsonResponse({
            "success": False,
            "error": (
                "Coin market data is "
                "temporarily unavailable."
            ),
            "code": "MARKET_UNAVAILABLE"
        }, status=503)

    return JsonResponse({
        "success": True,
        "coins": market_coins
    })


# ============================================================
# LATEST NEWS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def fetch_latest_news(request):

    articles = (
        NewsArticle.objects
        .order_by("-published_at")[:50]
    )

    data = []

    for article in articles:

        data.append({

            "title": article.title,

            "description": (
                article.description
            ),

            "author": article.author,

            "source": article.source,

            "url": article.url,

            "source_name": (
                article.source_name
            ),

            "source_img": (
                article.source_img
            ),

            "image_url": (
                article.image_url
            ),

            "published_at": (
                article.published_at.isoformat()
                if article.published_at
                else None
            ),

            "category": (
                article.category
            ),
        })

    return JsonResponse({
        "success": True,
        "data": data,
    })


# ============================================================
# MARKET BRIEF
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def market_brief(request):

    cache_key = "market_brief"

    cached = cache.get(
        cache_key
    )

    if cached:

        return JsonResponse({
            "success": True,
            "data": cached,
        })

    try:

        global_data = (
            fetch_market_global_data()
        )


        data = {
            **global_data,
        }

        cache.set(
            cache_key,
            data,
            timeout=300
        )

        return JsonResponse({
            "success": True,
            "data": data,
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=503)



# ============================================================
# MARKET INSIGHTS
# ============================================================


def build_market_insights():

    articles = (
        NewsArticle.objects
        .filter(
            category__isnull=False
        )
        .exclude(
            category=""
        )
        .order_by(
            "-published_at"
        )[:20]
    )

    insights = []

    for article in articles:

        categories = (
            article.category.split("|")
        )

        symbol = next(
            (
                category

                for category in categories

                if category != "CRYPTOCURRENCY"

            ),
            None
        )

        if not symbol:

            continue

        insights.append({

            "title": article.title,

            "source": (
                article.source_name
            ),

            "url": article.url,

            "published_at": (
                article.published_at
            ),

            "symbol": symbol,

            "image_url": (
                article.image_url
            ),

            "source_img": (
                article.source_img
            ),
        })

        if len(insights) == 10:

            break

    return insights


# ============================================================
# GET MARKET INSIGHTS
# ============================================================


@api_view(["GET"])
@permission_classes([AllowAny])
def get_markets_insights(request):

    insights = (
        build_market_insights()
    )

    return JsonResponse({
        "success": True,
        "data": insights
    })


# ============================================================
# NEWS BY SECTION
# ============================================================



@api_view(["GET"])
@permission_classes([AllowAny])
def get_news_by_section(request):

    section = request.GET.get(
        "section"
    )

    if section == "all":

        articles = (
            NewsArticle.objects
            .order_by("-published_at")
        )

    else:

        articles = (
            NewsArticle.objects
            .filter(
                section=section
            )
            .order_by(
                "-published_at"
            )
        )

    news = []

    for article in articles:

        news.append({

            "id": article.id,

            "title": article.title,

            "description": (
                article.description
            ),

            "author": article.author,

            "source": article.source,

            "source_name": (
                article.source_name
            ),

            "source_img": (
                article.source_img
            ),

            "url": article.url,

            "image_url": (
                article.image_url
            ),

            "published_at": (
                article.published_at.isoformat()
                if article.published_at
                else None
            ),

            "category": (
                article.category
            ),

            "section": (
                article.section
            ),

            "popularity_score": (
                article.popularity_Score
            ),
        })

    return JsonResponse({

        "success": True,

        "data": news,

        "length": len(news),

        "section": section,

    })


# ============================================================
# MARKET SNAPSHOT
# ============================================================



@api_view(["GET"])
@permission_classes([AllowAny])
def get_market_snapshot(request):

    cache_key = "market_snapshot"

    snapshot = cache.get(
        cache_key
    )

    if not snapshot:

        return JsonResponse({
            "success": False,
            "data": []
        })

    return JsonResponse({
        "success": True,
        "data": snapshot,
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_if_authenticated(request):
    return Response({
        "authenticated": True,
        "user": {
            "username": request.user.username,
            "id": request.user.id,
            "email": request.user.email,
        }
    })


MARKET_CAP_RANGE = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "90d": timedelta(days=90),
    "1y": timedelta(days=365)
}

@require_GET
@api_view(["GET"])
@permission_classes([AllowAny])
def Market_Cap_Trend(request):

    # FULLTIME KING_SELAH REMEMBER TO PUSH ADD A HOSTING PROVIDER SCHEDULER, IT'S USING SYSTEM TASK SCHEDULER NOW
    
    selected_range = request.GET.get("range", "24h")

    duration = MARKET_CAP_RANGE.get(selected_range)
    
    if duration is None:
        return JsonResponse({
            "success": False,
            "error": "Invalid range",
            "supported_ranges": list(MARKET_CAP_RANGE),
        }, status=400)

    end_time = timezone.now()
    start_time = end_time - duration


    snapshots = MarketCapSnapShot.objects.filter(
        timeStamp__gte=start_time,
        timeStamp__lte=end_time
    ).order_by("timeStamp")

    merged_data = {
        snapshot.timeStamp.isoformat(): {
            "timestamp": snapshot.timeStamp.isoformat(),
            "market_cap": float(snapshot.market_cap_usd),
            "source": "database",
        }

        for snapshot in snapshots
    }


    cache_key = f"cmc_global_history_{selected_range}"
    historical_data = cache.get(cache_key)

    if historical_data is None:
        try:
            historical_data = get_global_market_cap_history(
                start_time,
                end_time,
                interval="daily"
            )

            cache.set(cache_key, historical_data, 3600)

        except Exception:
            # Keep locally collected data available if
            # the historical provider is temporarily down.
            historical_data = None


    if historical_data:
        for item in historical_data:
            timestamp = item["timestamp"]
            market_cap = item["market_cap"]

            from django.utils.dateparse import parse_datetime

            parsed_timestamp = parse_datetime(timestamp)

            if parsed_timestamp is None:
                continue

            if timezone.is_naive(parsed_timestamp):
                parsed_timestamp = timezone.make_aware(
                    parsed_timestamp,
                    timezone=timezone.utc,
                )

            if start_time <= parsed_timestamp <= end_time:
                key = parsed_timestamp.isoformat()

                merged_data.setdefault(key, {
                    "timestamp": key,
                    "market_cap": float(market_cap),
                    "source": "CoinMarketCap"
                })

    data = sorted(
        merged_data.values(),
        key=lambda item: item["timestamp"]
    )

    return JsonResponse({
        "success": True,
        "range": selected_range,
        "data": data,
        "count": len(data),
        "history_start": data[0]["timestamp"] if data else None,
        "history_end": data[-1]["timestamp"] if data else None,
    })




def fear_greed_view(request):
    try:
        data = fetch_fear_greed()
        return JsonResponse(data)

    except (ValueError, KeyError, TypeError):
        return JsonResponse(
            {"error": "Invalid Fear & Greed API response."},
            status=502,
        )

    except requests.RequestException:
        return JsonResponse(
            {"error": "Fear & Greed service is temporarily unavailable."},
            status=502,
        )



@api_view(["GET"])
def volume_price_correlation(request):

    symbol = request.query_params.get(
        "symbol",
        "BTCUSDT",
    ).upper()


    days = request.query_params.get("days", 1)

    import re
    
    if not re.fullmatch(
        r"[A-Z0-9]{5,20}",
        symbol
    ):
        return Response({
            "success": False,
            "message": "Invalid symbol"
        }, status=status.HTTP_400_BAD_REQUEST)


    try:
        data = get_volume_price_correlation(
            symbol=symbol,
            days=int(days)
        )

        print("VOLUME_DATA", data)

        return Response(data)

    except ValueError as error:
        return Response(
            {"success": False, "message": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except requests.RequestException as error:

        print("Error:", error)

        return Response(
            {
                "success": False,
                "message": "Binance market data unavailable.",
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )





