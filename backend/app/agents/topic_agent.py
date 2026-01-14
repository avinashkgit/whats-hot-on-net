import feedparser
import random
import re
from sqlalchemy.orm import Session

from app.db.models import Article

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

    def run(self) -> str:
        all_topics: list[str] = []

        for feed_url in REGIONAL_FEEDS:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title = entry.title

                # Clean source suffix
                title = re.sub(r"\s+-\s+.*$", "", title)
                title = title.strip(" -–:")

                # Avoid very weak topics
                if len(title.split()) < 4:
                    continue

                all_topics.append(title)

        if not all_topics:
            return "Global geopolitical and economic developments"

        random.shuffle(all_topics)

        # ✅ Avoid duplicates already in DB
        for topic in all_topics:
            exists = (
                self.db.query(Article)
                .filter(Article.topic == topic)
                .first()
            )
            if not exists:
                return topic

        # Fallback if everything already exists
        return random.choice(all_topics)
