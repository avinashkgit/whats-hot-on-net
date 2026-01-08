from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from app.db.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    topic = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    image_url = Column(Text)
    published_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
