from django.core.management.base import BaseCommand

from ...services.market.Updater import (
    MarketUpdater,
)


class Command(BaseCommand):

    help = "Runs the market updater."

    def handle(
        self,
        *args,
        **options,
    ):

        updater = MarketUpdater()

        updater.run()