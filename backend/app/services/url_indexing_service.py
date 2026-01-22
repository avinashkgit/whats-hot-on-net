import os
import logging
import requests
from typing import Optional

# -------------------------------------------------
# LOGGING CONFIG
# -------------------------------------------------
logger = logging.getLogger("indexing")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------------------------------
# BING CONFIG
# -------------------------------------------------
BING_API_KEY = os.getenv("BING_API_KEY")
BING_ENDPOINT = "https://ssl.bing.com/webmasters/api.svc/json/SubmitUrl"
SITE_URL = "https://hotonnet.com"


# -------------------------------------------------
# BING URL SUBMISSION
# -------------------------------------------------
def submit_url_to_bing(url: str) -> bool:
    """
    Submit a URL to Bing for instant indexing.
    Returns True if successful, False otherwise.
    """

    if not BING_API_KEY:
        logger.error("BING_API_KEY is missing in environment variables")
        return False

    payload = {
        "siteUrl": SITE_URL,
        "url": url,
        "key": BING_API_KEY,
    }

    headers = {"Content-Type": "application/json"}

    try:
        logger.info(f"Submitting URL to Bing: {url}")

        response = requests.post(
            BING_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            logger.info("Bing indexing successful")
            return True

        logger.error(
            "Bing indexing failed | Status: %s | Response: %s",
            response.status_code,
            response.text,
        )
        return False

    except requests.exceptions.Timeout:
        logger.error("Bing indexing request timed out")
        return False

    except requests.exceptions.RequestException as e:
        logger.exception("Bing indexing request failed")
        return False


# -------------------------------------------------
# GOOGLE SITEMAP PING
# -------------------------------------------------
def ping_google_sitemap(sitemap_url: Optional[str] = None) -> bool:
    """
    Ping Google to notify sitemap update.
    This does NOT guarantee indexing.
    """

    sitemap_url = sitemap_url or f"{SITE_URL}/news-sitemap.xml"
    ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"

    try:
        logger.info(f"Pinging Google sitemap: {sitemap_url}")

        response = requests.get(ping_url, timeout=5)

        if response.status_code == 200:
            logger.info("Google sitemap ping successful")
            return True

        logger.warning(
            "Google sitemap ping failed | Status: %s",
            response.status_code,
        )
        return False

    except requests.exceptions.RequestException:
        logger.exception("Google sitemap ping failed")
        return False
