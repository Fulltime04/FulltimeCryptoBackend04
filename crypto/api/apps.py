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

            print("Imported Successfully")

            updater = MarketUpdater()

            threading.Thread(
                target=updater.run,
                daemon=True
            ).start()

        except Exception as e:

            print(e)
