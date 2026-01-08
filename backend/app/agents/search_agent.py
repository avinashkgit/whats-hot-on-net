import feedparser
from urllib.parse import quote_plus


def search_news(topic, limit=5):
    query = quote_plus(topic.strip())
    url = (
        "https://news.google.com/rss/search"
        f"?q={query}&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(url)

    results = []
    for entry in feed.entries[:limit]:
        results.append({
            "title": entry.title,
            "link": entry.link,
        })
    return results
