from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import user as user_schema
from app.services import user_service
from app.dependencies import auth as auth_deps
from app.core.config import settings
from app.models.user import User # UserRole removed
from app.permissions.dependencies import RequirePermission
from typing import Optional

router = APIRouter(prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

# Example Route 1: View All Users (Protected by 'view_any_user' permission)
# This modifies the existing GET "/" route for listing users.
@router.get(
    "/",
    response_model=List[user_schema.User],
    dependencies=[Depends(RequirePermission("view_any_user"))],
)
def read_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(auth_deps.get_db),
):
    filtered_role = role if role and role.lower() != "all" else ''
    users = user_service.get_users(db, role=filtered_role, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=user_schema.User)
def read_user(
    user_id: int,
    db: Session = Depends(auth_deps.get_db),
    # current_user: User = Depends(auth_deps.get_current_active_user) # Old dependency
    current_user: User = Depends(RequirePermission("view_any_user_profile_detail")) # New dependency
):
    # The old role-based check is removed. "view_any_user_profile_detail" implies ability to see any.
    # If self-view was intended here and user_id == current_user.id, that logic would be separate
    # or part of a "view_own_profile_detail" permission if this endpoint served both.
    # For now, this endpoint is for users who can view *any* user's details.
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=user_schema.User)
def update_user_details(
    user_id: int,
    user_in: user_schema.UserUpdate,
    db: Session = Depends(auth_deps.get_db),
    # current_user: User = Depends(auth_deps.get_current_active_user) # Old dependency
    current_user: User = Depends(RequirePermission("edit_any_user_profile_detail")) # New, more privileged permission
):
    # Old role-based checks for self-update vs admin update are removed from router.
    # "edit_any_user_profile_detail" implies admin/privileged access.
    # The service layer (user_service.update_user) might still need to check if
    # non-admin users are trying to change fields they shouldn't (e.g. role_id, is_active),
    # or if a user with "edit_own_profile" (on a different endpoint) tries to edit others.
    # For this endpoint, it's assumed the user has "edit_any_user_profile_detail".
    # The service layer should be responsible for fine-grained field control if user_in.role_id is part of UserUpdate.
    updated_user = user_service.update_user(db, user_id=user_id, user_update=user_in, requesting_user=current_user) # Pass current_user to service
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=user_schema.User, dependencies=[Depends(auth_deps.require_admin)])
def delete_user_account( 
    user_id: int,
    db: Session = Depends(auth_deps.get_db),
    # current_user: User = Depends(auth_deps.require_super_admin) # Example if only super_admin can delete
    # Ensure current_user is injected by the RequirePermission dependency for the self-delete check
    current_requesting_user: User = Depends(RequirePermission("delete_any_user")) # Added for self-delete check
):
    # Fetch the user to be deleted first to check ownership
    db_user_to_delete = user_service.get_user(db, user_id=user_id)
    if db_user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to delete not found")

    # Prevent self-deletion through this admin endpoint
    if db_user_to_delete.id == current_requesting_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot delete their own account via this endpoint. Use specific account management features.")
    
    deleted_user = user_service.delete_user(db, user_id=user_id)
    # user_service.delete_user might return None if user not found, or the deleted user object.
    # The check above for db_user_to_delete already handles not found, so deleted_user should be the object.
    if deleted_user is None: 
        # This case might be redundant if get_user above confirms existence.
        # However, it's a safe fallback if delete_user has its own not-found check.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found during deletion process")
    return deleted_user
