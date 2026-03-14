from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import enum

# Enum for UserPermission type, mirroring SQLAlchemy's Enum
class PermissionTypeEnum(str, enum.Enum):
    ADD = "Add"
    REMOVE = "Remove"

# Schemas for Roles
class RoleBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None

    class Config: # Added Config for orm_mode, good practice even if no direct ORM fields
        orm_mode = True

class Role(RoleBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # users: List[int] = [] # Omitted as per self-correction
    # permissions: List[str] = [] # Omitted as per self-correction

    class Config:
        orm_mode = True

# Schemas for Permissions
class PermissionBase(BaseModel):
    permission: str
    title: str
    category: str

    class Config:
        orm_mode = True

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    permission: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None

    class Config: # Added Config for orm_mode
        orm_mode = True

class Permission(PermissionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Schemas for RolesPermissions
class RolePermissionBase(BaseModel):
    role_id: str
    permission_id: str

    class Config:
        orm_mode = True

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionUpdate(BaseModel):
    role_id: Optional[str] = None
    permission_id: Optional[str] = None

    class Config: # Added Config for orm_mode
        orm_mode = True

class RolePermission(RolePermissionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # role: Optional[Role] = None # Omitted for now
    # permission: Optional[Permission] = None # Omitted for now

    class Config:
        orm_mode = True

# Schemas for UserPermissions
class UserPermissionBase(BaseModel):
    user_id: int # Matches User.id type (Integer)
    permission_id: str
    type: PermissionTypeEnum

    class Config:
        orm_mode = True

class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermissionUpdate(BaseModel):
    user_id: Optional[int] = None
    permission_id: Optional[str] = None
    type: Optional[PermissionTypeEnum] = None

    class Config: # Added Config for orm_mode
        orm_mode = True

class UserPermission(UserPermissionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # user: Optional[UserSchema] = None # Omitted for now
    # permission: Optional[Permission] = None # Omitted for now

    class Config:
        orm_mode = True
