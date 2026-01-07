from fastapi import FastAPI, Depends
from app.db.database import SessionLocal
from app.db.repository import get_articles

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/articles")
def articles(db=Depends(get_db)):
    return get_articles(db)
