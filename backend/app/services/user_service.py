from typing import Optional, List
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.permissions.models import Roles
from app.models.professor import ProfessorProfile # Import ProfessorProfile
from app.schemas.user import UserCreate, UserUpdate # UserCreate might be similar to auth_service
from app.services.auth_service import get_password_hash # For password updates

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).options(joinedload(User.professor_profile)).filter(User.id == user_id).first()
def get_users(db: Session, role: Optional[str] = '', skip: int = 0, limit: int = 100) -> List[User]:
    query = db.query(User).options(
        joinedload(User.professor_profile),
        joinedload(User.role)
    )

    if role and role.lower() != 'all':
        query = query.filter(User.role.has(Roles.name == role))

    return query.offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user_update: UserUpdate, requesting_user: User) -> Optional[User]: # Added requesting_user
    db_user = get_user(db, user_id) # This now also loads professor_profile if accessed
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
        del update_data["password"] # Don't try to set it directly via setattr

    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    # Option 1: Mark as inactive (soft delete)
    # db_user.is_active = False
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    # return db_user

    # Option 2: Actual delete (hard delete)
    db.delete(db_user) 
    db.commit()
    return db_user # Return the user that was deleted (its state in session before deletion)
