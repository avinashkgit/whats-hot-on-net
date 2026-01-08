from newspaper import Article
from urllib.parse import urlparse

BLOCKED_DOMAINS = (
    "nytimes.com",
    "wsj.com",
    "bloomberg.com",
    "axios.com",
    "forbes.com"
)


def extract_article(url, timeout=10):
    domain = urlparse(url).netloc

    if any(d in domain for d in BLOCKED_DOMAINS):
        raise ValueError(f"Blocked domain: {domain}")

    article = Article(url, request_timeout=timeout)
    article.download()
    article.parse()

    if not article.text.strip():
        raise ValueError("Empty article")

    return {
        "url": url,
        "title": article.title,
        "text": article.text,
        "authors": article.authors,
        "publish_date": article.publish_date,
    }
