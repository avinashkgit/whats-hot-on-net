import html
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db.models import NotificationTokenCreate
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
from pathlib import Path

from app.db.database import SessionLocal
from app.db.repository import (
    get_categories,
    get_articles,
    get_article_by_slug,
    save_notification_token,
)

app = FastAPI(title="HotOnNet API")
INDEX_HTML = Path("dist/index.html")

# =========================
# CORS CONFIGURATION
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # local React dev
        "https://hotonnet.com",  # production frontend
        "https://www.hotonnet.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_social_bot(user_agent: str | None) -> bool:
    if not user_agent:
        return False

    ua = user_agent.lower()
    bots = [
        "facebookexternalhit",
        "twitterbot",
        "whatsapp",
        "telegrambot",
        "linkedinbot",
        "slackbot",
        "discordbot",
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


# =========================
# ROUTES REQUIRED BY UI
# =========================


# --- Topics (Navigation / Filters)
@app.get("/categories")
def topics(db: Session = Depends(get_db)):
    return get_categories(db)


# --- Articles list (Home + Pagination + Topic filter)
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


@app.get("/share/{slug}", response_class=HTMLResponse)
def article_share(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user_agent = request.headers.get("user-agent", "")
    article = get_article_by_slug(db, slug=slug)

    # Never 404 on share URLs
    if not article:
        return RedirectResponse(
            url=f"https://hotonnet.com/article/{slug}",
            status_code=302,
        )

    # BOT → OG HTML
    if is_social_bot(user_agent):
        title = html.escape(article.get("title", ""))

        raw_description = article.get("summary") or article.get("content") or ""
        description = html.escape(str(raw_description)[:160])

        image = article.get("imageUrl") or "https://www.hotonnet.com/icons/og.png"

        return HTMLResponse(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>

  <meta property="og:type" content="article" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url"
        content="https://whats-hot-on-net.onrender.com/share/{slug}" />
  <meta property="og:site_name" content="HotOnNet" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{image}" />

  <meta http-equiv="refresh"
        content="0; url=https://hotonnet.com/article/{slug}" />
</head>
<body></body>
</html>""",
            headers={"Cache-Control": "public, max-age=600"},
        )

    # HUMAN → redirect to frontend
    return RedirectResponse(
        url=f"https://hotonnet.com/article/{slug}",
        status_code=302,
    )


# --- Single article (Article page)
@app.get("/articles/{slug}")
def article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug=slug)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article not found")
    return article


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notifications/token")
def register_notification_token(
    payload: NotificationTokenCreate, db: Session = Depends(get_db)
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
