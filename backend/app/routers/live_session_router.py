from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas import live_session as ls_schema
from app.models.user import User as UserModel # UserRole removed as permissions handle roles
from app.services import live_session_service as ls_service # Aliased
from app.dependencies import auth as auth_deps
from app.core.config import settings
from app.models import course as course_model # For checking course instructor
# Import for new permission system
from app.permissions.dependencies import RequirePermission

router = APIRouter(prefix=f"{settings.API_V1_STR}/live-sessions", tags=["Live Sessions"])

@router.post("/", response_model=ls_schema.LiveSession, status_code=status.HTTP_201_CREATED)
def create_new_live_session(
    session_in: ls_schema.LiveSessionCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_live_session"))
):
    # Authorization (e.g. is user instructor of the course_id in session_in) is handled in the service layer.
    result = ls_service.create_live_session(db=db, session=session_in, host_id=current_user.id)
    
    if result == "CourseNotFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if result == "NotAuthorizedToHost":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized to host sessions for this course")
    if result == "HostUserNotFound": 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host user not found") # Should be caught by RequirePermission
    if isinstance(result, str): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
        
    return result

@router.get("/course/{course_id}", response_model=List[ls_schema.LiveSession], dependencies=[Depends(RequirePermission("view_live_sessions_for_course"))])
def read_sessions_for_course(
    course_id: int, 
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(auth_deps.get_db)
    # current_user: UserModel = Depends(RequirePermission("view_live_sessions_for_course")) - if user object needed
):
    # Service should handle visibility based on user's enrollment or admin status for the course_id.
    db_course = db.query(course_model.Course).filter(course_model.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
    sessions = ls_service.get_live_sessions_for_course(db, course_id, skip, limit)
    return sessions

@router.get("/{session_id}", response_model=ls_schema.LiveSession, dependencies=[Depends(RequirePermission("view_live_session_detail"))])
def read_single_live_session(
    session_id: int, 
    db: Session = Depends(auth_deps.get_db)
    # current_user: UserModel = Depends(RequirePermission("view_live_session_detail")) - if user object needed
):
    # Service should handle visibility
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
    # Service layer `update_live_session` should handle ownership/admin check using current_user.
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
    # Service layer `delete_live_session` should handle ownership/admin check.
    deleted_session = ls_service.delete_live_session(db, session_id, current_user)
    if deleted_session == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this live session")
    if deleted_session is None: # Not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
    if isinstance(deleted_session, str): # Catch any other string error messages from service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=deleted_session)
    return deleted_session

# Placeholder for Agora token generation endpoint
# @router.post("/{session_id}/join-token", response_model=ls_schema.AgoraToken) # Define AgoraToken schema
# def get_agora_join_token(
#     session_id: int,
#     db: Session = Depends(auth_deps.get_db),
#     current_user: UserModel = Depends(auth_deps.get_current_active_user)
# ):
#     db_session = ls_service.get_live_session(db, session_id)
#     if not db_session:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live session not found")
#     
#     # Check if user is allowed to join (e.g., enrolled in course)
#     # ... authorization logic ...
# 
#     # Check if session is live or scheduled
#     if db_session.status not in [ls_model.LiveSessionStatus.scheduled, ls_model.LiveSessionStatus.live]:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not available to join")
# 
#     # token = ls_service.generate_agora_token(db_session.agora_channel_name, current_user.id)
#     # return {"token": token, "channel_name": db_session.agora_channel_name}
#     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agora token generation not implemented")
