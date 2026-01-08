from newspaper import Article
from .url_resolver_agent import resolve_google_news_url

def extract_article(url, timeout=10):
    resolved_url = resolve_google_news_url(url)

    if not resolved_url:
        raise ValueError("Could not resolve article URL")

    article = Article(resolved_url, request_timeout=timeout)
    article.download()
    article.parse()

    if not article.text.strip():
        raise ValueError("Empty article")

    return {
        "url": resolved_url,
        "title": article.title,
        "text": article.text,
        "authors": article.authors,
        "publish_date": article.publish_date,
    }
