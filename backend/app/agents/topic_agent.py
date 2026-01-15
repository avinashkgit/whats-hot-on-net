import feedparser
import random
import re
from sqlalchemy.orm import Session

from app.db.models import Article
from .google_news_decoder import decode_google_news_url

REGIONAL_FEEDS = [
    "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=en&gl=GB&ceid=GB:en",
    "https://news.google.com/rss?hl=en&gl=IN&ceid=IN:en",
    "https://news.google.com/rss?hl=en&gl=AU&ceid=AU:en",
    "https://news.google.com/rss?hl=en&gl=AE&ceid=AE:en",
]


class TopicAgent:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> dict:
        all_topics: list[dict] = []

        for feed_url in REGIONAL_FEEDS:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title = entry.title

                # Clean source suffix
                title = re.sub(r"\s+-\s+.*$", "", title)
                title = title.strip(" -–:")

                # Avoid weak topics
                if len(title.split()) < 4:
                    continue

                raw_link = entry.link
                decoded_link = decode_google_news_url(raw_link)
                final_link = decoded_link or raw_link

                all_topics.append(
                    {
                        "title": title,
                        "link": final_link,
                        "summary": getattr(entry, "summary", ""),
                    }
                )

        if not all_topics:
            return {
                "title": "Global geopolitical and economic developments",
                "link": "",
                "summary": "",
            }

        random.shuffle(all_topics)

        # ✅ Avoid duplicates already in DB
        for topic in all_topics:
            exists = (
                self.db.query(Article)
                .filter(Article.topic == topic["title"])
                .first()
            )
            if not exists:
                return topic

        # 🔁 Fallback if all topics already exist
        return random.choice(all_topics)
