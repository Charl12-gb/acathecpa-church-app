from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.models.user import User as UserModel
from app.models.course import Course
from app.models.course_lesson import CourseLesson
from app.models.course_section import CourseSection
from app.models.certificate import Certificate
from app.schemas.student import (
    StudentDashboardStats,
    EnrolledCourse,
    OverallProgress,
    WeeklyActivity,
    RecommendedCourse,
    RecentCertificate,
)


async def get_student_dashboard_stats_service(db: Session, current_user: UserModel) -> StudentDashboardStats:
    enrolled_courses_count = db.query(func.count(Course.id))\
        .join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id).scalar()

    certificates_count = db.query(func.count(Certificate.id))\
        .filter(Certificate.user_id == current_user.id).scalar()

    completed_lessons = db.query(func.count(CourseLesson.id))\
        .join(CourseSection).join(Course)\
        .join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id, CourseLesson.is_completed == True).scalar()

    total_lessons = db.query(func.count(CourseLesson.id))\
        .join(CourseSection).join(Course)\
        .join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id).scalar()

    total_study_hours = completed_lessons * 0.5
    average_progress = (completed_lessons / total_lessons * 100) if total_lessons else 0

    return StudentDashboardStats(
        enrolled_courses_count=enrolled_courses_count,
        certificates_count=certificates_count,
        total_study_hours=round(total_study_hours, 1),
        average_progress=round(average_progress, 1)
    )


async def get_student_enrolled_courses_service(db: Session, current_user: UserModel) -> List[EnrolledCourse]:
    courses = db.query(Course).join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id).all()

    enrolled = []
    for course in courses:
        total_lessons = sum(len(section.lessons) for section in course.sections)
        completed_lessons = sum(
            1 for section in course.sections for lesson in section.lessons if lesson.is_completed
        )
        progress = (completed_lessons / total_lessons * 100) if total_lessons else 0.0

        enrolled.append(EnrolledCourse(
            id=course.id,
            title=course.title,
            progress=round(progress, 1),
            last_activity_timestamp=course.updated_at.isoformat() if course.updated_at else None,
            image_url=course.image_url or f"https://picsum.photos/seed/{course.id}/300/200"
        ))
    return enrolled


async def get_student_overall_progress_service(db: Session, current_user: UserModel) -> OverallProgress:
    total_lessons = db.query(func.count(CourseLesson.id))\
        .join(CourseSection).join(Course)\
        .join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id).scalar()

    completed_lessons = db.query(func.count(CourseLesson.id))\
        .join(CourseSection).join(Course)\
        .join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id, CourseLesson.is_completed == True).scalar()

    completed_percentage = (completed_lessons / total_lessons * 100) if total_lessons else 0
    in_progress_percentage = 100 - completed_percentage if total_lessons else 0

    return OverallProgress(
        completed_percentage=round(completed_percentage, 1),
        in_progress_percentage=round(in_progress_percentage, 1)
    )


async def get_student_weekly_activity_service(db: Session, current_user: UserModel) -> List[WeeklyActivity]:
    today = datetime.utcnow().date()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    activities = []

    for i in range(7):
        day_date = today - timedelta(days=6 - i)
        # Suppose que CourseLesson.updated_at est défini comme dernière mise à jour
        completed_today = db.query(func.count(CourseLesson.id))\
            .join(CourseSection).join(Course)\
            .join(Course.enrolled_students)\
            .filter(
                UserModel.id == current_user.id,
                CourseLesson.is_completed == True,
                func.date(CourseLesson.updated_at) == day_date
            ).scalar()
        study_hours = completed_today * 0.5
        activities.append(WeeklyActivity(day_of_week=days[i], study_hours=round(study_hours, 1)))
    return activities


async def get_student_recommended_courses_service(db: Session, current_user: UserModel) -> List[RecommendedCourse]:
    enrolled_course_ids = db.query(Course.id).join(Course.enrolled_students)\
        .filter(UserModel.id == current_user.id).subquery()

    recommended = db.query(Course).filter(~Course.id.in_(enrolled_course_ids)).limit(3).all()

    return [
        RecommendedCourse(
            id=course.id,
            title=course.title,
            category=course.category,
            instructor_name=course.instructor.name if hasattr(course.instructor, "name") else "Instructor",
            duration_weeks=6,
            image_url=course.image_url or f"https://picsum.photos/seed/{course.id}/300/200"
        )
        for course in recommended
    ]


async def get_student_recent_certificates_service(db: Session, current_user: UserModel) -> List[RecentCertificate]:
    certificates = db.query(Certificate)\
        .filter(Certificate.user_id == current_user.id)\
        .order_by(Certificate.issue_date.desc()).limit(3).all()

    return [
        RecentCertificate(
            id=cert.id,
            course_name=cert.course.title if cert.course else "Unknown Course",
            date_obtained=cert.issue_date.strftime("%Y-%m-%d")
        )
        for cert in certificates
    ]
