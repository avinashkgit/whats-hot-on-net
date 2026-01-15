import os
import tweepy
import logging

logger = logging.getLogger(__name__)


class XPosterAgent:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        )

    def build_post(self, title: str, url: str) -> str:
        """
        Rules:
        - Post 'title + url' if <= 280 chars
        - Else post ONLY url
        """
        tweet = f"{title}\n{url}"

        if len(tweet) <= 280:
            return tweet

        return url

    def post_article(self, title: str, slug: str):
        try:
            url = f"https://hotonnet.com/article/{slug}"
            tweet = self.build_post(title, url)
            response = self.client.create_tweet(text=tweet)
            logger.info(f"✅ Posted to X | tweet_id={response.data['id']}")
            return response.data["id"]

        except Exception as e:
            logger.error("❌ Failed to post on X", exc_info=e)
            return None
