from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import SessionLocal
from app.db.repository import (
    get_categories,
    get_articles,
    get_article_by_slug,
)

app = FastAPI(title="HotOnNet API")

# =========================
# CORS CONFIGURATION
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # local React dev
        "https://hotonnet.com",    # production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# --- Single article (Article page)
@app.get("/articles/{slug}")
def article(slug: str, db: Session = Depends(get_db)):
    article = get_article_by_slug(db, slug=slug)
    if not article:
        return {"message": "Article not found"}
    return article
