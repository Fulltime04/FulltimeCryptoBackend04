NEWS_SECTION_MAP = {
    # Market
    "MARKET": "markets",
    "TRADING": "markets",
    "EXCHANGE": "markets",

    # Finance / macro
    "MACROECONOMICS": "finance",
    "FIAT": "finance",
    "BUSINESS": "finance",

    # Regulation
    "REGULATION": "regulation",

    # Mining
    "MINING": "mining",

    # Blockchain / technology
    "BLOCKCHAIN": "blockchain",
    "TECHNOLOGY": "technology",

    # Security
    "SECURITY INCIDENTS": "security",

    # Wallet
    "WALLET": "wallet",

    # DeFi
    "DEFI": "defi",
}


def get_news_section(categories):
    """
    Convert the provider's categories into
    an F_Coins section.
    """

    if not categories:
        return "news"

    # CryptoCompare gives us something like:
    #
    # BTC|MARKET|REGULATION|CRYPTOCURRENCY
    #
    # Convert it into:
    #
    # ["BTC", "MARKET", "REGULATION", "CRYPTOCURRENCY"]

    category_list = [
        category.strip().upper()
        for category in categories.split("|")
        if category.strip()
    ]

    # Check our preferred sections first.
    for category in category_list:

        section = NEWS_SECTION_MAP.get(category)

        if section:
            return section

    # If nothing matched,
    # keep it under general news.
    return "news"

