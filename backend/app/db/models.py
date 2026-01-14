from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text


class Category(Base):
    __tablename__ = "categories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name = Column(Text, nullable=False, unique=True)
    slug = Column(Text, nullable=False, unique=True)


class Article(Base):
    __tablename__ = "articles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    topic = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    image_url = Column(Text)

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    views = Column(Integer, nullable=False, default=0)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    category = relationship("Category")
