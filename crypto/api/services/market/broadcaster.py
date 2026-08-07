import logging

from ..utils import send_ws_update

logger = logging.getLogger(__name__)


class MarketBroadcaster:

    def broadcast(
        self,
        changed_coins,
    ):

        if not changed_coins:
            return

        logger.info(
            "Broadcasting %s changed coins",
            len(changed_coins),
        )

        send_ws_update(
            group_name="market_group",
            data=changed_coins,
            event="market_update",
        )