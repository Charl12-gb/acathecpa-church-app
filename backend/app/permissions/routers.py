from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Use relative imports for modules within the same package
from . import services, schemas, models
from app.database import get_db # get_db dependency

# Create Routers
roles_router = APIRouter(prefix="/roles", tags=["Roles"])
permissions_router = APIRouter(prefix="/permissions", tags=["Permissions"])
role_permissions_router = APIRouter(prefix="/role-permissions", tags=["Role-Permissions Associations"])
user_permissions_router = APIRouter(prefix="/user-permissions", tags=["User-Permissions Overrides"])

# Endpoints for RolesRouter
@roles_router.post("/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    # Service function create_role already handles the check for existing role name
    # and raises HTTPException. No need to duplicate the check here.
    # existing_role = services.get_role_by_name(db, name=role.name)
    # if existing_role:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    return services.create_role(db=db, role=role)

@roles_router.get("/", response_model=List[schemas.Role])
def read_roles_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_roles(db, skip=skip, limit=limit)

@roles_router.get("/{role_id}", response_model=schemas.Role)
def read_role_endpoint(role_id: str, db: Session = Depends(get_db)):
    db_role = services.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role

@roles_router.put("/{role_id}", response_model=schemas.Role)
def update_role_endpoint(role_id: str, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    # Service function update_role handles the check for role existence and name uniqueness.
    db_role = services.update_role(db, role_id=role_id, role_update=role)
    if db_role is None: # This would now only happen if the service itself returned None (e.g. not found)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role

@roles_router.delete("/{role_id}", response_model=schemas.Role)
def delete_role_endpoint(role_id: str, db: Session = Depends(get_db)):
    # Service function delete_role handles non-existence and deletion constraints.
    db_role = services.delete_role(db, role_id=role_id)
    # The service raises HTTPException if not found or if deletion is constrained.
    # If it returns None for other reasons (e.g. an explicit choice not to raise for 'not found'),
    # then this check is still valid. Given service logic, this might be redundant if service always raises.
    if db_role is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found or cannot be deleted based on service logic")
    return db_role

# Endpoints for PermissionsRouter
@permissions_router.post("/", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED)
def create_permission_endpoint(permission: schemas.PermissionCreate, db: Session = Depends(get_db)):
    # Service function create_permission handles the check for existing permission name.
    return services.create_permission(db=db, permission=permission)

@permissions_router.get("/", response_model=List[schemas.Permission])
def read_permissions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_permissions(db, skip=skip, limit=limit)

@permissions_router.get("/{permission_id}", response_model=schemas.Permission)
def read_permission_endpoint(permission_id: str, db: Session = Depends(get_db)):
    db_permission = services.get_permission(db, permission_id=permission_id)
    if db_permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return db_permission

@permissions_router.put("/{permission_id}", response_model=schemas.Permission)
def update_permission_endpoint(permission_id: str, permission: schemas.PermissionUpdate, db: Session = Depends(get_db)):
    # Service function update_permission handles non-existence and name uniqueness.
    db_permission = services.update_permission(db, permission_id=permission_id, permission_update=permission)
    if db_permission is None: # If service returns None for not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return db_permission

@permissions_router.delete("/{permission_id}", response_model=schemas.Permission)
def delete_permission_endpoint(permission_id: str, db: Session = Depends(get_db)):
    # Service function delete_permission handles non-existence and deletion constraints.
    db_permission = services.delete_permission(db, permission_id=permission_id)
    if db_permission is None: # If service returns None for not found (and doesn't raise)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found or cannot be deleted")
    return db_permission

# Endpoints for RolePermissionsRouter
@role_permissions_router.post("/", response_model=schemas.RolePermission, status_code=status.HTTP_201_CREATED)
def add_permission_to_role_endpoint(role_permission: schemas.RolePermissionCreate, db: Session = Depends(get_db)):
    # Service function add_permission_to_role handles all checks.
    return services.add_permission_to_role(db=db, role_permission=role_permission)

@role_permissions_router.get("/", response_model=List[schemas.RolePermission])
def list_role_permissions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_role_permissions(db, skip=skip, limit=limit)

@role_permissions_router.get("/{rp_id}", response_model=schemas.RolePermission)
def get_role_permission_by_id_endpoint(rp_id: str, db: Session = Depends(get_db)):
    db_rp = services.get_role_permission_by_id(db, rp_id=rp_id)
    if db_rp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role-Permission association not found")
    return db_rp

@role_permissions_router.get("/role/{role_id}/permissions", response_model=List[schemas.Permission])
def get_permissions_for_role_endpoint(role_id: str, db: Session = Depends(get_db)):
    # Service function get_permissions_for_role handles role existence check.
    return services.get_permissions_for_role(db, role_id=role_id)

@role_permissions_router.delete("/{role_id}/{permission_id}", response_model=schemas.RolePermission)
def remove_permission_from_role_endpoint(role_id: str, permission_id: str, db: Session = Depends(get_db)):
    db_rp = services.remove_permission_from_role(db, role_id=role_id, permission_id=permission_id)
    if db_rp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role-Permission association not found")
    return db_rp

# Endpoints for UserPermissionsRouter
@user_permissions_router.post("/", response_model=schemas.UserPermission, status_code=status.HTTP_201_CREATED)
def assign_permission_to_user_endpoint(user_permission: schemas.UserPermissionCreate, db: Session = Depends(get_db)):
    # Service function assign_permission_to_user handles all checks.
    return services.assign_permission_to_user(db=db, user_permission=user_permission)

@user_permissions_router.get("/", response_model=List[schemas.UserPermission])
def list_user_permissions_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_all_user_permissions(db, skip=skip, limit=limit)

@user_permissions_router.get("/{up_id}", response_model=schemas.UserPermission)
def get_user_permission_by_id_endpoint(up_id: str, db: Session = Depends(get_db)):
    db_up = services.get_user_permission_by_id(db, up_id=up_id)
    if db_up is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User-Permission override not found")
    return db_up

@user_permissions_router.get("/user/{user_id}/permissions", response_model=List[schemas.UserPermission])
def get_user_permissions_direct_endpoint(user_id: int, db: Session = Depends(get_db)):
    return services.get_user_permissions_direct(db, user_id=user_id)

@user_permissions_router.delete("/{user_id}/{permission_id}", response_model=schemas.UserPermission)
def revoke_permission_from_user_endpoint(user_id: int, permission_id: str, db: Session = Depends(get_db)):
    db_up = services.revoke_permission_from_user(db, user_id=user_id, permission_id=permission_id)
    if db_up is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User-Permission override not found")
    return db_up
