from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.auth import get_db
from app.dependencies.auth import require_professor
from app.services import professor_service, auth_service as user_service
from app.services import professor_service as dashboard_services
from app.dependencies import auth as auth_deps
from app.schemas import professor as professor_schema
from app.schemas import user as user_schema
from app.schemas import course as course_schema
from app.permissions.dependencies import RequirePermission
from app.core.config import settings
from app.models.user import User as UserModel
from app.permissions.models import UserRoleEnum

# Import Admin Dashboard Schemas
from app.schemas.professor import (
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

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/professors",
    tags=["Professor Profiles"]
)

# New router for Admin Dashboard (from previous step)
admin_dashboard_router = APIRouter(
    prefix=f"{settings.API_V1_STR}/admin/dashboard",
    tags=["Admin Dashboard"],
    dependencies=[Depends(auth_deps.require_admin)]
)


@admin_dashboard_router.get("/stats", response_model=AdminDashboardStats, summary="Get Admin Dashboard Statistics")
async def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin)
):
    """
    Retrieve overall statistics for the admin dashboard.
    - **total_users**: Total number of users.
    - **total_professors**: Total number of professors.
    - **total_courses**: Total number of courses.
    - **new_enrollments_last_month**: New course enrollments in the past month.
    """
    return await dashboard_services.get_admin_dashboard_stats_service(db=db)

@admin_dashboard_router.get("/professors", response_model=List[ProfessorStats], summary="Get List of Professor Statistics")
async def get_admin_dashboard_professors(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin)
):
    """
    Retrieve a list of statistics for all professors.
    - **id**: Professor's unique identifier.
    - **name**: Professor's full name.
    - **email**: Professor's email.
    - **courses_count**: Number of courses taught.
    - **students_count**: Total students across their courses.
    - **average_rating**: Average rating of their courses.
    """
    return await dashboard_services.get_admin_professors_service(db=db)


@admin_dashboard_router.get(
    "/professors/{professor_id}/courses",
    response_model=List[course_schema.Course],
    summary="Get Courses of a Professor",
)
async def get_admin_professor_courses(
    professor_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin),
):
    """
    Retrieve all courses created by a specific professor.
    """
    return dashboard_services.get_professor_courses_for_admin(
        db=db,
        professor_id=professor_id,
        skip=skip,
        limit=limit,
    )

@admin_dashboard_router.get("/recent-activities", response_model=List[RecentActivity], summary="Get Recent Activities")
async def get_admin_dashboard_recent_activities(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin)
):
    """
    Retrieve a list of recent activities across the platform.
    - **id**: Activity log entry ID.
    - **user_name**: Name of the user performing the action.
    - **action**: Description of the action.
    - **resource_name**: Name of the resource involved.
    - **timestamp**: Time of activity.
    """
    return await dashboard_services.get_admin_recent_activities_service(db=db)

@admin_dashboard_router.get("/user-distribution", response_model=UserDistribution, summary="Get User Distribution")
async def get_admin_dashboard_user_distribution(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin)
):
    """
    Retrieve the distribution of users by role.
    - **students_count**: Total number of students.
    - **professors_count**: Total number of professors.
    - **admins_count**: Total number of administrators.
    """
    return await dashboard_services.get_admin_user_distribution_service(db=db)

@admin_dashboard_router.get("/monthly-registrations", response_model=List[MonthlyRegistration], summary="Get Monthly User Registrations")
async def get_admin_dashboard_monthly_registrations(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(auth_deps.require_admin)
):
    """
    Retrieve the number of new user registrations per month.
    - **month**: Month (e.g., "Jan", "Feb").
    - **count**: Number of registrations.
    """
    return await dashboard_services.get_admin_monthly_registrations_service(db=db)


MANAGE_PROFESSOR_PROFILES = "manage_professor_profiles"
VIEW_ANY_USER_PROFILE_DETAIL = "view_any_user_profile_detail"

@router.post(
    "/", 
    response_model=user_schema.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Professor (User and Profile)",
)
def create_new_professor_endpoint(
    payload: user_schema.ProfessorUserAndProfileCreate, 
    db: Session = Depends(get_db),
):
    """
    Crée un nouvel utilisateur avec le rôle 'professeur' et son profil associé.
    La charge utile `payload` contient tous les champs nécessaires (utilisateur et profil)
    au même niveau.
    """
    try:
        # Le service gère la création de l'utilisateur et du profil
        professor_user = user_service.create_professor_user_and_profile(db=db, payload=payload)
        return professor_user
    except HTTPException as e:
        raise e # Re-lever les exceptions HTTP connues du service
    except Exception as e:
        # Loggez l'erreur 'e' ici pour le débogage
        print(f"Unexpected error creating professor: {e}") # Pour le débogage
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur inattendue est survenue lors de la création du professeur."
        )

@router.post(
    "/{user_id}/profile", 
    response_model=professor_schema.ProfessorProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Add a Professor Profile to an Existing User",
)
def add_professor_profile_to_user_endpoint(
    user_id: int,
    profile_in: professor_schema.ProfessorProfileCreateForExistingUser,
    db: Session = Depends(get_db),
):
    """
    Ajoute un profil de professeur à un utilisateur existant qui n'en a pas encore.
    `user_id` est fourni dans le chemin.
    `profile_in` contient les données du profil à créer.
    """
    profile = professor_service.add_profile_to_existing_user(db=db, user_id=user_id, profile_in=profile_in)
    return profile

@router.put(
    "/{user_id}/profile",
    response_model=professor_schema.ProfessorProfile,
    summary="Update a Professor's Profile",
)
def update_professor_profile_data_endpoint(
    user_id: int,
    profile_in: professor_schema.ProfessorProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Met à jour les informations du profil d'un professeur existant.
    Les détails de l'utilisateur (nom, email) ne sont pas mis à jour ici.
    Seuls les champs fournis dans `profile_in` seront mis à jour.
    """
    updated_profile = professor_service.update_professor_profile(
        db=db, user_id=user_id, profile_in=profile_in
    )
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil de professeur non trouvé pour cet utilisateur, mise à jour impossible.",
        )
    return updated_profile

@router.get(
    "/{user_id}",
    response_model=user_schema.User, 
    summary="Get a Professor's User and Profile details",
)
def get_professor_details_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupère les informations de l'utilisateur et le profil de professeur associé
    pour un ID d'utilisateur donné.
    """
    user = user_service.get_user_with_profile(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professeur (Utilisateur) non trouvé.")

    return user


@router.put("/{user_id}/professor-profile", response_model=professor_schema.ProfessorProfile)
def update_professor_profile_endpoint(
    user_id: int,
    profile_in: professor_schema.ProfessorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(RequirePermission(MANAGE_PROFESSOR_PROFILES))
):

    updated_profile = professor_service.update_professor_profile(
        db=db, user_id=user_id, profile_in=profile_in
    )
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor profile not found for this user, cannot update.",
        )
    return updated_profile

@router.get("/{user_id}/professor-profile", response_model=professor_schema.ProfessorProfile)
def read_professor_profile_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(RequirePermission(VIEW_ANY_USER_PROFILE_DETAIL))
):
    profile = professor_service.get_professor_profile_by_user_id(db=db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor profile not found for this user.",
        )
    return profile

@router.delete("/{user_id}/professor-profile", response_model=professor_schema.ProfessorProfile) # Or a different response model
def delete_professor_profile_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(RequirePermission(MANAGE_PROFESSOR_PROFILES))
):
    deleted_profile = professor_service.delete_professor_profile(db=db, user_id=user_id)
    if not deleted_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor profile not found for this user, cannot delete.",
        )
    return deleted_profile


# --- Professor Dashboard Routes ---

PROFESSOR_DASHBOARD_TAG = "Professor Dashboard"

@router.get("/dashboard/stats", response_model=ProfessorDashboardStats, tags=[PROFESSOR_DASHBOARD_TAG], summary="Get Professor Dashboard Statistics")
async def get_professor_dashboard_stats(
    db: Session = Depends(get_db),
    current_professor: UserModel = Depends(require_professor)
):
    """
    Retrieve statistics for the logged-in professor's dashboard.
    - **published_courses_count**: Number of published courses.
    - **total_students_count**: Total students across all courses.
    - **average_rating**: Average rating of professor's courses.
    - **total_questions_count**: Total questions in professor's courses.
    """
    return await dashboard_services.get_professor_dashboard_stats_service(db=db, current_user=current_professor)

@router.get("/dashboard/published-courses", response_model=List[CoursePerformance], tags=[PROFESSOR_DASHBOARD_TAG], summary="Get Professor's Published Courses Performance")
async def get_professor_published_courses(
    db: Session = Depends(get_db),
    current_professor: UserModel = Depends(require_professor)
):
    """
    Retrieve performance metrics for courses published by the logged-in professor.
    - **id**: Course ID.
    - **title**: Course title.
    - **students_count**: Number of students enrolled.
    - **rating**: Average rating of the course.
    - **last_updated**: Last update timestamp.
    """
    return await dashboard_services.get_professor_published_courses_service(db=db, current_user=current_professor)

@router.get("/dashboard/student-engagement", response_model=List[StudentEngagement], tags=[PROFESSOR_DASHBOARD_TAG], summary="Get Student Engagement Metrics")
async def get_professor_student_engagement(
    db: Session = Depends(get_db),
    current_professor: UserModel = Depends(require_professor)
):
    """
    Retrieve student engagement metrics for the logged-in professor's courses.
    - **course_name**: Name of the course.
    - **average_hours_spent**: Average hours students spent on the course.
    """
    return await dashboard_services.get_professor_student_engagement_service(db=db, current_user=current_professor)

@router.get("/dashboard/student-distribution", response_model=StudentDistributionInProfessorCourses, tags=[PROFESSOR_DASHBOARD_TAG], summary="Get Student Distribution in Courses")
async def get_professor_student_distribution(
    db: Session = Depends(get_db),
    current_professor: UserModel = Depends(require_professor)
):
    """
    Retrieve the distribution of students (active, inactive, completed) in the logged-in professor's courses.
    - **active_students_count**: Number of active students.
    - **inactive_students_count**: Number of inactive students.
    - **completed_students_count**: Number of students who completed courses.
    """
    return await dashboard_services.get_professor_student_distribution_service(db=db, current_user=current_professor)

@router.get("/dashboard/recent-activities", response_model=List[ProfessorRecentActivity], tags=[PROFESSOR_DASHBOARD_TAG], summary="Get Recent Activities in Professor's Courses")
async def get_professor_recent_activities(
    db: Session = Depends(get_db),
    current_professor: UserModel = Depends(require_professor)
):
    """
    Retrieve recent activities (questions, comments) related to the logged-in professor's courses.
    - **id**: Activity ID.
    - **student_name**: Name of the student.
    - **course_name**: Name of the course.
    - **activity_type**: Type of activity ("question" or "comment").
    - **content**: Content of the activity.
    - **timestamp**: Timestamp of the activity.
    """
    return await dashboard_services.get_professor_recent_activities_service(db=db, current_user=current_professor)
