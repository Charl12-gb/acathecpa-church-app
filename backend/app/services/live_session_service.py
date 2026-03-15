import uuid # For channel name generation
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from app.models import live_session as ls_model
from app.models import user as user_model
from app.models import course as course_model
from app.schemas import live_session as ls_schema
def _is_admin(user) -> bool:
    role_name = user.role.name if user.role else None
    return role_name in ["admin", "super_admin"]

def create_live_session(db: Session, session: ls_schema.LiveSessionCreate, host_id: int) -> Union[ls_model.LiveSession, str]:
    host_user = db.query(user_model.User).filter(user_model.User.id == host_id).first()
    if not host_user:
        return "HostUserNotFound"

    # If a course is specified, verify it exists and user is authorized
    if session.course_id:
        course = db.query(course_model.Course).filter(course_model.Course.id == session.course_id).first()
        if not course:
            return "CourseNotFound"
        if course.instructor_id != host_id and not _is_admin(host_user):
            return "NotAuthorizedToHost"

    db_session_data = session.dict(exclude={"host_id"})
    if not db_session_data.get("agora_channel_name"):
        prefix = f"course_{session.course_id}" if session.course_id else "meet"
        db_session_data["agora_channel_name"] = f"live_session_{prefix}_{uuid.uuid4().hex[:12]}"
    
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
    return db.query(ls_model.LiveSession).order_by(ls_model.LiveSession.scheduled_for.desc()).offset(skip).limit(limit).all()

def get_live_sessions_for_host(db: Session, host_id: int, skip: int = 0, limit: int = 100) -> List[ls_model.LiveSession]:
    return db.query(ls_model.LiveSession).filter(ls_model.LiveSession.host_id == host_id).order_by(ls_model.LiveSession.scheduled_for.desc()).offset(skip).limit(limit).all()

def update_live_session_status(db: Session, session_id: int, new_status: ls_model.LiveSessionStatus, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None
    if db_session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"
    db_session.status = new_status
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_live_session(db: Session, session_id: int, session_update: ls_schema.LiveSessionUpdate, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None # Not found

    # Authorization: Only host or admin/super_admin can update
    if db_session.host_id != current_user.id and not _is_admin(current_user):
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

    if db_session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"

    db.delete(db_session)
    db.commit()
    return db_session # Return the deleted session object

def generate_agora_token(app_id: str, app_certificate: str, channel_name: str, uid: int) -> Optional[str]:
    """Generate an Agora RTC token. Requires agora-token-builder package."""
    try:
        from agora_token_builder import RtcTokenBuilder, Role_Publisher
        import time
        expiration = int(time.time()) + 3600 * 24
        return RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, uid, Role_Publisher, expiration
        )
    except ImportError:
        return None
