from concurrent.futures import ThreadPoolExecutor, as_completed
from .extractor_agent import extract_article

def extract_articles_parallel(links, max_workers=5):
    articles = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(extract_article, item["link"]): item["link"]
            for item in links
        }

        for future in as_completed(future_map):
            url = future_map[future]
            try:
                articles.append(future.result())
            except Exception as e:
                print(f"[SKIPPED] {url}: {e}")

    return articles
