import os
import tweepy
import logging

logger = logging.getLogger(__name__)

consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    raise ValueError("❌ Missing X API credentials in environment variables")

# v1.1 client only for media upload
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api_v1 = tweepy.API(auth)


class XPosterAgent:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

    def build_post(self, title: str, url: str) -> str:
        tweet = f"{title}\n{url}"
        return tweet if len(tweet) <= 280 else url

    def post_article(self, title: str, slug: str):
        try:
            url = f"https://hotonnet.com/article/{slug}"
            post = self.build_post(title, url)

            response = self.client.create_tweet(text=post)
            tweet_id = response.data["id"]

            logger.info(f"✅ Posted to X | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post on X")
            return None

    def post_article_with_image(self, title: str, slug: str, img_path: str):
        try:
            url = f"https://hotonnet.com/article/{slug}"
            post = self.build_post(title, url)

            # Upload image (v1.1)
            media = api_v1.media_upload(img_path)
            media_id = media.media_id_string

            # Post tweet with image (v2)
            response = self.client.create_tweet(text=post, media_ids=[media_id])
            tweet_id = response.data["id"]

            logger.info(f"✅ Posted to X with image | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post on X with image")
            return None
