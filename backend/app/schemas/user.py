from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.permissions.schemas import RoleBase
from .professor import ProfessorProfile 
from app.schemas.professor import (
    ProfessorProfile,
    EducationEntry,
    ExperienceEntry,
    SocialLinks
)

# Base schema for common attributes
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    birthdate: Optional[str] = None
    role: Optional[RoleBase] = None

# Schema for user creation
class UserCreate(UserBase):
    password: str = Field(min_length=8)
    name: str # Name is required for creation based on auth.ts register
    # first_name from auth.ts can be part of 'name' or a separate field if needed

# Schema for user update (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    birthdate: Optional[str] = None
    role: Optional[RoleBase] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


# Schema for reading user data (typically for responses)
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    professor_profile: Optional[ProfessorProfile] = None # Add professor_profile
    # Add relationships if they should be returned by default, e.g.,
    # authored_content: List['Content'] = [] # Forward reference for circular deps
    # instructed_courses: List['Course'] = []

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class ProfessorUserAndProfileCreate(UserBase): # Hérite des champs utilisateur de UserBase
    password: str = Field(..., min_length=8) # Mot de passe requis pour un nouvel utilisateur

    # Champs du profil directement au même niveau
    specialization: str = Field(..., min_length=1)
    bio: Optional[str] = None
    education: Optional[List[EducationEntry]] = Field(default_factory=list)
    experience: Optional[List[ExperienceEntry]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    social_links: Optional[SocialLinks] = Field(default_factory=SocialLinks)