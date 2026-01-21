from fastapi.responses import HTMLResponse
from app.db.models import NotificationTokenCreate
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import SessionLocal
from app.db.repository import (
    get_categories,
    get_articles,
    get_article_by_slug,
    save_notification_token,
)

app = FastAPI(title="HotOnNet API")

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
        "googlebot",
        "bingbot",
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


@app.get("/article/{slug}", response_class=HTMLResponse)
def article(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    article = get_article_by_slug(db, slug)

    if not article:
        return HTMLResponse("Not found", status_code=404)

    user_agent = request.headers.get("user-agent")

    # ✅ BOT → serve OG HTML
    if is_social_bot(user_agent):
        image = article.imageUrl or "https://www.hotonnet.com/icons/og.png"
        description = article.summary or article.content[:160]

        return HTMLResponse(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{article.title}</title>

  <meta property="og:type" content="article" />
  <meta property="og:title" content="{article.title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url" content="https://www.hotonnet.com/article/{slug}" />
  <meta property="og:site_name" content="HotOnNet" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{article.title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{image}" />

  <!-- Redirect real browsers -->
  <meta http-equiv="refresh" content="0; url=/article/{slug}" />
</head>
<body></body>
</html>""",
            headers={
                "Cache-Control": "public, max-age=600",
            },
        )


# --- Single article (Article page)
# @app.get("/articles/{slug}")
# def article(slug: str, db: Session = Depends(get_db)):
#     article = get_article_by_slug(db, slug=slug)
#     if not article:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Article not found"
#         )
#     return article


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
