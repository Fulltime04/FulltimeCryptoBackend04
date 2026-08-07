from django.core.mail import message
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.conf import settings
import requests
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import (Wallet, CoinHolding, Transaction, Notifications)
from decimal import Decimal
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from .services.cryptocompare import (NOTIFICATION_BANK, CURRENCY_TO_COUNTRY, get_chart_data2, TRANSACTION_CARD_BANK, get_trending_coins)
import random
from .services.utils import (send_wallet_update, send_notification_update, get_wallet_stats, send_transaction_update)



marketCapApiKey = settings.COIN_MARKET_API_KEY

print(marketCapApiKey)
# --------------------- BEGINS ----------------------

@csrf_exempt
@transaction.atomic
def deposit(request):
    try:
        amount = Decimal(request.POST.get("amount"))
        user = User.objects.get(username='fulltime')

        wallet, created = Wallet.objects.get_or_create(user=user)

        wallet.balance += amount
        wallet.save()


        transact = createTransaction(
            user=user,
            transactionType="DEPOSIT",
            amount=amount
        )

        transaction_count = Transaction.objects.filter(user=user).count()

        notify = create_Notification(
            user=user,
            notification_type="DEPOSIT",
            amount=amount,
        )

        count = Notifications.objects.filter(user=user).count()

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

        send_transaction_update(user, transact, transaction_count)

        return JsonResponse({
            "success": True,
            "balance": str(wallet.balance)
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)



@csrf_exempt
@transaction.atomic
def withdraw(request):
    try:
        amount = Decimal(request.POST.get("amount"))
        user = User.objects.get(username='fulltime')
        wallet = Wallet.objects.get(user=user)


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

        transaction_count = Transaction.objects.filter(user=user).count()

        notify = create_Notification(
            user=user,
            notification_type="WITHDRAW",
            amount=amount,
        )

        count = Notifications.objects.filter(user=user).count()

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

        send_transaction_update(user, transact, transaction_count)


        return JsonResponse({
            "success": True,
            "balance": str(wallet.balance)
        })


    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)




@csrf_exempt
@transaction.atomic
def sell_coin(request):
    try:
        user = User.objects.get(username="fulltime")

        coin = request.POST.get("coin", "btc")
        current_price = Decimal(request.POST.get("price", "0"))
        quantity = Decimal(request.POST.get("quantity", "0"))

        # ---------------------------
        # VALIDATIONS
        # ---------------------------

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

        # ---------------------------
        # CHECK HOLDING
        # ---------------------------

        holding = CoinHolding.objects.select_for_update().filter(
            user=user,
            coin=coin
        ).first()

        if not holding:
            return JsonResponse({
                "success": False,
                "error": f"You do not own any {coin}"
            }, status=400)

        print({
            "coin": coin,
            "holding_quantity": str(holding.quantity),
            "requested_quantity": str(quantity)
        })

        if holding.quantity < quantity:
            return JsonResponse({
                "success": False,
                "error": (
                    f"Insufficient coin balance. "
                    f"You own {holding.quantity} {coin} "
                    f"but tried to sell {quantity}."
                )
            }, status=400)

        # ---------------------------
        # CALCULATIONS
        # ---------------------------

        avg_buy_price = holding.average_buy_price

        gross_amount = quantity * current_price

        fee_rate = Decimal("0.001")  # 0.1%
        fee = gross_amount * fee_rate

        received = gross_amount - fee

        cost_basis = quantity * avg_buy_price

        profit = received - cost_basis

        # ---------------------------
        # UPDATE WALLET
        # ---------------------------

        wallet = Wallet.objects.select_for_update().get(user=user)

        wallet.balance += received
        wallet.save()

        # ---------------------------
        # UPDATE HOLDINGS
        # ---------------------------

        old_quantity = holding.quantity

        holding.quantity -= quantity

        if holding.quantity <= 0:
            holding.delete()
            remaining_quantity = Decimal("0")
        else:
            holding.save()
            remaining_quantity = holding.quantity

        # ---------------------------
        # SAVE TRANSACTION
        # ---------------------------

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

        transaction_count = Transaction.objects.filter(user=user).count()

        notify = create_Notification(
            user=user,
            notification_type="SELL",
            amount=received,
            quantity=quantity,
            coin=coin
        )

        count = Notifications.objects.filter(user=user).count()

        print({
            "coin": coin,
            "old_quantity": str(old_quantity),
            "sold_quantity": str(quantity),
            "remaining_quantity": int(remaining_quantity),
            "received": str(received),
            "profit": str(profit),
            "wallet_balance": str(wallet.balance)
        })

        send_wallet_update(
            user=user,
            transaction_type="SELL",
            amount=received,
            coin=coin,
            quantity=quantity
        )

        send_notification_update(user,notify, count)

        send_transaction_update(user, transact, transaction_count)

        return JsonResponse({
            "success": True,
            "coin": coin,
            "sold_quantity": str(quantity),
            "remaining_quantity": int(remaining_quantity),
            "balance": str(wallet.balance),
            "received": str(received),
            "profit": str(profit),
            "fee": str(fee),
            "avg_buy_price": str(avg_buy_price),
            "Coin_quantity_balance": str(transact.Coin_quantity_balance),
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


@csrf_exempt
@transaction.atomic
def buy_coin(request):
    try:
        user = User.objects.get(username='fulltime')

        coin = request.POST.get("coin")

        # 🟢 THIS IS NOW COIN QUANTITY (NOT USD)
        quantity = Decimal(request.POST.get("quantity"))

        if quantity <= 0:
            return JsonResponse({
                "success": False,
                "error": "Quantity must be greater than 0"
            }, status=400)

        current_price = Decimal(request.POST.get("price"))

        wallet = Wallet.objects.select_for_update().get(user=user)

        # 💰 TOTAL COST = quantity × price
        total_cost = quantity * current_price

        if wallet.balance < total_cost:
            return JsonResponse({
                "success": False,
                "error": "Insufficient balance"
            }, status=400)

        # 💸 fee is based on actual money spent
        fee_rate = Decimal("0.001")
        fee = total_cost * fee_rate

        total_cost_with_fee = total_cost + fee

        # 📦 update holdings
        holding, _ = CoinHolding.objects.select_for_update().get_or_create(
            user=user,
            coin=coin,
            defaults={
                "quantity": Decimal("0"),
                "average_buy_price": Decimal("0")
            }
        )

        old_qty = holding.quantity
        old_avg = holding.average_buy_price

        new_total_qty = old_qty + quantity

        # 📊 weighted average price
        if new_total_qty > 0:
            holding.average_buy_price = (
                (old_qty * old_avg) + (quantity * current_price)
            ) / new_total_qty

        holding.quantity = new_total_qty
        holding.save()

        # 💳 deduct wallet
        wallet.balance -= total_cost_with_fee
        wallet.save()

        # 🧾 log transaction
        transact = createTransaction(
            user=user,
            transactionType="BUY",
            coin=coin,
            amount=total_cost,   # money spent before fee (or include fee if you want)
            quantity=quantity,
            price_per_coin=current_price,
            fee=fee,
            Coin_quantity_balance=new_total_qty,
        )

        transaction_count = Transaction.objects.filter(user=user).count()

        notify = create_Notification(
            user=user,
            notification_type="BUY",
            amount=total_cost,
            quantity=quantity,
            coin=coin,
        )
        count = Notifications.objects.filter(user=user).count()

        send_wallet_update(
            user=user,
            transaction_type="BUY",
            amount=total_cost,
            coin=coin,
            quantity=quantity
        )

        send_notification_update(user, notify, count)

        send_transaction_update(user, transact, transaction_count)

        print("coin_balance:", transact.Coin_quantity_balance)

        return JsonResponse({
            "success": True,
            "balance": str(wallet.balance),
            "quantity": str(holding.quantity),
            "average_buy_price": str(holding.average_buy_price),
            "fee": str(fee),
            "cost": str(total_cost_with_fee),
            "Coin_quantity_balance": str(transact.Coin_quantity_balance),
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)



def wallet_data(request):
    try:
        user = User.objects.get(username='fulltime')

        data = get_wallet_stats(user)

        return JsonResponse({
            "success": True,
            **data
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



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





def chart_data2(request, coin, days):
    try:

        data = get_chart_data2(
            coin,
            days
        )

        return JsonResponse(data, safe=False)

    except requests.exceptions.HTTPError as e:
        print(f"Coin: {coin}")
        print(f"Error: {e}")

        if e.response.status_code == 429:
            return JsonResponse({
                "success": False,
                "error": "Rate_limit_exceeded"
            }, status=429)

        return JsonResponse({
            "error": str(e)
        }, status=400)


def convert_currencies(request):
    user = User.objects.get(username='fulltime')
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

        notify = create_Notification(
            user=user,
            notification_type="CURRENCY_CONVERTER",
            from_amount=amount,
            from_Currency=from_Currency,
            to_amount=result,
            to_Currency=to_Currency,
        )

        count = Notifications.objects.filter(user=user).count()

        send_notification_update(
            user,
            notify,
            count
        )


        return JsonResponse({
            "rates": rates,
            "result": round(result, 2)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return JsonResponse({"error": str(e)}, status=500)



Exchange_Api_Key = settings.EXCHANGE_RATE_API_KEY
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



def Trending(request):
    cache_key = f"trending"
    cache_data = cache.get(cache_key)

    if cache_data:
        return JsonResponse(cache_data, safe=False)

    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url)
        data = response.json()

        cache.set(cache_key, data, timeout=300)

        return JsonResponse(data,safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def Popular(request):
    cache_key = "popular"
    cache_data = cache.get(cache_key)

    if cache_data:
        return JsonResponse(cache_data, safe=False)

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=12&page=1&sparkline=true"

        response = requests.get(url)
        data = response.json()

        cache.set(cache_key, data, timeout=300)

        return JsonResponse(data,safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def create_Notification(user, notification_type, **kwargs):
    template = NOTIFICATION_BANK[notification_type]

    title = template["title"]

    message = random.choice(
        template["messages"]
    ).format(**kwargs)

    icons = random.choice(template["icons"])


    notify = Notifications.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        icons=icons,
    )


    return notify



def notification(request):
    try:
        user = User.objects.get(username='fulltime')

        notifications = (
            Notifications.objects.filter(user=user).order_by("-created_at")
        )


        data = [
            {
                "id": n.id,
                "notification_type": n.type,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "icons": n.icons,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




def notification_count(request):
    user = User.objects.get(username='fulltime')
    count = Notifications.objects.filter(user=user).count()

    return JsonResponse({
        "count": count
    })

def transaction_counter(request):
    user = User.objects.get(username='fulltime')
    count = Transaction.objects.filter(user=user).count()

    return JsonResponse({
        "count": count
    })


import random

def createTransaction(user, transactionType, **kwargs):

    template = TRANSACTION_CARD_BANK[transactionType]

    transact = Transaction.objects.create(
        user=user,
        type=transactionType,

        icon=random.choice(template["icons"]),
        title=random.choice(template["titles"]),
        message=random.choice(template["messages"]).format(**kwargs),
        status=random.choice(template["status"]),

        **kwargs
    )

    return transact



def AllTransactions(request):
    try:
        user = User.objects.get(username="fulltime")

        transactions = (
            Transaction.objects
            .filter(user=user)
            .order_by("-created_at")
        )

        data = []

        for transaction in transactions:

            template = TRANSACTION_CARD_BANK[transaction.type]

            data.append({
                "id": transaction.id,

                "type": transaction.type,

                "icon": transaction.icon,

                "title": transaction.title,

                "message": transaction.message,

                "status": transaction.status,

                "coin": (
                    transaction.coin
                    if transaction.coin else ""
                ),


                "quantity": str(transaction.quantity if transaction.quantity else ""),

                "Coin_quantity_balance": str(transaction.Coin_quantity_balance if transaction.quantity else ""),

                "price_per_coin": str(transaction.price_per_coin if transaction.price_per_coin else ""),

                "amount": str(transaction.amount),

                "fee": str(transaction.fee if transaction.fee else ""),

                "created_at": transaction.created_at,
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


def coinMarketCaps(request):
    cache_key = "coinMarketCaps"
    cache_data = cache.get(cache_key)

    if cache_data:
        return JsonResponse(cache_data, safe=False)

    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers = {
            "X-CMC_PRO_API_KEY": marketCapApiKey
        }
        params = {
            "limit": 1000,
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        myData = data["data"]

        return JsonResponse(myData, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def coinConversion(request):
    amount = request.GET.get("amount")
    from_coin_id = request.GET.get("fromCoinId")
    to_coin_id = request.GET.get("toCoinId")
    user = User.objects.get(username='fulltime')

    fromName = request.GET.get("fromName")
    toName = request.GET.get("toName")

    try:
        url = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"

        headers = {
            "X-CMC_PRO_API_KEY": marketCapApiKey
        }

        params = {
            "amount": amount,
            "id": from_coin_id,
            "convert_id": to_coin_id,
        }


        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        result_Amount = data["data"]["quote"][to_coin_id]["price"]
        print(result_Amount)

        notify = create_Notification(
            user=user,
            notification_type="Coin_Exchange",
            amount=amount,
            from_coin_id=fromName,
            result_Amount=result_Amount,
            to_coin_id=toName,
        )

        count = Notifications.objects.filter(user=user).count()

        send_notification_update(
            user,
            notify,
            count
        )

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.core.cache import cache

def all_coins(request):

    page = int(request.GET.get("page", 1))

    data = cache.get(f"market_page_{page}")


    if data is None:
        return JsonResponse(
            {
                "error": "Market data not ready."
            },
            status=503
        )

    return JsonResponse(
        data,
        safe=False
    )





def list_Trending(request):

    cache_key = "trending_coins"

    cached = cache.get(cache_key)

    if cached:

        return JsonResponse(cached, safe=False)

    data = get_trending_coins()

    cache.set(cache_key, data, timeout=300)

    return JsonResponse(data, safe=False)











