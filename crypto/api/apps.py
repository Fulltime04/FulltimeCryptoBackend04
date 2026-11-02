import asyncio

from django.apps import AppConfig
import threading
import os
from channels.layers import get_channel_layer


class ApiConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        print("READY CALLED")

        try:

            from .services.market.Updater import (MarketUpdater, SnapShotUpdater)
            from .services.newsUpdater import NewsUpdater

            print("Markets_Updater Imported Successfully")
            print("NewsUpdater Imported Successfully")

            markets_updater = MarketUpdater()

            news_updater = NewsUpdater(
                interval=60 * 60 * 16
            )

            channel = get_channel_layer()
            snap_updater = SnapShotUpdater(channel)

            def run_Snap():

                print("SNAP SHOT RUNNING")

                asyncio.run(
                    snap_updater.run()
                )

            # threading.Thread(
            #     target=run_Snap,
            #     daemon=True
            # ).start()

            #
            # threading.Thread(
            #     target=news_updater.run,
            #     daemon=True
            # ).start()

            # threading.Thread(
            #     target=markets_updater.run,
            #     daemon=True
            # ).start()



            print("MarketUpdater started")
            print("NewsUpdater started")
            print("SnapShotUpdater started")

        except Exception as e:

            print(e)
