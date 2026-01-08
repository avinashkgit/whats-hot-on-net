import feedparser
import random
import re

GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en&gl=US&ceid=US:en"

# Sources that work well with newspaper3k
ALLOWED_SOURCES = (
    "Reuters",
    "BBC",
    "AP News",
    "The Guardian",
    "Al Jazeera",
    "Financial Times",
    "The New York Times",
    "Politico",
    "Axios",
)

# Topics that frequently fail extraction or are low-value for global news
DISALLOWED_KEYWORDS = (
    "Game Recap",
    "Preview",
    "vs.",
    "ESPN",
    "Netflix",
    "Episode",
    "Season",
    "Trailer",
    "Box Office",
    "Awards",
    "Minecraft",
    "Dynamite",
    "Wrestling",
    "NBA",
    "NFL",
    "NHL",
    "MLB",
)


class TopicAgent:
    def run(self) -> str:
        feed = feedparser.parse(GOOGLE_NEWS_RSS)
        print("Fetched", len(feed.entries), "news entries")

        if not feed.entries:
            return "Global geopolitical and economic developments"

        topics = []

        for entry in feed.entries:
            raw_title = entry.title
            print("Entry Title:", raw_title)

            # Ensure source is extractable
            if not any(src in raw_title for src in ALLOWED_SOURCES):
                continue

            # Remove source suffix (e.g. " - BBC News")
            title = re.sub(r"\s+-\s+.*$", "", raw_title)

            # Remove trailing punctuation
            title = title.strip(" -–:")

            # Filter disallowed categories
            if any(word in title for word in DISALLOWED_KEYWORDS):
                continue

            # Avoid very short / weak topics
            if len(title.split()) < 4:
                continue

            topics.append(title)

        if not topics:
            print("⚠️ No strong extractable topics found, using fallback")
            return "Global geopolitical and economic developments"

        return random.choice(topics)
