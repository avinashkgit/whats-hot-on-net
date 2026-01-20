import os
import tempfile
import requests
import tweepy
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# ────────────────────────────────────────────────
#   Credentials from .env
# ────────────────────────────────────────────────
consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")


class XPosterAgent:
    """
    Twitter/X posting client
    - Uses v2 Client for tweet creation
    - Uses v1.1 API for media upload (still required for images)
    """

    def __init__(self):
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError(
                "❌ Missing one or more X API credentials in environment variables"
            )

        # ── v2 Client for creating tweets ──
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True,
        )

        # ── OAuth 1.0a handler (needed for v1.1 media upload) ──
        self.oauth1_user_handler = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

        # ── v1.1 API instance for media upload ──
        self.api_v1 = tweepy.API(self.oauth1_user_handler, wait_on_rate_limit=True)

    # ────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────
    def build_post(self, title: str, url: str) -> str:
        """
        Smart truncation to fit tweet limit with URL.
        NOTE: X wraps URLs to ~23 chars, but we keep simple logic.
        """
        url_space = len(url) + 5  # newline + margin
        max_title = 280 - url_space

        if len(title) > max_title - 3:
            title = title[: max_title - 3].rstrip() + "..."

        return f"{title}\n{url}"

    def upload_media(self, img_path: str) -> str:
        """
        Upload image using v1.1 endpoint via tweepy.API
        Returns media_id_string
        """
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        try:
            media = self.api_v1.media_upload(
                filename=img_path,
                media_category="tweet_image",
            )
            logger.info(f"✅ Media uploaded | media_id={media.media_id_string}")
            return media.media_id_string

        except tweepy.TweepyException as e:
            logger.error(f"❌ Media upload failed: {e}")

            # Extra debugging
            if hasattr(e, "response") and e.response is not None:
                try:
                    logger.error(f"API response: {e.response.text}")
                except Exception:
                    pass

            raise RuntimeError("Media upload failed - check X access tier/credentials")

    # ────────────────────────────────────────────────
    # Posting methods
    # ────────────────────────────────────────────────
    def post_article(self, title: str, slug: str) -> str | None:
        """Post article link without image"""
        try:
            url = f"https://hotonnet.com/article/{slug}"
            text = self.build_post(title, url)

            response = self.client.create_tweet(text=text)

            tweet_id = None
            if response and response.data and "id" in response.data:
                tweet_id = response.data["id"]

            logger.info(f"✅ Posted article | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post article")
            return None

    def post_article_with_image(self, title: str, slug: str, img_path: str) -> str | None:
        """Upload local image + create tweet"""
        try:
            url = f"https://hotonnet.com/article/{slug}"
            text = self.build_post(title, url)

            media_id = self.upload_media(img_path)

            response = self.client.create_tweet(
                text=text,
                media_ids=[media_id],
            )

            tweet_id = None
            if response and response.data and "id" in response.data:
                tweet_id = response.data["id"]

            logger.info(f"✅ Posted article with image | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post article with image")
            return None

    def post_article_with_image_url(self, title: str, slug: str, image_url: str) -> str | None:
        """
        Download remote image → upload to X → post → clean up temp file
        """
        temp_path = None

        try:
            logger.info(f"Downloading image: {image_url}")

            r = requests.get(image_url, timeout=30)
            r.raise_for_status()

            # Decide extension
            ext = ".jpg"
            content_type = (r.headers.get("content-type") or "").lower()
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(r.content)
                temp_path = tmp.name

            logger.info(f"✅ Image downloaded to temp: {temp_path} ({len(r.content)} bytes)")

            return self.post_article_with_image(title, slug, temp_path)

        except Exception:
            logger.exception("❌ Failed to process remote image")
            return None

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.info(f"🧹 Temp file removed: {temp_path}")
                except Exception:
                    pass
