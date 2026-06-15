from django.urls import path
from . import views


urlpatterns = [
    path('list/', views.index, name='index'),
    path('exchange/', views.exchangerates, name='exchangerates'),
    path('chart_data2/<str:coin>/<int:days>/', views.chart_data2, name='chart_data2'),
    path('convert/', views.convert_currencies, name='convert_currencies'),
]