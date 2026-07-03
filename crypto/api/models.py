from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class Transaction(models.Model):
    TransactionType = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ("SELL", "sell coin"),
        ("BUY", "buy coin"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TransactionType)

    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    coin = models.CharField(max_length=10, null=True, blank=True)

    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    price_per_coin = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=100, default="")

    title = models.CharField(max_length=100, default="")

    message = models.TextField(default="")

    status = models.CharField(max_length=50, default="")




class CoinHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    average_buy_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class Notifications(models.Model):
    Types = (
        ("BUY", "Buy"),
        ("SELL", "Sell"),
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ("CURRENCY_CONVERTER", "Currency_Converter"),
        ("ALERT", "Price Alert"),
        ("SYSTEM", "System"),
        ("MESSAGE", "Message"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=Types)
    title = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField()
    icons = models.CharField(max_length=100, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
