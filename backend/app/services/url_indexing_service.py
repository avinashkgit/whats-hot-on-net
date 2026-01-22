import os
import requests
from typing import Optional

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
        print("❌ BING_API_KEY is missing in environment variables")
        return False

    payload = {
        "siteUrl": SITE_URL,
        "url": url,
        "key": BING_API_KEY,
    }

    headers = {"Content-Type": "application/json"}

    try:
        print(f"📌 Submitting URL to Bing: {url}")

        response = requests.post(
            BING_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            print("✅ Bing indexing successful")
            return True

        print(
            f"❌ Bing indexing failed | Status: {response.status_code} | Response: {response.text}"
        )
        return False

    except requests.exceptions.Timeout:
        print("⏳ Bing indexing request timed out")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Bing indexing request failed: {e}")
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
        print(f"📡 Pinging Google sitemap: {sitemap_url}")

        response = requests.get(ping_url, timeout=5)

        if response.status_code == 200:
            print("✅ Google sitemap ping successful")
            return True

        print(f"⚠️ Google sitemap ping failed | Status: {response.status_code}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Google sitemap ping failed: {e}")
        return False
