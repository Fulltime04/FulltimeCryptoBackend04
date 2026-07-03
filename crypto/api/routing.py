print("Route Initialized")
from django.urls import path
from .consumers import CryptoConsumer

websocket_urlpatterns = [
    path("ws/crypto/", CryptoConsumer.as_asgi()),
]