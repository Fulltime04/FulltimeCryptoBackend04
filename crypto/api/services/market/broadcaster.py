import logging

from ..utils import send_ws_update

logger = logging.getLogger(__name__)
import json


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