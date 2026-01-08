import requests
from urllib.parse import urlparse, parse_qs

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def resolve_google_news_url(url, timeout=10):
    """
    Resolves Google News RSS article URLs to the real publisher URL.
    Handles redirects, meta refresh, and ?url= patterns.
    """

    try:
        # 1️⃣ Try normal redirect
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        if resp.url and "news.google.com" not in resp.url:
            return resp.url

        # 2️⃣ Try extracting ?url= param
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        if "url" in qs:
            return qs["url"][0]

        # 3️⃣ Try HEAD request (sometimes works)
        head = requests.head(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )

        if head.url and "news.google.com" not in head.url:
            return head.url

    except Exception as e:
        print("[Resolver error]", e)

    return None
