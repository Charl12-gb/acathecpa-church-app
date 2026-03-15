from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Models needed for the check_permission function and RequirePermission
from app.permissions import models # This will allow access to models.Permissions, models.Roles, etc.
# User model
from app.models.user import User
# Database session
from app.database import get_db

# Current user dependency
from app.dependencies.auth import get_current_active_user

def check_permission(user: User, permission_name: str, db: Session) -> bool:
    # First, check role-based permissions
    # Ensure user.role_id is available. The User model has role_id.
    if user.role_id: # Only check role permissions if a role_id is assigned
        role_permission = db.query(models.RolesPermissions).join(models.Permissions).filter(
            models.RolesPermissions.role_id == user.role_id,
            models.Permissions.permission == permission_name
        ).first()

        if role_permission:
            # Now, we need to ensure this permission wasn't explicitly revoked for the user.
            user_removed_permission_for_role = db.query(models.UserPermissions).join(models.Permissions).filter(
                models.UserPermissions.user_id == user.id,
                models.Permissions.permission == permission_name,
                models.UserPermissions.type == "Remove" 
            ).first()
            if user_removed_permission_for_role:
                return False # Role permission exists, but user has it explicitly revoked
            return True # Role permission exists and not revoked for user

    # If no role permission (or no role_id), then check for direct user grants (type "Add")
    user_added_permission = db.query(models.UserPermissions).join(models.Permissions).filter(
        models.UserPermissions.user_id == user.id,
        models.Permissions.permission == permission_name,
        models.UserPermissions.type == "Add"
    ).first()

    if user_added_permission:
        return True

    # An explicit "Remove" without a corresponding role permission or "Add" permission means denied.
    # If a "Remove" existed with a role permission, it was handled above.
    # If we are here, it means no role permission was found for the user, and no "Add" permission was found.
    # An explicit "Remove" alone doesn't grant or deny if no other rule applies, it only overrides.
    # The original logic: if a "Remove" exists, it means False. This is correct if we assume
    # that permissions are additive by default from roles, and "Remove" is a specific denial.
    # Let's stick to the provided logic which is: role -> true, add -> true, remove -> false
    
    user_removed_permission = db.query(models.UserPermissions).join(models.Permissions).filter(
        models.UserPermissions.user_id == user.id,
        models.Permissions.permission == permission_name,
        models.UserPermissions.type == "Remove"
    ).first()

    if user_removed_permission:
        return False # Explicitly denied

    # If no role permission and no specific grant, and not explicitly removed, then permission is denied.
    return False

class RequirePermission:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    def __call__(self, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        if not current_user: # Should be handled by get_current_active_user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # get_current_active_user already checks for current_user.is_active.
        # The User model has role_id, which can be None.
        # If role_id is None, the user might only have directly assigned permissions.
        # The check for `not current_user.role_id and not current_user.is_active` seems a bit off.
        # `get_current_active_user` ensures user is active.
        # A user might be active but have no role_id, relying on direct permissions.
        # Let's adjust the basic check.
        # if not current_user.is_active: # This is redundant due to get_current_active_user
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User inactive"
        #     )

        # Super_admin / admin check: full access bypass
        if current_user.role_id:
            # Fetch the role name using role_id from the User object
            role = db.query(models.Roles).filter(models.Roles.id == current_user.role_id).first()
            if role and role.name in ("super_admin", "admin"):
                return current_user # super_admin and admin have all permissions

        has_perm = check_permission(user=current_user, permission_name=self.permission_name, db=db)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Requires: {self.permission_name}"
            )
        return current_user # Return the user object if permission is granted
