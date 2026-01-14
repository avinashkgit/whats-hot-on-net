import uuid
from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


# ============================
# Topic Model
# ============================

class Topic(Base):
    __tablename__ = "topics"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(Text, nullable=False, unique=True)
    slug = Column(Text, nullable=False, unique=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    articles = relationship(
        "Article",
        back_populates="topic",
        cascade="all, delete-orphan",
    )


# ============================
# Article Model
# ============================

class Article(Base):
    __tablename__ = "articles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)

    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    image_url = Column(Text)

    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
    )

    views = Column(
        Integer,
        nullable=False,
        server_default="0",
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    topic = relationship(
        "Topic",
        back_populates="articles",
    )
