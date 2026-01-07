from datetime import datetime
from sqlalchemy.orm import Session
from .models import Article

def save_article(db: Session, topic, title, body, image_url):
    article = Article(
        topic=topic,
        title=title,
        body=body,
        image_url=image_url,
        published_at=datetime.utcnow()
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_articles(db: Session, limit=10):
    return (
        db.query(Article)
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
