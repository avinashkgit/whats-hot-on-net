import os
import tempfile
import requests
import tweepy
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")


class XPosterAgent:
    def __init__(self):
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("❌ Missing X API credentials in environment variables")

        # v2 client (tweet posting)
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        # v1.1 API (media upload)
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.api_v1 = tweepy.API(auth)

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
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")

            url = f"https://hotonnet.com/article/{slug}"
            post = self.build_post(title, url)

            media = self.api_v1.media_upload(img_path)
            media_id = media.media_id_string

            response = self.client.create_tweet(text=post, media_ids=[media_id])
            tweet_id = response.data["id"]

            logger.info(f"✅ Posted to X with image | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post on X with image")
            return None

    def post_article_with_image_url(self, title: str, slug: str, image_url: str):
        """
        Clean helper:
        - Downloads image_url to temp file
        - Uploads it to X
        - Deletes temp file automatically
        """
        temp_path = None

        try:
            r = requests.get(image_url, timeout=30)
            r.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                f.write(r.content)
                temp_path = f.name

            tweet_id = self.post_article_with_image(title, slug, temp_path)
            logger.info(f"✅ Posted to X with image URL | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post on X with image URL")
            return None

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
