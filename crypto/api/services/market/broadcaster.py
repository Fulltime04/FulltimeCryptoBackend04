import logging

from ..utils import send_ws_update

logger = logging.getLogger(__name__)
import json

from channels.layers import get_channel_layer


class MarketBroadcaster:

    def broadcast(
        self,
        changed_coins,
    ):

        if not changed_coins:
            return

        payload = json.dumps(changed_coins)

        logger.info(
            "Broadcasting %s changed coins | Payload size: %s bytes",
            len(changed_coins),
            len(payload),
        )

        send_ws_update(
            group_name="market_group",
            data=changed_coins,
            event="market_update",
        )


class SnapShotBroadcaster:
    def __init__(self, channel_layer):
        self.channel_layer = channel_layer


    async def broadcast(self, coins):

        if not coins:
            return

        payload = json.dumps(coins)

        logger.info(
            "Broadcasting %s snapshot coins | Payload size: %s bytes",
            len(coins),
            len(payload),
        )

        await self.channel_layer.group_send(
            "snapshot_group",
            {
                "type": "snapshot_update",
                "data": coins,
            }
        )

        print("=" * 50)
        print("SENDING WEBSOCKET UPDATE")
        print("GROUP:", "snapshot_group")
        print("DATA:", coins)
        print("=" * 50)
