from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import Sum
from django.conf import settings
import random
import time
from ..models import Wallet, Transaction,Notifications
from ..services.cryptocompare import (NOTIFICATION_BANK, CURRENCY_TO_COUNTRY, get_chart_data2, TRANSACTION_CARD_BANK)
from django.utils import timezone

# from ...crypto import settings


def send_ws_update(group_name, data, **extra):

    print("=" * 50)
    print("SENDING WEBSOCKET UPDATE")
    print("GROUP:", group_name)
    # print("DATA:", data)
    print("=" * 50)

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_update",
            "data": data,
            "timestamp": timezone.now().timestamp(),
            **extra
        },

    )



def get_wallet_stats(user):
    wallet, _ = Wallet.objects.get_or_create(
        user=user
    )

    expenses = (
        Transaction.objects.filter(
            user=user,
            type="BUY"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    income = (
        Transaction.objects.filter(
            user=user,
            type="SELL"
        ).aggregate(
            total=Sum("profit")
        )["total"]
        or 0
    )

    income = max(income, 0)

    return {
        "balance": str(wallet.balance),
        "income": str(income),
        "expenses": str(expenses),
    }


def send_wallet_update(
    user,
    transaction_type,
    amount="0",
    coin=None,
    quantity="0",
):

    stats = get_wallet_stats(user)


    transaction.on_commit(
        lambda: send_ws_update(
            "wallet_group",
            {
                "type": "wallet_update",
                "transaction_type": transaction_type,
                "amount": str(amount),
                 **stats
            },
            event="wallet_update"   
        )
    )


def send_notification_update(user, notification,count):
    print("My USER", user)


    print("NOTIFICATION ID:", notification.id)
    print("TITLE:", notification.title)
    print("MESSAGE:", notification.message)
    print("TYPE:", notification.type)
    print("NOTIFICATION COUNT:", count)

    send_ws_update(
        "wallet_group",
        {
            "type": "notification",
            "notification": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.type,
                "icons": notification.icons,
            },
        },
        event="notification_update",
        notification_count=count,
    )


def send_transaction_update(user, transaction, count):
    print("My USER", user)

    print("TRANSACTION ID:", transaction.id)
    print("TRANSACTION TITLE:", transaction.title)
    print("TRANSACTION MESSAGE:", transaction.message)
    print("TRANSACTION TYPE:", transaction.type)
    print("TRANSACTION COUNT:", count)

    send_ws_update(
        "wallet_group",
        {
            "type": "transaction",
            "transaction": transaction_to_dict(transaction)
        },
       event="transaction_update",
       transaction_count=count
    )


def transaction_to_dict(transaction):

    return {
        "id": transaction.id,
        "type": transaction.type,

        "icon": transaction.icon,
        "title": transaction.title,
        "message": transaction.message,
        "status": transaction.status,

        "amount": str(transaction.amount),
        "coin": transaction.coin or "",
        "quantity": str(transaction.quantity),
        "price_per_coin": str(transaction.price_per_coin),
        "profit": str(transaction.profit),
        "fee": str(transaction.fee),
        "Coin_quantity_balance": str(transaction.Coin_quantity_balance),
        "createdAt": transaction.created_at.isoformat(),
    }








