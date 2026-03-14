from typing import Optional, List, Union # Added Union
from sqlalchemy.orm import Session
from app.models.content import Content, ContentType, ContentStatus
from app.models.user import User
from app.permissions.models import Roles as UserRole
from app.schemas.content import ContentCreate, ContentUpdate

def get_content(db: Session, content_id: int) -> Optional[Content]:
    return db.query(Content).filter(Content.id == content_id).first()

def get_all_contents(db: Session, skip: int = 0, limit: int = 100, type: Optional[ContentType] = None, status: Optional[ContentStatus] = ContentStatus.published) -> List[Content]:
    query = db.query(Content)
    if type:
        query = query.filter(Content.type == type)
    if status: # Default to published, pass None or specific status to override
        query = query.filter(Content.status == status)
    return query.offset(skip).limit(limit).all()
 
def get_user_contents(db: Session, user_id: int, skip: int = 0, limit: int = 100, status: Optional[ContentStatus] = None) -> List[Content]:
    query = db.query(Content).filter(Content.author_id == user_id)
    if status:
        query = query.filter(Content.status == status)
    return query.offset(skip).limit(limit).all()

def create_content(db: Session, content: ContentCreate, author_id: int) -> Content:
    db_content = Content(**content.dict(), author_id=author_id)
    # If status is not provided in ContentCreate, it defaults to 'draft' as per model/schema
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content(db: Session, content_id: int, content_update: ContentUpdate, current_user: User) -> Optional[Union[Content, str]]:
    db_content = get_content(db, content_id)
    if not db_content:
        return None
    
    # Authorization: only author or admin/super_admin can update
    if db_content.author_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorized" # Special return to indicate auth failure cleanly

    update_data = content_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def delete_content(db: Session, content_id: int, current_user: User) -> Optional[Union[Content, str]]: # Changed type hint
    db_content = get_content(db, content_id)
    if not db_content:
        return None

    if db_content.author_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorized"

    db.delete(db_content)
    db.commit()
    return db_content # Return the deleted content object

def publish_content(db: Session, content_id: int, current_user: User) -> Optional[Union[Content, str]]: # Changed type hint
    db_content = get_content(db, content_id)
    if not db_content:
        return None
    
    if db_content.author_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorized"
        
    db_content.status = ContentStatus.published
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content
