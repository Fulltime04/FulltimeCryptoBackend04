import time

from .news_service import save_all_news


class NewsUpdater:

    def __init__(self, interval=60 * 60 * 16):
        self.interval = interval

    def run(self):

        print("NewsUpdater started")

        while True:

            try:
                print("Fetching crypto news...")

                count = save_all_news()

                print(
                    f"News update complete. "
                    f"Saved/updated: {count}"
                )

            except Exception as e:

                print(f"NewsUpdater error: {e}")

            print("Next news update in 8 hours...")

            time.sleep(self.interval)
