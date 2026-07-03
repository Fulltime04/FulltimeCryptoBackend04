print("Consumers Initialized")

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class CryptoConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.wallet_group = "wallet_test"

        await self.channel_layer.group_add(
            self.wallet_group,
            self.channel_name
        )

        await self.accept()

        print("CONNECTED")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.wallet_group,
            self.channel_name
        )

        print("DISCONNECTED")

    async def send_update(self, event):
        print("SEND_UPDATE CALLED")
        
        payload = {
            **event["data"],
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