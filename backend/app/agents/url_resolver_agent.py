import requests

def resolve_google_news_url(url, timeout=10):
    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        return response.url
    except Exception:
        return None
