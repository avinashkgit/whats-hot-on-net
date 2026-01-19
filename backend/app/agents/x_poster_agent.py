import os
import tempfile
import requests
import tweepy
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# ────────────────────────────────────────────────
#   Credentials from .env (same as before)
# ────────────────────────────────────────────────
consumer_key = os.getenv("X_API_KEY")
consumer_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")


class XPosterAgent:
    """
    Twitter/X posting client - Fixed for Tweepy 4.10+ (Jan 2026)
    Uses manual OAuth1 handler for media upload + Client for v2 tweet creation
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

        # ── Manual OAuth 1.0a User Handler (REQUIRED for v1.1 media upload) ──
        self.oauth1_user_handler = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

        # ── v1.1 API instance just for media upload ──
        self.api_v1 = tweepy.API(self.oauth1_user_handler, wait_on_rate_limit=True)

    def build_post(self, title: str, url: str) -> str:
        """Smart truncation to fit tweet limit with URL"""
        url_space = len(url) + 5  # newline + margin
        max_title = 280 - url_space

        if len(title) > max_title - 3:
            title = title[: max_title - 3].rstrip() + "..."

        return f"{title}\n{url}"

    def upload_media(self, img_path: str) -> str:
        """
        Upload image using v1.1 endpoint via tweepy.API (still the most reliable path)
        Returns media_id_string
        """
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")

        try:
            media = self.api_v1.media_upload(
                filename=img_path,
                media_category="tweet_image",  # recommended for images
            )
            logger.debug(f"Media uploaded - ID: {media.media_id_string}")
            return media.media_id_string

        except tweepy.TweepyException as e:
            logger.error(f"Media upload failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"API response: {e.response.text}")
            raise RuntimeError(
                "Media upload failed - most likely needs Pro+ tier or valid credentials"
            )

    def post_article(self, title: str, slug: str) -> str | None:
        """Post article link without image"""
        try:
            url = f"https://hotonnet.com/article/{slug}"
            text = self.build_post(title, url)

            response = self.client.create_tweet(text=text)
            tweet_id = response.data["id"]

            logger.info(f"Posted article | tweet_id={tweet_id}")
            return tweet_id

        except Exception:
            logger.exception("❌ Failed to post article")
            return None

    def post_article_with_image_url(
        self, title: str, slug: str, image_url: str
    ) -> str | None:
        """
        Download remote image → upload to X → post → clean up temp file
        """
        temp_path = None
        try:
            r = requests.get(image_url, timeout=20)
            r.raise_for_status()

            ext = ".jpg"
            content_type = r.headers.get("content-type", "")
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(r.content)
                temp_path = tmp.name

            return self.post_article_with_image(title, slug, temp_path)

        except Exception:
            logger.exception("❌ Failed to process remote image")
            return None

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
