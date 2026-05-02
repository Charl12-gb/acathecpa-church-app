import uuid
from datetime import datetime
from typing import Optional, List, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import course as course_model
from app.models import enrollments as enrollment_model
from app.models import live_session as ls_model
from app.models import live_session_attendance as attendance_model
from app.models import user as user_model
from app.schemas import live_session as ls_schema


def _is_admin(user) -> bool:
    role_name = user.role.name if user.role else None
    return role_name in ["admin", "super_admin"]


def _generate_meeting_room_name(course_id: Optional[int]) -> str:
    prefix = f"course_{course_id}" if course_id else "meet"
    return f"live-session-{prefix}-{uuid.uuid4().hex[:12]}"


def _duration_seconds(start_at: Optional[datetime], end_at: Optional[datetime] = None) -> int:
    if not start_at:
        return 0
    effective_end = end_at or datetime.utcnow()
    return max(int((effective_end - start_at).total_seconds()), 0)


def _close_active_attendances(db_session: ls_model.LiveSession, closed_at: datetime) -> None:
    for attendance in db_session.attendances:
        if attendance.is_present and attendance.last_joined_at:
            attendance.total_duration_seconds = (attendance.total_duration_seconds or 0) + _duration_seconds(attendance.last_joined_at, closed_at)
            attendance.last_left_at = closed_at
            attendance.is_present = False


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
    if not db_session_data.get("meeting_room_name"):
        db_session_data["meeting_room_name"] = _generate_meeting_room_name(session.course_id)

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

    now = datetime.utcnow()
    if new_status == ls_model.LiveSessionStatus.live:
        db_session.actual_started_at = db_session.actual_started_at or now
        db_session.actual_ended_at = None
    elif new_status == ls_model.LiveSessionStatus.ended:
        db_session.actual_started_at = db_session.actual_started_at or now
        db_session.actual_ended_at = now
        _close_active_attendances(db_session, now)

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


def record_live_session_join(db: Session, db_session: ls_model.LiveSession, current_user: user_model.User) -> attendance_model.LiveSessionAttendance:
    now = datetime.utcnow()
    attendance = db.query(attendance_model.LiveSessionAttendance).filter(
        attendance_model.LiveSessionAttendance.live_session_id == db_session.id,
        attendance_model.LiveSessionAttendance.user_id == current_user.id,
    ).first()

    if attendance is None:
        attendance = attendance_model.LiveSessionAttendance(
            live_session_id=db_session.id,
            user_id=current_user.id,
            first_joined_at=now,
            last_joined_at=now,
            join_count=1,
            is_present=True,
        )
        db.add(attendance)
    elif not attendance.is_present:
        attendance.first_joined_at = attendance.first_joined_at or now
        attendance.last_joined_at = now
        attendance.join_count = (attendance.join_count or 0) + 1
        attendance.is_present = True

    if db_session.status == ls_model.LiveSessionStatus.live and not db_session.actual_started_at:
        db_session.actual_started_at = now

    db.add(db_session)
    db.commit()
    db.refresh(attendance)
    return attendance


def record_live_session_leave(db: Session, session_id: int, current_user: user_model.User) -> Optional[attendance_model.LiveSessionAttendance]:
    attendance = db.query(attendance_model.LiveSessionAttendance).filter(
        attendance_model.LiveSessionAttendance.live_session_id == session_id,
        attendance_model.LiveSessionAttendance.user_id == current_user.id,
    ).first()

    if attendance is None:
        return None

    if attendance.is_present and attendance.last_joined_at:
        now = datetime.utcnow()
        attendance.total_duration_seconds = (attendance.total_duration_seconds or 0) + _duration_seconds(attendance.last_joined_at, now)
        attendance.last_left_at = now
        attendance.is_present = False
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

    return attendance


def get_live_session_attendance_summary(db: Session, session_id: int) -> Optional[ls_schema.LiveSessionAttendanceSummary]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None

    expected_attendees = None
    if db_session.course_id:
        expected_attendees = db.query(func.count()).select_from(enrollment_model.Enrollment).filter(
            enrollment_model.Enrollment.course_id == db_session.course_id
        ).scalar() or 0

    attendees: List[ls_schema.LiveSessionAttendanceMember] = []
    for attendance in sorted(db_session.attendances, key=lambda row: row.first_joined_at or datetime.max):
        total_duration_seconds = attendance.total_duration_seconds or 0
        if attendance.is_present and attendance.last_joined_at:
            total_duration_seconds += _duration_seconds(attendance.last_joined_at)

        attendees.append(ls_schema.LiveSessionAttendanceMember(
            user_id=attendance.user_id,
            user_name=attendance.user.name if attendance.user else None,
            user_email=attendance.user.email if attendance.user else None,
            first_joined_at=attendance.first_joined_at,
            last_joined_at=attendance.last_joined_at,
            last_left_at=attendance.last_left_at,
            total_duration_seconds=total_duration_seconds,
            join_count=attendance.join_count or 0,
            is_present=attendance.is_present,
        ))

    unique_attendees = len(attendees)
    present_count = sum(1 for attendee in attendees if attendee.is_present)
    attendance_rate = None
    if expected_attendees:
        attendance_rate = round((unique_attendees / expected_attendees) * 100, 2)

    actual_duration_seconds = _duration_seconds(db_session.actual_started_at, db_session.actual_ended_at)

    return ls_schema.LiveSessionAttendanceSummary(
        session_id=db_session.id,
        title=db_session.title,
        status=db_session.status,
        scheduled_for=db_session.scheduled_for,
        planned_duration_minutes=db_session.duration_minutes,
        actual_started_at=db_session.actual_started_at,
        actual_ended_at=db_session.actual_ended_at,
        actual_duration_seconds=actual_duration_seconds,
        unique_attendees=unique_attendees,
        present_count=present_count,
        expected_attendees=expected_attendees,
        attendance_rate=attendance_rate,
        attendees=attendees,
    )


def reschedule_live_session(db: Session, session_id: int, payload: ls_schema.LiveSessionReschedule, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None

    if db_session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"

    cloned_session = ls_model.LiveSession(
        course_id=db_session.course_id,
        title=payload.title or db_session.title,
        description=payload.description if payload.description is not None else db_session.description,
        scheduled_for=payload.scheduled_for,
        duration_minutes=payload.duration_minutes if payload.duration_minutes is not None else db_session.duration_minutes,
        host_id=db_session.host_id,
        status=ls_model.LiveSessionStatus.scheduled,
        meeting_room_name=_generate_meeting_room_name(db_session.course_id),
        actual_started_at=None,
        actual_ended_at=None,
    )
    db.add(cloned_session)
    db.commit()
    db.refresh(cloned_session)
    return cloned_session


def delete_live_session(db: Session, session_id: int, current_user: user_model.User) -> Optional[Union[ls_model.LiveSession, str]]:
    db_session = get_live_session(db, session_id)
    if not db_session:
        return None # Not found

    if db_session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"

    db.delete(db_session)
    db.commit()
    return db_session # Return the deleted session object
