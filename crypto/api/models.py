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
    created_at = models.DateTimeField(auto_now_add=True)


class CoinHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
# Create your models here.
