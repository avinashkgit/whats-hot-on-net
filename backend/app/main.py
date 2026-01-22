import html
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.routes import sitemap

from app.db.database import SessionLocal
from app.db.models import NotificationTokenCreate
from app.db.repository import (
    get_categories,
    get_articles,
    get_article_by_slug,
    save_notification_token,
)

app = FastAPI(title="HotOnNet API")

# =========================
# FRONTEND BUILD (OPTIONAL)
# =========================
INDEX_HTML = Path("dist/index.html")

# =========================
# DOMAIN CONFIG
# =========================
PUBLIC_SITE_URL = "https://hotonnet.com"  # frontend (Hostinger)
PUBLIC_API_URL = "https://api.hotonnet.com"  # backend (Render)
DEFAULT_OG_IMAGE = f"{PUBLIC_SITE_URL}/icons/og.png"

# =========================
# CORS CONFIGURATION
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://hotonnet.com",
        "https://www.hotonnet.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sitemap.router)


# =========================
# BOT DETECTION
# =========================
def is_social_bot(user_agent: str | None) -> bool:
    if not user_agent:
        return False

    ua = user_agent.lower()
    bots = [
        "facebookexternalhit",
        "facebot",
        "twitterbot",
        "whatsapp",
        "telegrambot",
        "linkedinbot",
        "slackbot",
        "discordbot",
        "embedly",
        "pinterest",
        "skypeuripreview",
    ]
    return any(bot in ua for bot in bots)


def is_search_engine_bot(user_agent: str | None) -> bool:
    if not user_agent:
        return False

    ua = user_agent.lower()
    bots = [
        "googlebot",
        "bingbot",
        "duckduckbot",
        "yandexbot",
        "baiduspider",
    ]
    return any(bot in ua for bot in bots)


# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/categories")
def topics(db: Session = Depends(get_db)):
    return get_categories(db)


@app.get("/articles")
def articles(
    category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_articles(
        db,
        category=category,
        page=page,
        limit=limit,
    )

@app.get("/article/{slug}")
def article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug=slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.post("/notifications/token")
def register_notification_token(
    payload: NotificationTokenCreate,
    db: Session = Depends(get_db),
):
    token_row = save_notification_token(
        db=db,
        token=payload.token,
        platform=payload.platform,
        device_id=payload.device_id,
        browser=payload.browser,
    )

    return {
        "message": "Token saved",
        "id": str(token_row.id),
    }


# =========================
# SHARE URL (OG PREVIEW)
# =========================
@app.get("/share/{slug}", response_class=HTMLResponse)
def article_share(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user_agent = request.headers.get("user-agent", "")
    article = get_article_by_slug(db, slug=slug)

    frontend_article_url = f"{PUBLIC_SITE_URL}/article/{slug}"

    # /share exists on backend → must use API domain
    share_url = f"{PUBLIC_API_URL}/share/{slug}"

    if not article:
        return RedirectResponse(url=frontend_article_url, status_code=302)

    # Social bots → OG HTML
    if is_social_bot(user_agent):
        title = html.escape(str(article.get("title") or "HotOnNet"))

        raw_description = article.get("summary") or article.get("content") or ""
        raw_description = str(raw_description).strip()
        description = (
            html.escape(raw_description[:160])
            if raw_description
            else "Read the latest story on HotOnNet."
        )

        image = (
            article.get("imageUrl")
            or article.get("image_url")
            or article.get("image")
            or DEFAULT_OG_IMAGE
        )

        if isinstance(image, str) and image.startswith("/"):
            image = f"{PUBLIC_SITE_URL}{image}"

        return HTMLResponse(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>

  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="HotOnNet" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url" content="{share_url}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{image}" />
</head>
<body></body>
</html>""",
            headers={"Cache-Control": "public, max-age=600"},
        )

    # Search engines → serve SPA HTML if exists
    if is_search_engine_bot(user_agent):
        if INDEX_HTML.exists():
            return HTMLResponse(
                INDEX_HTML.read_text(encoding="utf-8"),
                headers={"Cache-Control": "public, max-age=300"},
            )

        return RedirectResponse(url=frontend_article_url, status_code=302)

    # Humans → redirect to frontend
    return RedirectResponse(url=frontend_article_url, status_code=302)


# =========================
# HEALTH
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}
