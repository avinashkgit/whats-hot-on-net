from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.db.repository import get_articles

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
        batch = get_articles(db, page=page, limit=limit)
        if not batch:
            break
        articles.extend(batch)
        page += 1

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for article in articles:
        if not article.slug or not article.created_at:
            continue

        xml.append(f"""
  <url>
    <loc>{SITE_URL}/article/{article.slug}</loc>
    <lastmod>{article.published_at.isoformat()}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
        """)

    xml.append("</urlset>")

    return Response(
        "\n".join(xml),
        media_type="application/xml"
    )

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
        batch = get_articles(db, page=page, limit=limit)
        if not batch:
            break

        for article in batch:
            if article.created_at and article.created_at >= cutoff:
                recent_articles.append(article)

        # Stop early once we hit only old articles
        if all(
            article.created_at and article.created_at < cutoff
            for article in batch
        ):
            break

        page += 1

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    )

    # Google News limit: max 1000 URLs
    for article in recent_articles[:1000]:
        if not article.slug or not article.title or not article.created_at:
            continue

        xml.append(f"""
  <url>
    <loc>{SITE_URL}/article/{article.slug}</loc>
    <news:news>
      <news:publication>
        <news:name>{SITE_NAME}</news:name>
        <news:language>{LANG}</news:language>
      </news:publication>
      <news:publication_date>{article.created_at.isoformat()}</news:publication_date>
      <news:title>{article.title}</news:title>
    </news:news>
  </url>
        """)

    xml.append("</urlset>")

    return Response(
        "\n".join(xml),
        media_type="application/xml"
    )
