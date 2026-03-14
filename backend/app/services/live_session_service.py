import uuid # For channel name generation
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from app.models import live_session as ls_model
from app.models import user as user_model
from app.models import course as course_model
from app.schemas import live_session as ls_schema
from app.permissions.models import Roles as UserRole

def create_live_session(db: Session, session: ls_schema.LiveSessionCreate, host_id: int) -> Union[ls_model.LiveSession, str]:
    course = db.query(course_model.Course).filter(course_model.Course.id == session.course_id).first()
    if not course:
        return "CourseNotFound"
    
    # Authorization: Check if the host is the course instructor or an admin/super_admin
    host_user = db.query(user_model.User).filter(user_model.User.id == host_id).first()
    if not host_user: # Should not happen if host_id comes from current_user
        return "HostUserNotFound"
        
    if course.instructor_id != host_id and host_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorizedToHost"

    db_session_data = session.dict()
    if not db_session_data.get("agora_channel_name"):
        # Create a unique channel name, e.g., based on course_id and a new uuid
        db_session_data["agora_channel_name"] = f"live_session_course_{session.course_id}_{uuid.uuid4().hex[:12]}"
    
    db_session = ls_model.LiveSession(**db_session_data, host_id=host_id)
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_live_session(db: Session, session_id: int) -> Optional[ls_model.LiveSession]:
    return db.query(ls_model.LiveSession).filter(ls_model.LiveSession.id == session_id).first()

def get_live_sessions_for_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[ls_model.LiveSession]:
    return db.query(ls_model.LiveSession).filter(ls_model.LiveSession.course_id == course_id).order_by(ls_model.LiveSession.scheduled_for.desc()).offset(skip).limit(limit).all()

def get_all_live_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ls_model.LiveSession]:
    # Could filter by status (e.g., only show scheduled or live ones by default)
    return db.query(ls_model.LiveSession).order_by(ls_model.LiveSession.scheduled_for.desc()).offset(skip).limit(limit).all()

def update_live_session(db: Session, session_id: int, session_update: ls_schema.LiveSessionUpdate, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None # Not found

    # Authorization: Only host or admin/super_admin can update
    if db_session.host_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorized"

    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_live_session(db: Session, session_id: int, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None # Not found

    if db_session.host_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.super_admin]:
        return "NotAuthorized"

    db.delete(db_session)
    db.commit()
    return db_session # Return the deleted session object

# Placeholder for Agora token generation - this would typically involve the Agora SDK
# and would be called when a user tries to join a session.
# For now, it's out of scope of this service's direct DB interactions.
# def generate_agora_token(channel_name: str, user_id: int) -> str:
#     # Logic to generate Agora token
#     # This would use settings.AGORA_APP_ID, settings.AGORA_APP_CERTIFICATE
#     # from your app.core.config
#     return "dummy_agora_token_replace_with_real_one"
