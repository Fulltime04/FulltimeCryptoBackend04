from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class Transaction(models.Model):
    TransactionType = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ("SELL", "sell coin"),
        ("BUY", "buy coin"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TransactionType)

    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    coin = models.CharField(max_length=10, null=True, blank=True)

    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    Coin_quantity_balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    price_per_coin = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=100, default="")

    title = models.CharField(max_length=100, default="")

    message = models.TextField(default="")

    status = models.CharField(max_length=50, default="")




class CoinHolding(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=Types)
    title = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField()
    icons = models.CharField(max_length=100, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class NewsArticle(models.Model):

    title = models.CharField(max_length=500)

    description = models.TextField(blank=True)

    author = models.TextField(max_length=200, blank=True)

    source = models.TextField(max_length=200, blank=True)

    url = models.URLField(unique=True)
    image_url = models.URLField(blank=True)


    source_name = models.TextField(max_length=100,blank=True)

    source_img = models.URLField(blank=True)

    published_at = models.DateTimeField()

    fetched_at = models.DateTimeField(auto_now_add=True)

    category = models.CharField(
        max_length=500,
        default="crypto",
    )

    section = models.CharField(
        max_length=100,
        default="news",
        db_index=True,
    )

    popularity_Score = models.FloatField(default=0)

    class Meta:
        ordering = ["-published_at"]



class TrendingPost(models.Model):

    title = models.CharField(max_length=500)

    description = models.TextField(
        blank=True,
        default=""
    )

    author = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    url = models.URLField(
        unique=True
    )

    image_url = models.URLField(
        blank=True,
        default=""
    )

    source_name = models.CharField(
        max_length=100,
        default="CoinMarketCap"
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    post_type = models.CharField(
        max_length=50,
        default="community"
    )

    popularity_score = models.FloatField(
        default=0
    )

    fetched_at = models.DateTimeField(
        auto_now=True
    )

    is_trending = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["-popularity_score", "-published_at"]

    def __str__(self):
        return self.title
# Create your models here.



class MarketCapSnapShot(models.Model):
    market_cap_usd = models.DecimalField(
        max_digits=30,
        decimal_places=2,
    )

    timeStamp = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        ordering = ["timeStamp"]

    def __str__(self):
        return f'Market cap ${self.market_cap_usd:,.2f}'
