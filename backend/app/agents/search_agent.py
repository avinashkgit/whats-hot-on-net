import feedparser
from urllib.parse import quote_plus

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def extract_real_link(entry):
    """
    Google News RSS puts the real publisher URL in entry.links
    """
    if hasattr(entry, "links"):
        for link in entry.links:
            if link.get("rel") == "alternate" and link.get("type") == "text/html":
                return link.get("href")

    # Fallbacks
    if hasattr(entry, "source") and "href" in entry.source:
        return entry.source["href"]

    return entry.link  # worst-case fallback


def search_news(topic, limit=5):
    query = quote_plus(topic.strip())
    url = f"{GOOGLE_NEWS_RSS}?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)

    results = []
    for entry in feed.entries:
        real_link = extract_real_link(entry)

        results.append({
            "title": entry.title,
            "link": real_link,
        })

        if len(results) >= limit:
            break

    return results
