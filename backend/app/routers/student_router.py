from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, require_student
from app.models.user import User as UserModel
from app.services import student_service as student_dashboard_services 
from app.schemas.student import (
    StudentDashboardStats,
    EnrolledCourse,
    OverallProgress,
    WeeklyActivity,
    RecommendedCourse,
    RecentCertificate,
)
from app.core.config import settings # For API_V1_ST

student_dashboard_router = APIRouter(
    prefix=f"{settings.API_V1_STR}/student/dashboard", 
    tags=["Student Dashboard"],
    dependencies=[Depends(require_student)] 
)

@student_dashboard_router.get("/stats", response_model=StudentDashboardStats, summary="Get Student Dashboard Statistics")
async def get_student_dashboard_stats(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve statistics for the logged-in student's dashboard.
    """
    return await student_dashboard_services.get_student_dashboard_stats_service(db=db, current_user=current_student)

@student_dashboard_router.get("/enrolled-courses", response_model=List[EnrolledCourse], summary="Get Student's Enrolled Courses")
async def get_student_enrolled_courses(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve the list of courses the logged-in student is enrolled in.
    """
    return await student_dashboard_services.get_student_enrolled_courses_service(db=db, current_user=current_student)

@student_dashboard_router.get("/overall-progress", response_model=OverallProgress, summary="Get Student's Overall Progress")
async def get_student_overall_progress(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve the overall progress of the logged-in student.
    """
    return await student_dashboard_services.get_student_overall_progress_service(db=db, current_user=current_student)

@student_dashboard_router.get("/weekly-activity", response_model=List[WeeklyActivity], summary="Get Student's Weekly Activity")
async def get_student_weekly_activity(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve the logged-in student's study activity for the week.
    """
    return await student_dashboard_services.get_student_weekly_activity_service(db=db, current_user=current_student)

@student_dashboard_router.get("/recommended-courses", response_model=List[RecommendedCourse], summary="Get Recommended Courses for Student")
async def get_student_recommended_courses(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve a list of courses recommended for the logged-in student.
    """
    return await student_dashboard_services.get_student_recommended_courses_service(db=db, current_user=current_student)

@student_dashboard_router.get("/recent-certificates", response_model=List[RecentCertificate], summary="Get Student's Recent Certificates")
async def get_student_recent_certificates(
    db: Session = Depends(get_db),
    current_student: UserModel = Depends(require_student)
):
    """
    Retrieve a list of certificates recently obtained by the logged-in student.
    """
    return await student_dashboard_services.get_student_recent_certificates_service(db=db, current_user=current_student)
