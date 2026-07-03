print("ASGI FILE LOADED")
import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "crypto.settings"
)

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


print("BEFORE ROUTING IMPORT")

from api.routing import websocket_urlpatterns

print("AFTER ROUTING IMPORT")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})


print("APPLICATION CREATED")