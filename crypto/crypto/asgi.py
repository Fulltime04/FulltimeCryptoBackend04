# print("ASGI FILE LOADED")
# import os
#
# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "crypto.settings"
# )
#
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
#
#
# print("BEFORE ROUTING IMPORT")
#
# # from api.routing import websocket_urlpatterns
# #
# # print("AFTER ROUTING IMPORT")
# #
# # django_asgi_app = get_asgi_application()
# #
# # application = ProtocolTypeRouter({
# #     "http": django_asgi_app,
# #     "websocket": AuthMiddlewareStack(
# #         URLRouter(websocket_urlpatterns)
# #     ),
# # })
# #
# #
# # print("APPLICATION CREATED")
# #
# #
# # import os
# #
# # os.environ.setdefault(
# #     "DJANGO_SETTINGS_MODULE",
# #     "crypto.settings"
# # )
# #
# # from django.core.asgi import get_asgi_application
# #
# # from channels.routing import (
# #     ProtocolTypeRouter,
# #     URLRouter
# # )
#
# from accounts.middleware import (
#     JWTAuthMiddlewareStack
# )
#
# from api.routing import websocket_urlpatterns
#
#
# django_asgi_app = get_asgi_application()
#
#
# application = ProtocolTypeRouter({
#
#     "http": django_asgi_app,
#
#     "websocket": JWTAuthMiddlewareStack(
#
#         URLRouter(
#             websocket_urlpatterns
#         )
#
#     ),
#
# })


import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "crypto.settings"
)

from django.core.asgi import get_asgi_application


# Initialize Django first
django_asgi_app = get_asgi_application()


# Only import Channels/routing after Django is ready
from channels.routing import (
    ProtocolTypeRouter,
    URLRouter
)

from accounts.middleware import (
    JWTAuthMiddlewareStack
)

from api.routing import websocket_urlpatterns


application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),

})