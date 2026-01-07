from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import SessionLocal
from app.db.repository import get_articles

app = FastAPI()

# =========================
# CORS CONFIGURATION
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # local React dev
        "https://whats-hot-on-net.onrender.com",  # deployed frontend (if any)
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
# Routes
# =========================
@app.get("/articles")
def articles(db=Depends(get_db)):
    return get_articles(db)
