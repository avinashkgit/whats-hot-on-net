from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from .models import Article, Category, NotificationToken
from slugify import slugify
from sqlalchemy import func


# ======================================================
# GET TOPICS (for Navigation / Filters)
# ======================================================


def get_categories(db: Session):
    return db.query(Category).order_by(Category.name.asc()).all()


# ======================================================
# CREATE ARTICLE (Admin / CMS)
# ======================================================


def save_article(
    db: Session,
    *,
    topic: str,
    title: str,
    slug: str,
    summary: str,
    content: str,
    category_id,
    image_url: str | None = None,
    image_model: str | None = None,
):
    article = Article(
        topic=topic,
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        category_id=category_id,
        image_url=image_url,
        image_model=image_model,
    )

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# ======================================================
# GET ARTICLES (Paginated + Topic joined)
# ======================================================


def get_articles(
    db: Session,
    *,
    category: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    query = db.query(Article).join(Category)

    # ✅ FILTER BY CATEGORY SLUG
    if category:
        query = query.filter(Category.slug == category)

    query = query.order_by(Article.created_at.desc())

    total = query.count()
    articles = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "items": [
            {
                "id": a.id,
                "topic": a.topic,
                "title": a.title,
                "slug": a.slug,
                "summary": a.summary,
                "content": a.content,
                "imageUrl": a.image_url,
                "views": a.views,
                "createdAt": a.created_at,
                "category": {
                    "id": a.category.id,
                    "name": a.category.name,
                    "slug": a.category.slug,
                },
            }
            for a in articles
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit,
    }


# ======================================================
# GET SINGLE ARTICLE BY SLUG (Article Page)
# ======================================================


def get_article_by_slug(db: Session, *, slug: str):
    article = db.query(Article).join(Category).filter(Article.slug == slug).first()

    if not article:
        return None

    article.views += 1
    db.commit()
    db.refresh(article)

    return {
        "id": article.id,
        "topic": article.topic,
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "content": article.content,
        "imageUrl": article.image_url,
        "views": article.views,
        "createdAt": article.created_at,
        "category": {
            "id": article.category.id,
            "name": article.category.name,
            "slug": article.category.slug,
        },
    }


# ======================================================
# GET OR CREATE TOPICS
# ======================================================


def get_or_create_category(db: Session, *, name: str) -> Category:
    slug = slugify(name)

    category = db.query(Category).filter(Category.slug == slug).first()
    if category:
        return category

    category = Category(
        name=name,
        slug=slug,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def topic_exists(db, *, topic: str) -> bool:
    return db.query(Article.id).filter(Article.topic == topic).first() is not None


def save_notification_token(db: Session, token: str, platform: str, device_id=None, browser=None):
    existing = db.query(NotificationToken).filter(NotificationToken.token == token).first()

    if existing:
        existing.is_active = True
        existing.last_seen_at = func.now()
        db.commit()
        db.refresh(existing)
        return existing

    new_token = NotificationToken(
        token=token,
        platform=platform,
        device_id=device_id,
        browser=browser,
        is_active=True,
        last_seen_at=func.now(),
    )

    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token

def get_active_notification_tokens(db):
    rows = (
        db.query(NotificationToken.token)
        .filter(NotificationToken.is_active == True)
        .all()
    )
    return [r[0] for r in rows]