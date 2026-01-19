import os
import tempfile
import requests
from requests_oauthlib import OAuth1
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

        # v2 client for tweet posting
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        # OAuth1 for media upload (v2 supports OAuth1 User Context)
        self.auth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )

    def build_post(self, title: str, url: str) -> str:
        max_title_len = 280 - len(url) - 5  # Margin for newline and ellipsis
        if len(title) > max_title_len:
            title = title[:max_title_len - 3] + "..."
        return f"{title}\n{url}"

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

    def upload_media_v2(self, img_path: str) -> str:
        """
        Uploads media using v2 API endpoint with one-shot upload (suitable for images < 5MB).
        For larger files or videos, implement chunked upload separately.
        """
        media_url = "https://upload.twitter.com/2/media/upload"
        try:
            with open(img_path, "rb") as img_file:
                files = {"media": img_file}
                r = requests.post(media_url, auth=self.auth, files=files, timeout=30)
                r.raise_for_status()
                media_id = r.json()["media_id_string"]
                return media_id
        except Exception:
            logger.exception("❌ Failed to upload media to X v2")
            raise

    def post_article_with_image(self, title: str, slug: str, img_path: str):
        try:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")

            url = f"https://hotonnet.com/article/{slug}"
            post = self.build_post(title, url)

            media_id = self.upload_media_v2(img_path)

            response = self.client.create_tweet(text=post, media_ids=[media_id])
            tweet_id = response.data["id"]

            logger.info(f"✅ Posted to X with image | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post on X with image")
            return None

    def post_article_with_image_url(self, title: str, slug: str, image_url: str):
        """
        Downloads image_url to temp file, uploads to X v2, deletes temp file.
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