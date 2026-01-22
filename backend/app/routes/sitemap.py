from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

from app.db.database import SessionLocal
from app.db.repository import get_articles_for_sitemap

router = APIRouter()

# === CONFIG ===
SITE_URL = "https://hotonnet.com"
SITE_NAME = "Hot On Net"
LANG = "en"


# === DB DEPENDENCY ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === DATETIME HELPERS ===
def to_utc(dt_value):
    """
    Convert various datetime formats to timezone-aware UTC datetime.
    Supports:
    - datetime (naive or aware)
    - ISO string like '2026-01-21T10:20:00' or '2026-01-21T10:20:00Z'
    """
    if not dt_value:
        return None

    # If string -> parse ISO
    if isinstance(dt_value, str):
        try:
            dt_value = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
        except Exception:
            return None

    # If still not datetime -> ignore
    if not isinstance(dt_value, datetime):
        return None

    # If naive datetime -> assume UTC
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=timezone.utc)

    return dt_value.astimezone(timezone.utc)


# ======================================================
# MAIN SITEMAP (ALL ARTICLES)
# URL: /sitemap.xml
# ======================================================
@router.get("/sitemap.xml", include_in_schema=False)
def sitemap(db: Session = Depends(get_db)):
    page = 1
    limit = 50
    articles = []

    # Paginate through all articles
    while True:
        batch = get_articles_for_sitemap(db, page=page, limit=limit)
        if not batch:
            break
        articles.extend(batch)
        page += 1

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for article in articles:
        if not article.slug:
            continue

        created_at = to_utc(getattr(article, "created_at", None))
        published_at = to_utc(getattr(article, "published_at", None))

        # lastmod should be a valid datetime
        lastmod_dt = published_at or created_at
        if not lastmod_dt:
            continue

        xml.append(
            f"""
  <url>
    <loc>{SITE_URL}/article/{escape(str(article.slug))}</loc>
    <lastmod>{lastmod_dt.isoformat()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
        """.strip()
        )

    xml.append("</urlset>")

    return Response("\n".join(xml), media_type="application/xml")


# ======================================================
# GOOGLE NEWS SITEMAP (LAST 48 HOURS ONLY)
# URL: /news-sitemap.xml
# ======================================================
@router.get("/news-sitemap.xml", include_in_schema=False)
def news_sitemap(db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    page = 1
    limit = 50
    recent_articles = []

    # Paginate until articles are older than 48h
    while True:
        batch = get_articles_for_sitemap(db, page=page, limit=limit)
        if not batch:
            break

        batch_has_recent = False
        batch_all_old = True

        for article in batch:
            created_at = to_utc(getattr(article, "created_at", None))
            if not created_at:
                continue

            if created_at >= cutoff:
                recent_articles.append(article)
                batch_has_recent = True
                batch_all_old = False
            else:
                # This one is old
                pass

        # Stop early once we hit only old articles (and none recent)
        if batch_all_old and not batch_has_recent:
            break

        page += 1

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    )

    # Google News limit: max 1000 URLs
    for article in recent_articles[:1000]:
        if not article.slug or not article.title:
            continue

        created_at = to_utc(getattr(article, "created_at", None))
        if not created_at:
            continue

        xml.append(
            f"""
  <url>
    <loc>{SITE_URL}/article/{escape(str(article.slug))}</loc>
    <news:news>
      <news:publication>
        <news:name>{escape(SITE_NAME)}</news:name>
        <news:language>{escape(LANG)}</news:language>
      </news:publication>
      <news:publication_date>{created_at.isoformat()}</news:publication_date>
      <news:title>{escape(str(article.title))}</news:title>
    </news:news>
  </url>
        """.strip()
        )

    xml.append("</urlset>")

    return Response("\n".join(xml), media_type="application/xml")
