from slugify import slugify

from agents.topic_agent import TopicAgent
from agents.search_agent import search_news
from agents.extractor_pool import extract_articles_parallel
from agents.context_builder_agent import build_context, build_fallback_context
from agents.writer_agent import WriterAgent
from agents.image_agent import ImageAgent

from app.db.database import SessionLocal
from app.db.repository import save_article, get_or_create_topic


def run():
    db = SessionLocal()

    try:
        # =========================
        # 1️⃣ Pick topic (AI)
        # =========================
        topic_name = TopicAgent().run()
        print("Topic:", topic_name)

        # =========================
        # 2️⃣ Get or create topic
        # =========================
        topic = get_or_create_topic(db, name=topic_name)
        topic_id = topic.id

        # =========================
        # 3️⃣ Discover links
        # =========================
        links = search_news(topic_name, limit=5)
        if not links:
            raise RuntimeError("No news links found")

        # =========================
        # 4️⃣ Extract context
        # =========================
        articles = extract_articles_parallel(links, max_workers=5)

        if articles:
            context = build_context(articles)
        else:
            print("⚠️ No full articles extracted. Falling back to headlines.")
            context = build_fallback_context(links)

        # =========================
        # 5️⃣ Write article
        # =========================
        article = WriterAgent().run(topic_name, context)

        title = article["title"]
        content = article["body"]
        summary = article.get("summary") or content[:200]
        slug = slugify(title)

        # =========================
        # 6️⃣ Generate image
        # =========================
        image_url = ImageAgent().run(topic_name)

        # =========================
        # 7️⃣ Save article
        # =========================
        save_article(
            db=db,
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            topic_id=topic_id,
            image_url=image_url,
        )

        print("✅ Article saved successfully")

    finally:
        db.close()


if __name__ == "__main__":
    run()
