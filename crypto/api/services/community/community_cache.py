# Praise the LORD

from django.core.cache import cache


class CommunityCache:

    POSTS_KEY = "cmc_top_community_posts"
    TOKEN_KEY = "cmc_trending_tokens"

    TIMEOUT = 300

    @classmethod
    def get_posts(cls):
        return cache.get(cls.POSTS_KEY)

    @classmethod
    def set_posts(cls, posts):
        
        cache.set(cls.POSTS_KEY, posts, cls.TIMEOUT)

    @classmethod
    def get_token(cls):
        return cache.get(cls.TOKEN_KEY)

    @classmethod
    def set_token(cls, token):

        cache.set(cls.TOKEN_KEY, token, cls.TIMEOUT)

