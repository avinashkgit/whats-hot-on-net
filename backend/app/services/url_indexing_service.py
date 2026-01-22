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
