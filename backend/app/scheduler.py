from slugify import slugify
from dotenv import load_dotenv

from agents.topic_agent import TopicAgent
from agents.search_agent import search_news
from agents.extractor_pool import extract_articles_parallel
from agents.context_builder_agent import build_context, build_fallback_context
from agents.writer_agent import WriterAgent
from agents.image_agent import ImageAgent
from agents.x_poster_agent import XPosterAgent

from app.db.database import SessionLocal
from app.db.repository import save_article, get_or_create_category

load_dotenv()


def run():
    db = SessionLocal()

    try:
        # =========================
        # 1️⃣ Pick TOPIC (idea)
        # =========================
        topic_data = TopicAgent(db).run()

        topic = topic_data.get("title")
        if not topic:
            raise RuntimeError(f"Invalid topic_data returned: {topic_data}")

        print("Topic idea:", topic_data)

        # =========================
        # 2️⃣ Discover links
        # =========================
        links = search_news(topic, limit=5)
        if not links:
            raise RuntimeError("No news links found")

        # =========================
        # 3️⃣ Extract context
        # =========================
        articles = extract_articles_parallel(links, max_workers=5)

        if articles:
            context = build_context(articles)
        else:
            print("⚠️ No full articles extracted. Falling back to headlines.")
            context = build_fallback_context(links)

        # =========================
        # 4️⃣ Write article + CATEGORY
        # =========================
        article = WriterAgent().run(topic, context)

        title = article["title"]
        content = article["body"]
        summary = article.get("summary") or content[:200]
        category_name = article["category"]
        slug = slugify(title)

        # =========================
        # 5️⃣ Get or create CATEGORY
        # =========================
        category = get_or_create_category(db, name=category_name)

        # =========================
        # 6️⃣ Generate image
        # =========================
        image_url = ImageAgent().run(topic)

        # =========================
        # 7️⃣ Save article
        # =========================
        save_article(
            db=db,
            topic=topic,
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            category_id=category.id,
            image_url=image_url,
        )

        print(f"✅ Article saved | topic='{topic}' | category='{category_name}'")

        # =========================
        # 8️⃣ Download image and post to X
        # =========================
        tweet_id = XPosterAgent().post_article_with_image_url(title, slug, image_url)
        print("✅ Tweet posted | tweet_id =", tweet_id)

    finally:
        db.close()


if __name__ == "__main__":
    run()
