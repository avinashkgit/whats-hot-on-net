from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy import Boolean
from pydantic import BaseModel


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
    image_model = Column(Text)

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


class NotificationToken(Base):
    __tablename__ = "notification_tokens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    token = Column(Text, nullable=False, unique=True)
    platform = Column(Text, nullable=False)  # web / android / ios

    device_id = Column(Text, nullable=True)
    browser = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    last_seen_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class NotificationTokenCreate(BaseModel):
    token: str
    platform: str
    device_id: str | None = None
    browser: str | None = None