from django.urls import path
from . import views


urlpatterns = [
    path('wallet_data/', views.wallet_data, name='wallet_data'),
    path('notification/', views.notification, name='notification'),
    

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