from django.apps import AppConfig
import threading
import os


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):

        print("READY CALLED")

        try:

            from .services.market.Updater import MarketUpdater
            # from .services.newsUpdater import NewsUpdater

            print("Markets_Updater Imported Successfully")
            print("NewsUpdater Imported Successfully")

            markets_updater = MarketUpdater()
            # news_updater = NewsUpdater()
            #
            # threading.Thread(
            #     target=news_updater.run,
            #     daemon=True
            # ).start()

            threading.Thread(
                target=markets_updater.run,
                daemon=True
            ).start()

        except Exception as e:

            print(e)
