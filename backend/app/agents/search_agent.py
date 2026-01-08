import feedparser
from urllib.parse import quote_plus

from .google_news_decoder import decode_google_news_url

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def search_news(topic, limit=5):
    query = quote_plus(topic.strip())
    url = f"{GOOGLE_NEWS_RSS}?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)

    results = []
    for entry in feed.entries:
        raw_link = entry.link
        decoded_link = decode_google_news_url(raw_link)

        final_link = decoded_link or raw_link

        results.append(
            {
                "title": entry.title,
                "link": final_link,
                "summary": getattr(entry, "summary", ""),
            }
        )

        if len(results) >= limit:
            break

    return results
