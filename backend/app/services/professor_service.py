from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func, extract
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.professor import ProfessorProfile as ProfessorProfileModel
from app.models.user import User as UserModel
from app.permissions.models import Roles as RolesModel
from app.models.course import Course as CourseModel, CourseStatus
from app.models.course_test import CourseTest as CourseTestModel
from app.models.course_section import CourseSection as CourseSectionModel
from app.models.enrollments import Enrollment as enrollments
from app.models.test_question import TestQuestion as TestQuestionModel
from app.models.course_test import CourseTest as CourseTestModel
from app.models.course_section import CourseSection as CourseSectionModel
from app.models.enrollments import Enrollment

from app.schemas.professor import (
    ProfessorProfileCreateForExistingUser,
    ProfessorProfileUpdate,
    AdminDashboardStats,
    ProfessorStats,
    RecentActivity,
    UserDistribution,
    MonthlyRegistration,
    ProfessorDashboardStats,
    CoursePerformance,
    StudentEngagement,
    StudentDistributionInProfessorCourses,
    ProfessorRecentActivity,
)

def add_profile_to_existing_user(db: Session, *, user_id: int, profile_in: ProfessorProfileCreateForExistingUser) -> ProfessorProfileModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    existing_profile = db.query(ProfessorProfileModel).filter(ProfessorProfileModel.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Professor profile already exists for this user.",
        )

    profile_data = profile_in.model_dump()
    db_profile = ProfessorProfileModel(**profile_data, user_id=user_id)

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def get_professor_profile_by_user_id(db: Session, *, user_id: int) -> Optional[ProfessorProfileModel]:
    return db.query(ProfessorProfileModel).filter(ProfessorProfileModel.user_id == user_id).first()

def update_professor_profile(db: Session, *, user_id: int, profile_in: ProfessorProfileUpdate) -> Optional[ProfessorProfileModel]:
    db_profile = get_professor_profile_by_user_id(db, user_id=user_id)
    if not db_profile:
        return None

    update_data = profile_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def delete_professor_profile(db: Session, *, user_id: int) -> Optional[ProfessorProfileModel]:
    db_profile = get_professor_profile_by_user_id(db, user_id=user_id)
    if not db_profile:
        return None

    db.delete(db_profile)
    db.commit()
    return db_profile

async def get_admin_dashboard_stats_service(db: Session) -> AdminDashboardStats:
    """
    Récupère les statistiques globales pour le tableau de bord de l'administrateur.
    """
    total_users = db.query(func.count(UserModel.id)).scalar()
    
    professor_role = db.query(RolesModel).filter(RolesModel.name == 'professor').first()
    total_professors = 0
    if professor_role:
        total_professors = db.query(func.count(UserModel.id)).filter(UserModel.role_id == professor_role.id).scalar()
        
    total_courses = db.query(func.count(CourseModel.id)).scalar()

    one_month_ago = datetime.utcnow() - timedelta(days=30)
    new_enrollments_last_month = db.query(func.count(UserModel.id)).filter(UserModel.created_at >= one_month_ago).scalar()

    return AdminDashboardStats(
        total_users=total_users or 0,
        total_professors=total_professors or 0,
        total_courses=total_courses or 0,
        new_enrollments_last_month=new_enrollments_last_month or 0,
    )

async def get_admin_professors_service(db: Session) -> List[ProfessorStats]:
    professor_role = db.query(RolesModel).filter(RolesModel.name == 'professor').first()
    if not professor_role:
        return []

    professors = db.query(UserModel).filter(UserModel.role_id == professor_role.id).all()
    
    professor_stats_list = []
    for prof in professors:
        courses_count = db.query(func.count(CourseModel.id)).filter(CourseModel.instructor_id == prof.id).scalar()
        
        students_count_query = db.query(func.count(Enrollment.user_id.distinct())) \
            .join(CourseModel, Enrollment.course_id == CourseModel.id) \
            .filter(CourseModel.instructor_id == prof.id)
        students_count = students_count_query.scalar()

        average_rating = 0.0  # à implémenter si tu veux la note moyenne des cours

        professor_stats_list.append(
            ProfessorStats(
                id=prof.id,
                name=prof.name or "N/A",
                email=prof.email,
                courses_count=courses_count or 0,
                students_count=students_count or 0,
                average_rating=average_rating
            )
        )
    return professor_stats_list

async def get_admin_recent_activities_service(db: Session) -> List[RecentActivity]:
    """
    Récupère une liste des activités récentes sur la plateforme pour le tableau de bord de l'administrateur.
    NOTE: Un véritable journal d'activités nécessiterait une table/modèle dédié(e) `ActivityLog`.
          Cette implémentation est une simulation basique.
    """
    activities = []
    
    recent_courses = db.query(CourseModel).order_by(CourseModel.created_at.desc()).limit(3).all()
    for course in recent_courses:
        instructor_name = "Unknown Instructor"
        if course.instructor:
            instructor_name = course.instructor.name or course.instructor.email
        activities.append(RecentActivity(
            id=f"course-{course.id}",
            user_name=instructor_name,
            action="created_course",
            resource_name=course.title,
            timestamp=course.created_at.isoformat() + "Z"
        ))

    recent_users = db.query(UserModel).order_by(UserModel.created_at.desc()).limit(3).all()
    for user in recent_users:
        activities.append(RecentActivity(
            id=f"user-{user.id}",
            user_name=user.name or user.email,
            action="Enregistrement d'un utilisateur ",
            resource_name=user.email,
            timestamp=user.created_at.isoformat() + "Z"
        ))
    
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    return activities[:5]

async def get_admin_user_distribution_service(db: Session) -> UserDistribution:
    """
    Récupère la distribution des utilisateurs par rôle pour le tableau de bord de l'administrateur.
    """
    students_count = 0
    professors_count = 0
    admins_count = 0

    student_role = db.query(RolesModel).filter(RolesModel.name == 'student').first()
    if student_role:
        students_count = db.query(func.count(UserModel.id)).filter(UserModel.role_id == student_role.id).scalar()

    professor_role = db.query(RolesModel).filter(RolesModel.name == 'professor').first()
    if professor_role:
        professors_count = db.query(func.count(UserModel.id)).filter(UserModel.role_id == professor_role.id).scalar()
    
    admin_role = db.query(RolesModel).filter(RolesModel.name == 'admin').first()
    if admin_role:
        admins_count = db.query(func.count(UserModel.id)).filter(UserModel.role_id == admin_role.id).scalar()
        
    super_admin_role = db.query(RolesModel).filter(RolesModel.name == 'super_admin').first()
    if super_admin_role:
        admins_count += db.query(func.count(UserModel.id)).filter(UserModel.role_id == super_admin_role.id).scalar()


    return UserDistribution(
        students_count=students_count or 0,
        professors_count=professors_count or 0,
        admins_count=admins_count or 0
    )

async def get_admin_monthly_registrations_service(db: Session) -> List[MonthlyRegistration]:
    """
    Récupère le nombre de nouvelles inscriptions d'utilisateurs par mois pour le tableau de bord de l'administrateur.
    Affiche les 6 derniers mois, y compris le mois en cours.
    """
    registrations = []
    today = datetime.utcnow()
    
    for i in range(5, -1, -1):
        target_month_date = today - timedelta(days=i * 30)
        first_day_of_month = datetime(target_month_date.year, target_month_date.month, 1)
        
        if first_day_of_month.month == 12:
            first_day_of_next_month = datetime(first_day_of_month.year + 1, 1, 1)
        else:
            first_day_of_next_month = datetime(first_day_of_month.year, first_day_of_month.month + 1, 1)

        count = db.query(func.count(UserModel.id)).filter(
            UserModel.created_at >= first_day_of_month,
            UserModel.created_at < first_day_of_next_month
        ).scalar()
        
        month_abbr = first_day_of_month.strftime("%b")

        registrations.append(MonthlyRegistration(month=month_abbr, count=count or 0))
        
    return registrations

async def get_professor_dashboard_stats_service(db: Session, current_user: UserModel) -> ProfessorDashboardStats:
    """
    Récupère les statistiques pour le tableau de bord du professeur connecté.
    """
    professor_id = current_user.id

    published_courses_count = db.query(func.count(CourseModel.id)).filter(
        CourseModel.instructor_id == professor_id,
        CourseModel.status == CourseStatus.published
    ).scalar()

    total_students_count_query = db.query(func.count(Enrollment.user_id.distinct())) \
        .join(CourseModel, Enrollment.course_id == CourseModel.id) \
        .filter(CourseModel.instructor_id == professor_id)
    total_students_count = total_students_count_query.scalar()
    
    average_rating = 0.0  # À calculer plus tard si tu as des retours d’évaluations

    total_questions_count = db.query(func.count(TestQuestionModel.id)) \
        .join(CourseTestModel, TestQuestionModel.test_id == CourseTestModel.id) \
        .join(CourseSectionModel, CourseTestModel.section_id == CourseSectionModel.id) \
        .join(CourseModel, CourseSectionModel.course_id == CourseModel.id) \
        .filter(CourseModel.instructor_id == professor_id) \
        .scalar()

    return ProfessorDashboardStats(
        published_courses_count=published_courses_count or 0,
        total_students_count=total_students_count or 0,
        average_rating=average_rating,
        total_questions_count=total_questions_count or 0
    )

async def get_professor_published_courses_service(db: Session, current_user: UserModel) -> List[CoursePerformance]:
    """
    Récupère les métriques de performance pour les cours publiés par le professeur connecté.
    """
    professor_id = current_user.id
    
    courses = db.query(CourseModel).filter(
        CourseModel.instructor_id == professor_id,
        CourseModel.status == CourseStatus.published
    ).all()

    performance_list = []
    for course in courses:
        students_count = db.query(func.count(Enrollment.user_id.distinct())) \
            .filter(Enrollment.course_id == course.id) \
            .scalar()
        
        rating = 0.0  # À implémenter si tu veux une moyenne des feedbacks
        
        performance_list.append(
            CoursePerformance(
                id=course.id,
                title=course.title,
                students_count=students_count or 0,
                rating=rating,
                last_updated=course.updated_at.isoformat() + "Z" if course.updated_at else datetime.utcnow().isoformat() + "Z"
            )
        )
    return performance_list

async def get_professor_student_engagement_service(db: Session, current_user: UserModel) -> List[StudentEngagement]:
    """
    Récupère les métriques d'engagement des étudiants pour les cours du professeur connecté.
    NOTE: `average_hours_spent` n'est pas traçable avec les modèles actuels.
          Cela nécessiterait un système pour suivre le temps passé par les étudiants.
    """
    professor_id = current_user.id
    courses = db.query(CourseModel.title).filter(
        CourseModel.instructor_id == professor_id,
        CourseModel.status == CourseStatus.published
    ).all()
    
    engagement_list = []
    for course_title_tuple in courses:
        engagement_list.append(
            StudentEngagement(
                course_name=course_title_tuple[0],
                average_hours_spent=0.0 
            )
        )
    return engagement_list 

async def get_professor_student_distribution_service(db: Session, current_user: UserModel) -> StudentDistributionInProfessorCourses:
    """
    Récupère la distribution des étudiants dans les cours du professeur connecté.
    NOTE: Les concepts 'active', 'inactive', 'completed' ne sont pas définis par les modèles actuels.
    """
    professor_id = current_user.id

    active_students_count_query = db.query(func.count(Enrollment.user_id.distinct())) \
        .join(CourseModel, Enrollment.course_id == CourseModel.id) \
        .filter(CourseModel.instructor_id == professor_id)
    
    active_students_count = active_students_count_query.scalar()

    return StudentDistributionInProfessorCourses(
        active_students_count=active_students_count or 0,
        inactive_students_count=0,
        completed_students_count=0
    )

async def get_professor_recent_activities_service(db: Session, current_user: UserModel) -> List[ProfessorRecentActivity]:
    """
    Récupère les activités récentes liées aux cours du professeur connecté.
    NOTE: Un suivi détaillé des activités (questions, commentaires des étudiants) nécessite
          des modèles supplémentaires (par exemple, ActivityLog, StudentQuestion, StudentComment)
          non présents dans le schéma actuel.
    """
    # Le suivi détaillé des activités récentes des étudiants dans les cours d'un professeur
    # (comme les questions posées, les commentaires) nécessiterait des modèles de données supplémentaires
    # qui enregistrent ces interactions, les lient aux étudiants, aux cours, et incluent des timestamps.
    # Par exemple, vous pourriez avoir une table `CourseForumPost` ou `StudentQuestion`.
    # En l'absence de tels modèles, cette fonction retournera une liste vide.
    return []