from agents.topic_agent import TopicAgent
from agents.search_agent import search_news
from agents.extractor_pool import extract_articles_parallel
from agents.context_builder_agent import build_context, build_fallback_context
from agents.writer_agent import WriterAgent
from agents.image_agent import ImageAgent

from app.db.database import SessionLocal
from app.db.repository import save_article


def run():
    # 1️⃣ Pick topic
    topic = TopicAgent().run()
    print("Topic:", topic)

    # 2️⃣ Discover links
    links = search_news(topic, limit=5)
    if not links:
        raise RuntimeError("No news links found")

    # 3️⃣ Parallel extraction
    articles = extract_articles_parallel(links, max_workers=5)
    if articles:
        context = build_context(articles)
    else:
        context = build_fallback_context(links)

    if not articles:
        print("⚠️ No full articles extracted. Falling back to headline-based context.")

    # 4️⃣ Build grounded context
    context = build_context(articles)

    # 5️⃣ Write article
    article = WriterAgent().run(topic, context)

    # 6️⃣ Generate image
    image_url = ImageAgent().run(topic)

    # 7️⃣ Persist
    db = SessionLocal()
    save_article(
        db=db,
        topic=topic,
        title=article["title"],
        body=article["body"],
        image_url=image_url,
    )
    db.close()


if __name__ == "__main__":
    run()
