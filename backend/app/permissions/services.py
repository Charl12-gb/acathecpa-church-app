from sqlalchemy.orm import Session
from typing import List, Optional, Type, Set # Added Set for type hinting
# Corrected import path for models and schemas based on typical project structure
from . import models, schemas # models.Roles, models.Permissions, models.RolesPermissions, models.UserPermissions
from fastapi import HTTPException, status

from app.models.user import User 

# Service Functions for Roles
def create_role(db: Session, role: schemas.RoleCreate) -> models.Roles:
    # Check if role name already exists
    existing_role = get_role_by_name(db, role.name)
    if existing_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already in use")
    db_role = models.Roles(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: str) -> Optional[models.Roles]:
    return db.query(models.Roles).filter(models.Roles.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[models.Roles]:
    return db.query(models.Roles).filter(models.Roles.name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Roles]:
    return db.query(models.Roles).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: str, role_update: schemas.RoleUpdate) -> Optional[models.Roles]:
    db_role = get_role(db, role_id)
    if not db_role:
        # Raise HTTPException here directly as the service layer should inform the client
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if role_update.name is not None:
        # Check if new name already exists and is not the current role's name
        existing_role = get_role_by_name(db, role_update.name)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already in use by another role")
        db_role.name = role_update.name
    
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: str) -> Optional[models.Roles]:
    db_role = get_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if db_role.users or db_role.permissions:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role cannot be deleted as it is currently in use")

    db.delete(db_role)
    db.commit()
    # Return the deleted object (now detached) for confirmation, or simply return None or a success message
    return db_role 

# Service Functions for Permissions
def create_permission(db: Session, permission: schemas.PermissionCreate) -> models.Permissions:
    existing_permission = get_permission_by_name(db, permission.permission)
    if existing_permission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission name already exists")
    db_permission = models.Permissions(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def get_permission(db: Session, permission_id: str) -> Optional[models.Permissions]:
    return db.query(models.Permissions).filter(models.Permissions.id == permission_id).first()

def get_permission_by_name(db: Session, name: str) -> Optional[models.Permissions]:
    return db.query(models.Permissions).filter(models.Permissions.permission == name).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permissions]:
    return db.query(models.Permissions).offset(skip).limit(limit).all()

def update_permission(db: Session, permission_id: str, permission_update: schemas.PermissionUpdate) -> Optional[models.Permissions]:
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    update_data = permission_update.model_dump(exclude_unset=True)
    
    if "permission" in update_data and update_data["permission"] != db_permission.permission:
        existing_permission = get_permission_by_name(db, update_data["permission"])
        if existing_permission and existing_permission.id != permission_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission name already in use")

    for key, value in update_data.items():
        setattr(db_permission, key, value)
    
    db.commit()
    db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, permission_id: str) -> Optional[models.Permissions]:
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    
    if db_permission.roles_permissions or db_permission.user_permissions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission cannot be deleted as it is currently in use")

    db.delete(db_permission)
    db.commit()
    return db_permission

# Service Functions for RolesPermissions
def add_permission_to_role(db: Session, role_permission: schemas.RolePermissionCreate) -> models.RolesPermissions:
    existing_rp = db.query(models.RolesPermissions).filter_by(
        role_id=role_permission.role_id,
        permission_id=role_permission.permission_id
    ).first()
    if existing_rp:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission already assigned to this role")

    role = get_role(db, role_permission.role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    perm = get_permission(db, role_permission.permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    db_rp = models.RolesPermissions(**role_permission.model_dump())
    db.add(db_rp)
    db.commit()
    db.refresh(db_rp)
    return db_rp

def get_role_permission_association(db: Session, role_id: str, permission_id: str) -> Optional[models.RolesPermissions]:
    return db.query(models.RolesPermissions).filter_by(role_id=role_id, permission_id=permission_id).first()

def get_permissions_for_role(db: Session, role_id: str) -> List[models.Permissions]:
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db.query(models.Permissions).join(models.RolesPermissions).filter(models.RolesPermissions.role_id == role_id).all()

def remove_permission_from_role(db: Session, role_id: str, permission_id: str) -> Optional[models.RolesPermissions]:
    db_rp = get_role_permission_association(db, role_id, permission_id)
    if not db_rp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not assigned to this role")
    db.delete(db_rp)
    db.commit()
    return db_rp

def get_role_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.RolesPermissions]:
    return db.query(models.RolesPermissions).offset(skip).limit(limit).all()

def get_role_permission_by_id(db: Session, rp_id: str) -> Optional[models.RolesPermissions]:
    return db.query(models.RolesPermissions).filter(models.RolesPermissions.id == rp_id).first()

# Service Functions for UserPermissions
def assign_permission_to_user(db: Session, user_permission: schemas.UserPermissionCreate) -> models.UserPermissions:
    perm = get_permission(db, user_permission.permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    # User existence check would go here if user_service is available
    # user = user_service.get_user(db, user_permission.user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_up = db.query(models.UserPermissions).filter_by(
        user_id=user_permission.user_id,
        permission_id=user_permission.permission_id
    ).first()
    
    if existing_up:
        existing_up.type = user_permission.type 
        db_up = existing_up
    else:
        db_up = models.UserPermissions(**user_permission.model_dump())
        db.add(db_up)
    
    db.commit()
    db.refresh(db_up)
    return db_up

def get_user_permission_override(db: Session, user_id: int, permission_id: str) -> Optional[models.UserPermissions]:
    return db.query(models.UserPermissions).filter_by(user_id=user_id, permission_id=permission_id).first()

def get_user_permissions_direct(db: Session, user_id: int) -> List[models.UserPermissions]:
    return db.query(models.UserPermissions).filter_by(user_id=user_id).all()

def revoke_permission_from_user(db: Session, user_id: int, permission_id: str) -> Optional[models.UserPermissions]:
    db_up = get_user_permission_override(db, user_id, permission_id)
    if not db_up:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User permission override not found")
    db.delete(db_up)
    db.commit()
    return db_up

def get_all_user_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.UserPermissions]:
    return db.query(models.UserPermissions).offset(skip).limit(limit).all()

def get_user_permission_by_id(db: Session, up_id: str) -> Optional[models.UserPermissions]:
    return db.query(models.UserPermissions).filter(models.UserPermissions.id == up_id).first()