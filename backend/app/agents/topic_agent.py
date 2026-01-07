import feedparser
import random
import re

GOOGLE_NEWS_RSS = "https://news.google.com/rss" "?hl=en&gl=US&ceid=US:en"


class TopicAgent:
    def run(self) -> str:
        feed = feedparser.parse(GOOGLE_NEWS_RSS)

        if not feed.entries:
            return "Global technology and economic trends"

        topics = []

        for entry in feed.entries[:20]:  # top 20 headlines
            title = entry.title

            # Remove source name (e.g. " - BBC News")
            title = re.sub(r"\s+-\s+.*$", "", title)

            # Remove trailing punctuation
            title = title.strip(" -–:")

            # Filter weak / clickbait titles
            if len(title.split()) >= 4:
                topics.append(title)

        if not topics:
            return "Global geopolitical and technology developments"

        return random.choice(topics)
