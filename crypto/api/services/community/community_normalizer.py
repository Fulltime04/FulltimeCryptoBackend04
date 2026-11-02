# Praise the LORD

'''
Fulltime
'''

class CommunityNormalizer:

    @staticmethod
    def normalize_post(post):

        return {
            "title": post.get("title", ""),
            "description": post.get("description", ""),
            "author": post.get("author", ""),
            "url": post.get("url", ""),
            "image_url": post.get("image_url", ""),
            "source_name": "CoinMarketCap",
            "published_at": post.get("published_at"),
            "post_type": "community",
        }
