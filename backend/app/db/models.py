from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Article(Base):
    __tablename__ = "articles"

    id = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text)
    category_id = Column(Text, ForeignKey("categories.id"), nullable=False)
    views = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category")
