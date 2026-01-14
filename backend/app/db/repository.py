from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from .models import Article, Topic
from slugify import slugify


# ======================================================
# GET TOPICS (for Navigation / Filters)
# ======================================================


def get_topics(db: Session):
    return db.query(Topic).order_by(Topic.name.asc()).all()


# ======================================================
# CREATE ARTICLE (Admin / CMS)
# ======================================================


def save_article(
    db: Session,
    *,
    title: str,
    slug: str,
    summary: str,
    content: str,
    topic_id: UUID,
    image_url: str | None = None,
) -> Article:
    article = Article(
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        topic_id=topic_id,
        image_url=image_url,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


# ======================================================
# GET ARTICLES (Paginated + Topic joined)
# ======================================================


def get_articles(db, *, topic_id=None, page=1, limit=10):
    query = db.query(Article).join(Topic).order_by(Article.created_at.desc())

    if topic_id:
        query = query.filter(Article.topic_id == topic_id)

    total = query.count()

    articles = query.offset((page - 1) * limit).limit(limit).all()

    items = [
        {
            "id": a.id,
            "title": a.title,
            "slug": a.slug,
            "summary": a.summary,
            "content": a.content,
            "imageUrl": a.image_url,
            "views": a.views,
            "createdAt": a.created_at,
            "topic": {
                "id": a.topic.id,
                "name": a.topic.name,
                "slug": a.topic.slug,
            },
        }
        for a in articles
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit,
    }


# ======================================================
# GET SINGLE ARTICLE BY SLUG (Article Page)
# ======================================================


def get_article_by_slug(
    db: Session,
    *,
    slug: str,
) -> Article | None:
    return db.query(Article).join(Topic).filter(Article.slug == slug).first()


# ======================================================
# GET OR CREATE TOPICS
# ======================================================


def get_or_create_topic(db, *, name: str) -> Topic:
    slug = slugify(name)

    topic = db.query(Topic).filter(Topic.slug == slug).first()

    if topic:
        return topic

    topic = Topic(
        name=name,
        slug=slug,
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return topic
