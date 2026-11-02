from django.core.management.base import BaseCommand

from ...services.news_service import save_crypto_news


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        count = save_crypto_news()

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved {count} news articles."
            )
        )