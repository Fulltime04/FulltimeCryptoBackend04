from .community_cache import CommunityCache
from .community_fetcher import CommunityFetcher
from .community_normalizer import CommunityNormalizer

from ...models import TrendingPost

class CommunityUpdater:

    def __init__(self):
        self.fetcher = CommunityFetcher()

    def update_posts(self):

        raw_response = self.fetcher.fetch_top_posts()

        raw_posts = raw_response.get(
            "data",
            []
        )

        normalized_posts = []

        for raw_post in raw_posts:

            post = CommunityNormalizer.normalize_post(
                raw_post,
            )

            if not post["url"]:
                continue

            TrendingPost.objects.update_or_create(
                url=post["url"],
                defaults=post
            )

            normalized_posts.append(post)


            return normalized_posts

