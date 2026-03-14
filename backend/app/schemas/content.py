from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
# Enums from models
from app.models.content import ContentType, ContentFormat, ContentStatus
from .user import User # For author representation

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_body: Optional[str] = None
    type: ContentType
    format: Optional[ContentFormat] = None
    media_url: Optional[HttpUrl] = None # Validate as URL
    is_premium: bool = False
    price: Optional[float] = None
    status: ContentStatus = ContentStatus.draft
    tags: Optional[List[str]] = []

class ContentCreate(ContentBase):
    author_id: Optional[int] = None # Will be set from current user usually

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_body: Optional[str] = None
    type: Optional[ContentType] = None
    format: Optional[ContentFormat] = None
    media_url: Optional[HttpUrl] = None
    is_premium: Optional[bool] = None
    price: Optional[float] = None
    status: Optional[ContentStatus] = None
    tags: Optional[List[str]] = None

class Content(ContentBase):
    id: int
    author_id: int
    author: Optional[User] = None # Nested author information
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
