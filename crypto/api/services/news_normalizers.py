from datetime import datetime, timezone
from django.utils import timezone as django_timezone


def normalize_cryptocompare(article):
    """
    Convert a CryptoCompare article into
    the format used by F_Coins.
    """

    source_info = article.get("source_info", {})

    categories = article.get("categories", "")

    published_at = None

    published_on = article.get("published_on")

    if published_on:
        published_at = datetime.fromtimestamp(
            published_on,
            tz=timezone.utc
        )

    return {
        "title": article.get("title", ""),
        "description": article.get("body", ""),
        "author": article.get("authors", ""),
        "source": article.get("source", ""),

        "url": article.get("url", ""),

        "image_url": article.get("imageurl", ""),

        "source_name": source_info.get("name", ""),
        "source_img": source_info.get("img", ""),

        "published_at": published_at,

        "category": categories,
    }


def normalize_newsdata(article):
    """
    Convert a NewsData.io article into
    the format used by F_Coins.
    """

    categories = article.get("category", [])

    if isinstance(categories, list):
        categories = "|".join(categories)

    else:
        categories = str(categories or "")

    published_at = None

    pub_date = article.get("pubDate")

    if pub_date:

        try:

            published_at = datetime.fromisoformat(
                pub_date.replace("Z", "+00:00")
            )

            if published_at.tzinfo is None:
                published_at = django_timezone.make_aware(
                    published_at
                )

        except ValueError:

            published_at = None

    return {
        "title": article.get("title", ""),
        "description": article.get("description") or "",
        "author": article.get("creator", "") or "",

        "source": article.get("source_name", ""),

        "url": article.get("link", ""),

        "image_url": article.get("image_url", "") or "",

        "source_name": article.get("source_name", ""),
        "source_img": article.get("source_icon", "") or "",

        "published_at": published_at,

        "category": categories,
    }