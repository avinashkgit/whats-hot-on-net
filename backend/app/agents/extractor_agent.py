from newspaper import Article

def extract_article(url, timeout=10):
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
