import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timezone
from ..models import NewsArticle
from .news_categorizers import get_news_section

from .news_normalizers import (normalize_cryptocompare, normalize_newsdata)


NEWSDATA_CRYPTO_URL = "https://newsdata.io/api/1/crypto"

def fetch_newsData_crypto():

    cache_key = "newsData_crypto_news"

    cached = cache.get(cache_key)

    if cached:
        return cached

    all_articles = []

    next_page = None

    try:

        for page_number in range(3):

            params = {
                "apikey": settings.NEWS_DATA_API_KEY,
                "language": "en",
                "size": 10,
            }

            # Only send "page" after the first request
            if next_page:
                params["page"] = next_page

            response = requests.get(
                NEWSDATA_CRYPTO_URL,
                params=params,
                timeout=10
            )

            print(
                f"NewsData PAGE {page_number + 1} URL:",
                response.url
            )

            print(
                "NewsData STATUS:",
                response.status_code
            )

            response.raise_for_status()

            data = response.json()

            articles = data.get("results", [])

            print(
                f"ARTICLES THIS PAGE: {len(articles)}"
            )

            all_articles.extend(articles)

            # Get the token for the next request
            next_page = data.get("nextPage")

            # Stop if NewsData has no more pages
            if not next_page:
                print("No more NewsData pages.")
                break

        cache.set(
            cache_key,
            all_articles,
            timeout=60 * 60 * 6
        )

        print(
            "TOTAL NEWSDATA ARTICLES:",
            len(all_articles)
        )

        return all_articles

    except requests.RequestException as e:

        print("NEWS_DATA:", e)

        return []



CRYPTOCOMPARE_NEWS_URL = "https://min-api.cryptocompare.com/data/v2/news/"



def _fetch_crypto_news(lang="EN", categories="BTC,ETH,SOL,XRP"):

    all_news = []

    cache_key = f"cryptocompare_news_{lang}_{categories}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    for page in range(1,3):

        params = {
            "lang": lang,
            "limit": 50,
            "page": page,
        }

        if categories:
            params["categories"] = categories

        if settings.CRYPTOCOMPARE_API_KEY:
            params["api_key"] = settings.CRYPTOCOMPARE_API_KEY

        try:
            response = requests.get(
                CRYPTOCOMPARE_NEWS_URL,
                params=params,
                timeout=10
            )

            print("URL:", response.url)
            print("STATUS:", response.status_code)

            response.raise_for_status()

            data = response.json()

            print("API RESPONSE:", data)

            articles = data.get("Data", [])

            print("ARTICLES THIS PAGE:", len(articles))

            for article in articles:

                if article.get("published_on"):
                    article["published_date"] = datetime.fromtimestamp(
                        article["published_on"], tz=timezone.utc
                    )

                all_news.append(article)

        except requests.RequestException as e:

            print(f"CryptoCompare API error: {e}")

            return []

    cache.set(
        cache_key,
        all_news,
        timeout=300
    )

    print("TOTAL NEWS:", len(all_news))

    return all_news





def save_crypto_news():

    articles = _fetch_crypto_news()

    if not articles:
        print("No articles received from CryptoCompare.")
        return 0

    saved_count = 0

    for article in articles:

        normalized = normalize_cryptocompare(article)

        if not normalized["url"]:
            continue

        if not normalized["published_at"]:
            continue

        categories = normalized["category"]

        section = get_news_section(categories)

        NewsArticle.objects.update_or_create(

            url=normalized["url"],

            defaults={

                "title": normalized["title"],

                "description": normalized["description"],

                "author": normalized["author"],

                "source": normalized["source"],

                "image_url": normalized["image_url"],

                "source_img": normalized["source_img"],

                "source_name": normalized["source_name"],

                "published_at": normalized["published_at"],

                "category": normalized["category"],

                "section": section,

                "popularity_Score": 0,
            }
        )

        saved_count += 1

    print(f"SAVED_NEWS: {saved_count}")

    return saved_count



def save_newsdata_news():

    articles = fetch_newsData_crypto()

    if not articles:
        print("No articles received from NewsData.")
        return 0

    saved_count = 0

    for article in articles:

        normalized = normalize_newsdata(article)

        if not normalized["url"]:
            continue

        if not normalized["published_at"]:
            continue

        categories = normalized["category"]

        section = get_news_section(categories)

        NewsArticle.objects.update_or_create(

            url=normalized["url"],

            defaults={

                "title": normalized["title"],

                "description": normalized["description"] or "",

                "author": normalized["author"],

                "source": normalized["source"],

                "image_url": normalized["image_url"],

                "source_img": normalized["source_img"],

                "source_name": normalized["source_name"],

                "published_at": normalized["published_at"],

                "category": normalized["category"],

                "section": section,

                "popularity_Score": 0,
            }
        )

        saved_count += 1

    print(f"NEWS_DATA SAVED: {saved_count}")

    return saved_count



def save_all_news():

    crypto_count = save_crypto_news()

    newsdata_count = save_newsdata_news()

    total_count = crypto_count + newsdata_count

    print(f"TOTAL NEWS SAVED/UPDATED: {total_count}")

    return total_count












# {'id': '71411705', 'guid': 'https://en.coin-turk.com/?p=248398', 'published_on': 1789009871, 'imageurl': 'https://resources.cryptocompare.com/news/79/71411705.jpeg', 'title': 'Block seeks OCC approval to launch Builders Bank for Bitcoin and stablecoin custody', 'url': 'https://en.coin-turk.com/block-seeks-occ-approval-to-launch-builders-bank-for-bitcoin-and-stablecoin-custody/?utm_source=rss&utm_medium=rss&utm_campaign=block-seeks-occ-approval-to-launch-builders-bank-for-bitcoin-and-stablecoin-custody', 'body': '🚨 Block seeks OCC approval to launch Builders Bank for Bitcoin and stablecoins custody. 🪙 Builders Bank would focus on custody, not accept deposits or offer FDIC insurance. 💼 Lee Woolley, with 20 years in finance, is named to lead the new $BTC-focused entity. 📌 This application marks Block’s latest push to expand digital asset services through federal regulation. Continue Reading: Block seeks OCC approval to launch Builders Bank for Bitcoin and stablecoin custody The post Block seeks OCC approval to launch Builders Bank for Bitcoin and stablecoin custody appeared first on COINTURK NEWS .', 'tags': 'Cryptocurrency News', 'lang': 'EN', 'upvotes': '0', 'downvotes': '0',
# 'categories': 'BTC|FIAT|REGULATION|CRYPTOCURRENCY', 'source_info': {'name': 'CoinTurk News', 'img': 'https://resources.cryptocompare.com/news/79/default.png', 'lang': 'EN'}, 'source': 'cointurken'}



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