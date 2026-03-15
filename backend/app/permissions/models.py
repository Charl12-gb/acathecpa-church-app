from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Import Base from the central database.py
from app.database import Base 

def generate_uuid():
    return str(uuid.uuid4())

class UserRoleEnum(SQLAlchemyEnum):
    admin = "admin"
    professor = "professor"
    student = "student"
    super_admin = "super_admin"

class Roles(Base):
    __tablename__ = "roles"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    users = relationship("User", back_populates="role")
    permissions = relationship("RolesPermissions", back_populates="role")

class Permissions(Base):
    __tablename__ = "permissions"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    permission = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles_permissions = relationship("RolesPermissions", back_populates="permission")
    user_permissions = relationship("UserPermissions", back_populates="permission")

class RolesPermissions(Base):
    __tablename__ = "roles_permissions"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    role_id = Column(String(36), ForeignKey("roles.id"))
    permission_id = Column(String(36), ForeignKey("permissions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    role = relationship("Roles", back_populates="permissions")
    permission = relationship("Permissions", back_populates="roles_permissions")

class UserPermissions(Base):
    __tablename__ = "user_permissions"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    permission_id = Column(String(36), ForeignKey("permissions.id"))
    type = Column(SQLAlchemyEnum("Add", "Remove", name="permission_type_enum"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permissions", back_populates="user_permissions")
