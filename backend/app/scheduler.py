from slugify import slugify
from dotenv import load_dotenv

from agents.topic_agent import TopicAgent
from agents.search_agent import search_news
from agents.extractor_pool import extract_articles_parallel
from agents.context_builder_agent import build_context, build_fallback_context
from agents.writer_agent import WriterAgent
from agents.image_prompt_agent import ImagePromptAgent
from agents.image_agent import ImageAgent
from agents.x_poster_agent import XPosterAgent

from app.app.services.fcm_service import send_push_to_tokens
from app.db.database import SessionLocal
from app.db.repository import (
    get_active_notification_tokens,
    save_article,
    get_or_create_category,
)

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
        # 6️⃣ Generate scenic image prompt (NEW)
        # =========================
        prompt_data = ImagePromptAgent().run(
            topic=summary,  # use rewritten title for best results
            category=category_name,
        )

        final_prompt = prompt_data["prompt"]
        negative_prompt = prompt_data["negative_prompt"]

        # =========================
        # 7️⃣ Generate image using prompt (UPDATED)
        # =========================
        image_url, model = ImageAgent().run(
            prompt=prompt_data["prompt"],
            negative_prompt=prompt_data["negative_prompt"],
            topic=topic,
            humans_allowed=prompt_data["humans_allowed"],
        )

        # =========================
        # 8️⃣ Save article
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
            image_model=model,
        )

        print(f"✅ Article saved | topic='{topic}' | category='{category_name}'")

        # =========================
        # 9️⃣ Post to X
        # =========================
        # tweet_id = XPosterAgent().post_article(summary, slug)
        tweet_id = XPosterAgent().post_article_with_image_url(summary, slug, image_url)
        print("✅ Tweet posted | tweet_id =", tweet_id)

        tokens = get_active_notification_tokens(db)

        if not tokens:
            print("⚠️ No active notification tokens found. Skipping push.")
            return

        article_url = f"https://hotonnet.com/article/{slug}"

        # ✅ Keep summary short (FCM data size safety)
        short_summary = summary.strip()
        if len(short_summary) > 120:
            short_summary = short_summary[:110] + "..."

        print(
            "PUSH DEBUG:",
            {
                "title": title,
                "body": short_summary,
                "url": article_url,
                "image_url": image_url,
                "tokens": len(tokens),
            },
        )

        push_resp = send_push_to_tokens(
            tokens=tokens,
            title=title,  # ✅ article title
            body=short_summary,  # ✅ short summary
            image_url=image_url,
            url=article_url,
        )

        print("✅ Push sent:", push_resp)

    finally:
        db.close()


if __name__ == "__main__":
    run()
