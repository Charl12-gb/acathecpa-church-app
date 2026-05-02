from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas import live_session as ls_schema
from app.models.user import User as UserModel # UserRole removed as permissions handle roles
from app.services import live_session_service as ls_service # Aliased
from app.dependencies import auth as auth_deps
from app.core.config import settings
from app.models import course as course_model # For checking course instructor
# Import for new permission system
from app.permissions.dependencies import RequirePermission

router = APIRouter(prefix=f"{settings.API_V1_STR}/live-sessions", tags=["Live Sessions"])

@router.get("/", response_model=List[ls_schema.LiveSession])
def read_all_live_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_live_sessions_for_course"))
):
    """List all live sessions. Professors see only their own, admins see all."""
    role_name = current_user.role.name if current_user.role else None
    if role_name in ["admin", "super_admin"]:
        sessions = ls_service.get_all_live_sessions(db, skip, limit)
    else:
        sessions = ls_service.get_live_sessions_for_host(db, current_user.id, skip, limit)
    return sessions

@router.post("/", response_model=ls_schema.LiveSession, status_code=status.HTTP_201_CREATED)
def create_new_live_session(
    session_in: ls_schema.LiveSessionCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_live_session"))
):
    result = ls_service.create_live_session(db=db, session=session_in, host_id=current_user.id)

    if result == "CourseNotFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if result == "NotAuthorizedToHost":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to host sessions for this course")
    if result == "HostUserNotFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host user not found")
    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

    return result

@router.get("/course/{course_id}", response_model=List[ls_schema.LiveSession], dependencies=[Depends(RequirePermission("view_live_sessions_for_course"))])
def read_sessions_for_course(
    course_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(auth_deps.get_db)
):
    db_course = db.query(course_model.Course).filter(course_model.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    sessions = ls_service.get_live_sessions_for_course(db, course_id, skip, limit)
    return sessions

@router.get("/{session_id}", response_model=ls_schema.LiveSession, dependencies=[Depends(RequirePermission("view_live_session_detail"))])
def read_single_live_session(
    session_id: int,
    db: Session = Depends(auth_deps.get_db)
):
    db_session = ls_service.get_live_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    return db_session

@router.put("/{session_id}", response_model=ls_schema.LiveSession)
def update_existing_live_session(
    session_id: int,
    session_in: ls_schema.LiveSessionUpdate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_live_session"))
):
    updated_session = ls_service.update_live_session(db, session_id, session_in, current_user)
    if updated_session == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this live session")
    if updated_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    if isinstance(updated_session, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_session)
    return updated_session

@router.delete("/{session_id}", response_model=ls_schema.LiveSession)
def delete_existing_live_session(
    session_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_live_session"))
):
    deleted_session = ls_service.delete_live_session(db, session_id, current_user)
    if deleted_session == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this live session")
    if deleted_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    if isinstance(deleted_session, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=deleted_session)
    return deleted_session

@router.patch("/{session_id}/status", response_model=ls_schema.LiveSession)
def update_live_session_status(
    session_id: int,
    status_update: ls_schema.LiveSessionStatusUpdate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_live_session"))
):
    """Update only the status of a live session (scheduled -> live -> ended)."""
    result = ls_service.update_live_session_status(db, session_id, status_update.status, current_user)
    if result == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this live session")
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result

from app.models.live_session import LiveSessionStatus as LSStatus

@router.get("/{session_id}/attendance", response_model=ls_schema.LiveSessionAttendanceSummary)
def read_live_session_attendance(
    session_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_live_session_detail"))
):
    summary = ls_service.get_live_session_attendance_summary(db, session_id)
    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    return summary

@router.post("/{session_id}/reschedule", response_model=ls_schema.LiveSession, status_code=status.HTTP_201_CREATED)
def reschedule_existing_live_session(
    session_id: int,
    payload: ls_schema.LiveSessionReschedule,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_live_session"))
):
    result = ls_service.reschedule_live_session(db, session_id, payload, current_user)
    if result == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reschedule this live session")
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result

@router.post("/{session_id}/join", response_model=ls_schema.JitsiJoinResponse)
def join_live_session(
    session_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_live_session_detail"))
):
    """Get Jitsi/JaaS credentials to join a live session."""
    db_session = ls_service.get_live_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")

    if db_session.status == LSStatus.ended:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette session est terminée")

    if not settings.JITSI_APP_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La visioconférence n'est pas configurée. Veuillez définir JITSI_APP_ID."
        )

    room = db_session.meeting_room_name or f"live-session-{db_session.id}"
    domain = settings.JITSI_DOMAIN
    url = f"https://{domain}/{settings.JITSI_APP_ID}/{room}"
    ls_service.record_live_session_join(db, db_session, current_user)

    return {
        "app_id": settings.JITSI_APP_ID,
        "domain": domain,
        "room": room,
        "url": url,
        "jwt": settings.JITSI_JWT,
        "uid": current_user.id
    }

@router.post("/{session_id}/leave")
def leave_live_session(
    session_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_live_session_detail"))
):
    db_session = ls_service.get_live_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")

    ls_service.record_live_session_leave(db, session_id, current_user)
    return {"detail": "Presence updated"}
