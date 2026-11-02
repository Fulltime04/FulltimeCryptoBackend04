import time

from django.core.management.base import (BaseCommand,CommandError)
from ...services.market.market_cap_trend import collect_market_cap




class Command(BaseCommand):
    help = 'Collect global cryptocurrency market cap'

    def handle(self, *args, **options):
        while True:
            
            try:

                snapshot = collect_market_cap()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Saved market cap: "
                        f"${snapshot.market_cap_usd:,.2f}"
                    )
                )

            except Exception as e:
                self.stderr.write(str(e))

            time.sleep(600)
