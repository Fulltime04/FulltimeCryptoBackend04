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
    path("search/",views.search_coins, name="search_coins"),

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


    path("news_list/", views.fetch_latest_news, name="fetch_latest_news"),

    path("market_brief/", views.market_brief, name="market_brief"),
    path("market_insights/", views.get_markets_insights, name="get_markets_insights"),
    path("markets_cap_trend/", views.Market_Cap_Trend, name="get_market_cap_trend"),
    path("fear_greed/", views.fear_greed_view, name="fear_greed_view"),
    path("volume_price_correlation/", views.volume_price_correlation, name="volume_price_correlation"),

    path("news/", views.get_news_by_section, name="get_news_by_section"),
    path("snap_shot/", views.get_market_snapshot, name="SnapShot"),

    path("check_authentication/", views.check_if_authenticated, name="check_authentication"),
]