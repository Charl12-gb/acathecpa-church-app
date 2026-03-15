from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class ContentType(enum.Enum):
    article = "article"
    podcast = "podcast"

class ContentFormat(enum.Enum):
    audio = "audio"
    video = "video"
    text = "text"
    pdf = "pdf"

class ContentStatus(enum.Enum):
    draft = "draft"
    published = "published"

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    content_body = Column(Text, nullable=True) # Renamed from 'content' to avoid clash
    type = Column(SQLAlchemyEnum(ContentType), nullable=False)
    format = Column(SQLAlchemyEnum(ContentFormat), nullable=True)
    media_url = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
    price = Column(Float, nullable=True) # Assuming price can be decimal
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLAlchemyEnum(ContentStatus), default=ContentStatus.draft)
    tags = Column(JSON, nullable=True) # Storing tags as a JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="authored_content")

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.type.value}')>"
