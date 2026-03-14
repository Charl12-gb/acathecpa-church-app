import app.models
from pydantic import BaseModel
from typing import Optional
from datetime import datetime 
from app.schemas.user import UserBase

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None 
    token_type: str = "bearer"
    user: Optional[UserBase] = None 

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject (usually user ID or email)
    exp: Optional[datetime] = None # Expiry time
    # Add any other custom claims you need
    # E.g., roles: List[str] = []
