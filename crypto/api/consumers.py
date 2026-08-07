print("Consumers Initialized")

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs
from django.core.cache import cache

class CryptoConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        query = parse_qs(
            self.scope["query_string"].decode()
        )

        group = query.get("group", ["wallet"])[0]

        print("Query: ", query)

        if group == "market":
            self.group_name = "market_group"
            count = cache.get("market_connection", 0)
            cache.set("market_connection", count + 1)

        elif group == "wallet":
            self.group_name = "wallet_group"

        else:
            self.group_name = "general_group"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        print(f"CONNECTED -> {self.group_name}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        if self.group_name == "market_group":
            count = cache.get("market_connection", 0)

            if count > 0:
                cache.set("market_connection", count - 1)

        print(f"DISCONNECTED -> {self.group_name}")

    async def send_update(self, event):
        print("SEND_UPDATE CALLED")
        
        payload = {
            "event": event.get("event"),
            "data": event.get("data"),
            "timestamp": event.get("timestamp"),
            "notification_count": event.get("notification_count"),
            "transaction_count": event.get("transaction_count")
        }

        await self.send(
            text_data=json.dumps(payload)
        )



# class CryptoConsumer(AsyncWebsocketConsumer):
#
#     async def connect(self):
#         self.wallet_group = "wallet_test"
#
#         await self.channel_layer.group_add(
#             self.wallet_group,
#             self.channel_name
#         )
#
#         await self.accept()
#
#         print("CONNECTED")
#
#
#         await self.accept()
#
#         await self.send(
#             text_data=json.dumps({
#                 "message": "Welcome Fulltime"
#             })
#         )
#
#         print("WebSocket Connected")
#
#     async def disconnect(self, close_code):
#
#         await self.channel_layer.group_discard(
#             self.wallet_group,
#             self.channel_name
#         )
#
#         print("WebSocket Disconnected")
#
#     async def receive(self, text_data):
#
#         data = json.loads(text_data)
#
#         print("Received:", data)
#
#         await self.send(
#             text_data=json.dumps({
#                 "response": f"You said: {data['message']}"
#             })
#         )
#
#     async def send_update(self, event):
#         print("=" * 50)
#         print("SEND_UPDATE CALLED")
#         print("EVENT:", event)
#         print("=" * 50)
#
#         await self.send(
#             text_data=json.dumps(
#                 event["data"]
#             )
#         )