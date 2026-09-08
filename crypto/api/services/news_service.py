import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime

CRYPTOCOMPARE_NEWS_URL = "https://min-api.cryptocompare.com/data/v2/news/"

def _fetch_crypto_news(lang="EN", categories=None):
    """
    Fetch crypto news from CryptoCompare (CCData).
    Every article includes an imageurl field.
    Caches results for 5 minutes.
    """
    all_news = []

    cache_key = f"cryptocompare_news_{lang}_{categories}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    for page in range(1, 4):
        params = {
            "lang": lang,
            "limit": 50,
            "page": page,
          }

        if categories:
            params["categories"] = categories  # e.g. "BTC,ETH"

        if settings.CRYPTOCOMPARE_API_KEY:
            params["api_key"] = settings.CRYPTOCOMPARE_API_KEY

        try:
            response = requests.get(CRYPTOCOMPARE_NEWS_URL, params=params, timeout=10)

            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()

                articles = data.get("Data", [])

                for article in articles:
                    article["published_date"] = datetime.fromtimestamp(article["published_on"])

                all_news.extend(articles)

                cache.set(cache_key, all_news, timeout=300)

        except requests.RequestException as e:
            print(f"CryptoCompare API error: {e}")
            return []

    return all_news


# CRYPTOPANIC_BASE_URL = "https://cryptopanic.com/developers/api/v2/posts/"
#
# def _fetch_crypto_news(currencies=None, kind="all", filter_type=None):
#
#     cache_key = f'crypto_panic_{currencies}_{kind}_{filter_type}'
#     cache_data = cache.get(cache_key)
#
#     if cache_data:
#         return cache_data
#
#     params = {
#         "auth_token": settings.CRYPTO_PANIC_KEY,
#         "kind": kind,
#     }
#
#     if currencies:
#         params["currencies"] = currencies.strip(",")
#
#     if filter_type:
#         params["filter"] = filter_type
#
#     try:
#         response = requests.get(CRYPTOPANIC_BASE_URL, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#
#         results = data.get("results", [])
#
#         cache.set(cache_key, results, timeout=300)
#
#         return results
#
#     except Exception as e:
#         print(f"CryptoPanic API error: {e}")
#         return []





















# import requests
# from django.conf import settings
# from django.core.cache import cache
# from django.utils.dateparse import parse_datetime
# from django.http import JsonResponse
# # from ..models import NewsArticle
#
#
# NEWS_API_KEY = settings.NEWS_API_KEY
#
#
# def fetch_latest_news():
#
#     url = "https://pro-api.coingecko.com/api/v3/news"
#
#     headers = {
#         "x-cg-pro-api-key": NEWS_API_KEY
#     }
#
#     params = {
#         "page": 1,
#         "per_page": 20,
#         "language": "en",
#         "type": "news",
#     }
#
#     try:
#         response = requests.get(
#             url,
#             headers=headers,
#             params=params,
#             timeout=10
#         )
#
#         response.raise_for_status()
#
#         data = response.json()
#
#         return data.get("data", [])
#
#     except requests.RequestException as error:
#
#         print("Latest news error:", error)
#
#         return []
#
#
# # def fetch_trending_news():
# #     """
# #     Fetch popular/trending news from the external News API.
# #     """
# #
# #
# #     url = "https://pro-api.coingecko.com/api/v3/news"
# #
# #     headers = {
# #         "x-cg-pro-api-key": NEWS_API_KEY
# #     }
# #
# #     try:
# #         response = requests.get(
# #             url,
# #             params=params,
# #             timeout=10
# #         )
# #
# #         response.raise_for_status()
# #
# #         data = response.json()
# #
# #         return data.get("articles", [])
# #
# #     except requests.RequestException as error:
# #         print("Trending news error:", error)
# #
# #         return []
#
#
#
# def clean_article(article):
#     """
#     Clean and standardize an article received from the API.
#     """
#
#     published_at = parse_datetime(
#         article.get("publishedAt", "")
#     )
#
#     source = article.get("source") or {}
#
#     return {
#         "title": article.get("title") or "No title available",
#
#         "description": (
#             article.get("description")
#             or ""
#         ),
#
#         "author": (
#             article.get("author")
#             or "Unknown"
#         ),
#
#         "source": (
#             source.get("name")
#             or "Unknown"
#         ),
#
#         "url": article.get("url") or "",
#
#         "image_url": (
#             article.get("urlToImage")
#             or ""
#         ),
#
#         "published_at": published_at,
#     }
#
#
#
# def save_article(article, category="crypto"):
#     """
#     Save one cleaned article into the database.
#     """
#
#     article = clean_article(article)
#
#     if not article["url"]:
#         return None
#
#     news_article, created = (
#         NewsArticle.objects.update_or_create(
#
#             url=article["url"],
#
#             defaults={
#                 "title": article["title"],
#                 "description": article["description"],
#                 "author": article["author"],
#                 "source": article["source"],
#                 "image_url": article["image_url"],
#                 "published_at": article["published_at"],
#                 "category": category,
#             }
#         )
#     )
#
#     return news_article
#
#
#
# def update_news():
#     """
#     Fetch news from the external API and
#     save it into our database.
#     """
#
#     latest_articles = fetch_latest_news()
#
#     # trending_articles = fetch_trending_news()
#
#     for article in latest_articles:
#         save_article(
#             article,
#             category="latest"
#         )
#
#     # for article in trending_articles:
#     #     save_article(
#     #         article,
#     #         category="trending"
#     #     )
#     # Clear old cached news because
#     # the database has been updated.
#
#     cache.delete("full_news")
#
#
#
# def get_cache_news():
#
#     cache_key = "full_news"
#
#     cache_news = cache.get(cache_key)
#
#     if cache_news is not None:
#         return cache_news
#
#     try:
#         articles = NewsArticle.objects.all()
#
#         news = []
#
#         for article in articles:
#
#             news.append({
#                 "id": article.id,
#                 "title": article.title,
#                 "description": article.description,
#                 "author": article.author,
#                 "source": article.source,
#                 "url": article.url,
#                 "image_url": article.image_url,
#                 "published_at": article.published_at,
#                 "category": article.category,
#                 "popularity_score": article.popularity_Score,
#             })
#
#
#         cache.set(
#             cache_key,
#             news,
#             60 * 15
#         )
#
#         return news
#
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)