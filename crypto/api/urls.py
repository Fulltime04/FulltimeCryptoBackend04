from cryptography.x509 import name
from django.urls import path
from . import views


urlpatterns = [
    path('wallet_data/', views.wallet_data, name='wallet_data'),
    path('notification/', views.notification, name='notification'),
    path('notification_count/', views.notification_count, name='notification_count'),
    path('transactions/', views.AllTransactions, name="All_Transactions"),
    path('transaction_counter/', views.transaction_counter, name='transaction_counter'),
    path('coinConversion/', views.coinConversion, name='coinConversion'),
    path('coinMarketCaps/', views.coinMarketCaps, name='coinMarketCaps'),
    path('all_Coins/', views.all_coins, name='all_coins'),
    path("list_Trending/", views.list_Trending, name='list_Trending'),

    path('list/', views.index, name='index'),
    path('exchange/', views.exchangerates, name='exchangerates'),
    path('chart_data2/<str:coin>/<int:days>/', views.chart_data2, name='chart_data2'),
    path('convert/', views.convert_currencies, name='convert_currencies'),
    path("trending/", views.Trending, name='Trending'),
    path("popular/", views.Popular, name='Popular'),

    path("deposit/", views.deposit),
    path("sell/", views.sell_coin),
    path("withdraw/", views.withdraw),
    path("buy/", views.buy_coin),
]