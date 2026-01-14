from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from .models import Article, Category
from slugify import slugify


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
    title: str,
    slug: str,
    summary: str,
    content: str,
    category_id,
    image_url: str | None = None,
):
    article = Article(
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        category_id=category_id,
        image_url=image_url,
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
    category_id: UUID | None = None,
    page: int = 1,
    limit: int = 10,
):
    query = (
        db.query(Article)
        .join(Category)
        .order_by(Article.created_at.desc())
    )

    if category_id:
        query = query.filter(Article.category_id == category_id)

    total = query.count()

    articles = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "slug": a.slug,
                "summary": a.summary,
                "content": a.content,
                "imageUrl": a.image_url,
                "views": a.views,
                "createdAt": a.created_at,
                # ✅ UI NOW EXPECTS `category`
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


def get_article_by_slug(
    db: Session,
    *,
    slug: str,
) -> Article | None:
    return db.query(Article).join(Category).filter(Article.slug == slug).first()


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
