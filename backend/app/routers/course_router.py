from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas import course as course_schema
from app.schemas import course_section as section_schema
from app.schemas import course_lesson as lesson_schema
from app.schemas import course_test as test_schema
from app.schemas import test_question as question_schema
from app.schemas import user as user_schema
from app.services import course_service
from app.dependencies import auth as auth_deps # Assuming auth_deps provides get_db and get_current_active_user
from app.core.config import settings
from app.models.course import CourseStatus, Course
from app.models.course_section import CourseSection
from app.models.user import User as UserModel
from app.permissions.dependencies import RequirePermission # Assuming this is your permission system
from app.schemas import certificate as certificate_schema
from app.schemas.enrollment import EnrollmentProgress # Added
from app.schemas.course_test import TestSubmissionWithScoreSchema # Added
from datetime import datetime
from sqlalchemy.orm import joinedload

router = APIRouter(prefix=f"{settings.API_V1_STR}/courses", tags=["Courses & Enrollments"])

# --- Course Endpoints ---
@router.post("/", response_model=course_schema.Course, status_code=status.HTTP_201_CREATED)
def create_new_course(
    course_in: course_schema.CourseCreate, # Uses updated course_schema.CourseCreate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_course"))
):
    return course_service.create_course(db=db, course=course_in, instructor_id=current_user.id)

@router.get("/", response_model=List[course_schema.Course], dependencies=[Depends(RequirePermission("view_any_course_listing"))])
def read_all_courses(
    skip: int = 0, limit: int = 20,
    status_filter: Optional[CourseStatus] = Query(CourseStatus.published, alias="status", description="Filter courses by status"),
    sort_by: Optional[str] = Query(None, alias="sortBy"),
    sort_order: Optional[str] = Query("asc", alias="sortOrder"),
    db: Session = Depends(auth_deps.get_db)
):
    return course_service.get_all_courses(db, skip=skip, limit=limit, status=status_filter, sort_by=sort_by, sort_order=sort_order)

@router.get("/{course_id}", response_model=course_schema.Course)
def read_single_course(
    course_id: int, 
    db: Session = Depends(auth_deps.get_db),
    current_user: Optional[UserModel] = Depends(RequirePermission("view_course_detail"))
):
    db_course = course_service.get_course(db, course_id, eager_load_content=True)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    if db_course.status == CourseStatus.draft:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or not accessible")

        is_admin_role = hasattr(current_user, 'role') and current_user.role and current_user.role.name in ["admin", "super_admin"]
        if current_user.id != db_course.instructor_id and not is_admin_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this draft course")

    # 👇 Intégration de la progression identique à la logique fonctionnelle
    progress = None
    if current_user:
        total_lessons = sum(len(section.lessons) for section in db_course.sections)
        completed_lessons = sum(
            1 for section in db_course.sections for lesson in section.lessons if lesson.is_completed
        )
        progress = round((completed_lessons / total_lessons) * 100, 1) if total_lessons else 0.0
        db_course.progress = progress

    return db_course

@router.put("/{course_id}", response_model=course_schema.Course)
def update_existing_course(
    course_id: int, course_in: course_schema.CourseUpdate, # Uses updated course_schema.CourseUpdate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_own_course"))
):
    updated_course = course_service.update_course(db, course_id, course_in, current_user)
    if updated_course == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this course")
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", response_model=course_schema.Course)
def delete_existing_course(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_own_course"))
):
    deleted_course = course_service.delete_course(db, course_id, current_user)
    if deleted_course == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this course")
    if not deleted_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return deleted_course

@router.post("/{course_id}/publish", response_model=course_schema.Course)
def publish_existing_course(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("publish_course"))
):
    published_course = course_service.publish_course(db, course_id, current_user)
    if published_course == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to publish this course")
    if not published_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return published_course

# --- CourseSection Endpoints ---
@router.post("/{course_id}/sections/", response_model=section_schema.CourseSection, status_code=status.HTTP_201_CREATED)
def create_section_for_course(
    course_id: int, section_in: section_schema.CourseSectionCreate, # Uses updated section_schema.CourseSectionCreate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_course_section"))
):
    return course_service.create_course_section(db, section_in, course_id)

@router.get("/{course_id}/sections/", response_model=List[section_schema.CourseSection], dependencies=[Depends(RequirePermission("view_course_sections"))])
def read_sections_for_course(
    course_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(auth_deps.get_db)
):
    return course_service.get_course_sections(db, course_id, skip, limit)

@router.get("/sections/{section_id}", response_model=section_schema.CourseSection, dependencies=[Depends(RequirePermission("view_course_section_detail"))])
def read_single_section(section_id: int, db: Session = Depends(auth_deps.get_db)):
    section = course_service.get_course_section(db, section_id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section

@router.put("/sections/{section_id}", response_model=section_schema.CourseSection)
def update_existing_section(
    section_id: int, section_in: section_schema.CourseSectionUpdate, # Uses updated section_schema.CourseSectionUpdate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_course_section"))
):
    updated_section = course_service.update_course_section(db, section_id, section_in)
    if updated_section == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this section")
    if not updated_section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return updated_section

@router.delete("/sections/{section_id}", response_model=section_schema.CourseSection)
def delete_existing_section(
    section_id: int, db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_course_section"))
):
    deleted_section = course_service.delete_course_section(db, section_id)
    if deleted_section == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this section")
    if not deleted_section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found for deletion")
    return deleted_section

# --- CourseLesson Endpoints ---
@router.post("/sections/{section_id}/lessons/", response_model=lesson_schema.CourseLesson, status_code=status.HTTP_201_CREATED)
def create_lesson_for_section(
    section_id: int, lesson_in: lesson_schema.CourseLessonCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_course_lesson"))
):
    return course_service.create_course_lesson(db, lesson_in, section_id)

@router.get("/sections/{section_id}/lessons/", response_model=List[lesson_schema.CourseLesson], dependencies=[Depends(RequirePermission("view_course_lessons"))])
def read_lessons_for_section(
    section_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(auth_deps.get_db)
):
    return course_service.get_course_lessons(db, section_id, skip, limit)

@router.get("/lessons/{lesson_id}", response_model=lesson_schema.CourseLesson, dependencies=[Depends(RequirePermission("view_course_lesson_detail"))])
def read_single_lesson(lesson_id: int, db: Session = Depends(auth_deps.get_db)):
    lesson = course_service.get_course_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson

@router.put("/lessons/{lesson_id}", response_model=lesson_schema.CourseLesson)
def update_existing_lesson(
    lesson_id: int, lesson_in: lesson_schema.CourseLessonUpdate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_course_lesson"))
):
    updated_lesson = course_service.update_course_lesson(db, lesson_id, lesson_in)
    if not updated_lesson: # Assuming service returns None if not found, or specific error object/string
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    # Add authorization check if service returns "NotAuthorized" or similar
    return updated_lesson

@router.delete("/lessons/{lesson_id}", response_model=lesson_schema.CourseLesson)
def delete_existing_lesson(
    lesson_id: int, db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_course_lesson"))
):
    deleted_lesson = course_service.delete_course_lesson(db, lesson_id)
    # Add "NotAuthorized" check if applicable from service
    if not deleted_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found for deletion")
    return deleted_lesson

# --- CourseTest Endpoints ---
@router.post("/sections/{section_id}/tests/", response_model=test_schema.CourseTest, status_code=status.HTTP_201_CREATED)
def create_test_for_section(
    section_id: int, test_in: test_schema.CourseTestCreate, # Uses updated test_schema.CourseTestCreate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_course_test"))
):
    return course_service.create_course_test(db, test_in, section_id)

@router.get("/tests/{test_id}", response_model=dict, dependencies=[Depends(RequirePermission("view_course_test"))])
def read_single_test(test_id: int, db: Session = Depends(auth_deps.get_db)):
    test = course_service.get_course_test(db, test_id)
    return test_schema.CourseTest(
        id=test.id,
        title=test.title,
        description=test.description,
        section_id=test.section_id,
        duration_minutes=test.duration_minutes,
        passing_score=test.passing_score,
        max_attempts=test.max_attempts,
        questions=[
            question_schema.TestQuestionBase(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                points=q.points,
                correct_answer_data=q.correct_answer_data,
            )
            for q in test.questions
        ] if test.questions else []
    ).dict() if test else {}

@router.get("/sections/{section_id}/tests", response_model=dict, dependencies=[Depends(RequirePermission("view_course_test"))])
def read_tests_for_section(section_id: int, db: Session = Depends(auth_deps.get_db)):
    test = course_service.get_course_test_for_section(db, section_id)
    return test_schema.CourseTest(
        id=test.id,
        title=test.title,
        description=test.description,
        section_id=test.section_id,
        duration_minutes=test.duration_minutes,
        passing_score=test.passing_score,
        max_attempts=test.max_attempts,
        questions=[
            question_schema.TestQuestionBase(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                points=q.points,
                correct_answer_data=q.correct_answer_data,
            )
            for q in test.questions
        ] if test.questions else []
    ).dict() if test else {}

@router.put("/tests/{test_id}", response_model=test_schema.CourseTest)
def update_existing_test(
    test_id: int, test_in: test_schema.CourseTestUpdate, # Uses updated test_schema.CourseTestUpdate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_course_test"))
):
    updated_test = course_service.update_course_test(db, test_id, test_in)
    if updated_test == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if not updated_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return updated_test

@router.delete("/tests/{test_id}", response_model=test_schema.CourseTest)
def delete_existing_test(
    test_id: int, db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_course_test"))
):
    deleted_test = course_service.delete_course_test(db, test_id)
    if deleted_test == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if not deleted_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found for deletion")
    return deleted_test

# --- TestQuestion Endpoints ---
@router.post("/tests/{test_id}/questions/", response_model=question_schema.TestQuestion, status_code=status.HTTP_201_CREATED)
def create_question_for_test(
    test_id: int, question_in: question_schema.TestQuestionCreate, # Uses updated question_schema.TestQuestionCreate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("create_test_question"))
):
    return course_service.create_test_question(db, question_in, test_id)

@router.get("/tests/{test_id}/questions/", response_model=List[question_schema.TestQuestion], dependencies=[Depends(RequirePermission("view_test_questions"))])
def read_questions_for_test(
    test_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(auth_deps.get_db)
):
    return course_service.get_test_questions(db, test_id, skip, limit)

@router.get("/questions/{question_id}", response_model=question_schema.TestQuestion, dependencies=[Depends(RequirePermission("view_test_questions"))])
def read_single_question(question_id: int, db: Session = Depends(auth_deps.get_db)):
    question = course_service.get_test_question(db, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question

@router.put("/questions/{question_id}", response_model=question_schema.TestQuestion)
def update_existing_question(
    question_id: int, question_in: question_schema.TestQuestionUpdate, # Uses updated question_schema.TestQuestionUpdate
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("edit_test_question"))
):
    updated_question = course_service.update_test_question(db, question_id, question_in)
    if updated_question == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if not updated_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return updated_question

@router.delete("/questions/{question_id}", response_model=question_schema.TestQuestion)
def delete_existing_question(
    question_id: int, db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("delete_test_question"))
):
    deleted_question = course_service.delete_test_question(db, question_id)
    if deleted_question == "NotAuthorized":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if not deleted_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found for deletion")
    return deleted_question

# --- Enrollment Endpoints ---
@router.post("/{course_id}/enroll", response_model=user_schema.User) 
def enroll_in_course(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("enroll_in_course"))
):
    result = course_service.enroll_student_in_course(db, course_id, current_user.id)
    if result == "NotFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course or user not found")
    if result == "AlreadyEnrolled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already enrolled in this course")
    if result == "CourseNotPublished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is not published")
    if isinstance(result, str) and result not in ["NotFound", "AlreadyEnrolled", "CourseNotPublished"]:
        # Catch other service error strings
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not enroll in course: {result}")
    if not isinstance(result, UserModel) and result not in [current_user]: # If service returns Course model on success
         # This path might be hit if service returns the course model on success, adjust as needed
         pass # Or return a specific user schema if that's the contract
    return current_user # Assuming current_user is the enrolled user to be returned

@router.post("/{course_id}/unenroll", response_model=user_schema.User)
def unenroll_from_course(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("unenroll_from_course"))
):
    result = course_service.unenroll_student_from_course(db, course_id, current_user.id)
    if result == "NotFound":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course or user not found")
    if result == "NotEnrolled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not enrolled in this course")
    if isinstance(result, str) and result not in ["NotFound", "NotEnrolled"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not unenroll from course: {result}")
    return current_user

@router.get("/me/enrolled", response_model=List[course_schema.Course])
def get_my_enrolled_courses(
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_own_enrolled_courses")),
    skip: int = 0, limit: int = 20
):
    return course_service.get_user_enrolled_courses(db, current_user.id, skip, limit)

@router.get("/instructor/me", response_model=List[course_schema.Course])
def get_my_instructed_courses(
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(RequirePermission("view_own_instructed_courses")), 
    skip: int = 0, limit: int = 20
):
    return course_service.get_course_instructor_courses(db, current_user.id, skip, limit)

# --- Certificate Endpoints ---
@router.post(
    "/{course_id}/users/{user_id}/certificates/", # Path was /courses/{course_id}/... in original, assuming prefix makes it /courses/{course_id}/users/...
    response_model=certificate_schema.Certificate,
    status_code=status.HTTP_201_CREATED,
    summary="Create a certificate for a user for a given course",
    dependencies=[Depends(RequirePermission("issue_certificate"))]
)
def create_user_course_certificate(
    course_id: int,
    user_id: int,
    # certificate_in: certificate_schema.CertificateCreate, # Payload is minimal or auto-generated
    db: Session = Depends(auth_deps.get_db),
    # current_user: UserModel = Depends(auth_deps.get_current_active_user) # For checking issuer permission
):
    course = course_service.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    target_user = db.query(UserModel).filter(UserModel.id == user_id).first() # Basic user fetch
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    # Service create_certificate might check course.points_required_for_certificate
    # and student's actual points/completion before issuing.
    # For now, router passes basic info.
    certificate_create_payload = certificate_schema.CertificateCreate(
        course_id=course_id,
        user_id=user_id,
        issue_date=datetime.utcnow(),
        # certificate_url and verification_code are likely generated by the service or passed if fixed
    )

    new_certificate = course_service.create_certificate(db=db, certificate_in=certificate_create_payload)
    if not new_certificate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create certificate. It may already exist or input is invalid.")
    return new_certificate

@router.get(
    "/users/{user_id}/certificates/", # Path relative to /courses prefix might be /courses/users/...
    response_model=List[certificate_schema.CertificateDisplay],
    summary="Get all certificates for a specific user"
)
def read_user_certificates(
    user_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user), # User for auth check
    skip: int = 0,
    limit: int = 20
):
    # Basic auth: user can see their own, or admin can see anyone's.
    # This should ideally be encapsulated in RequirePermission.
    is_admin_role = hasattr(current_user, 'role') and current_user.role and current_user.role.name in ["admin", "super_admin"]
    if current_user.id != user_id and not is_admin_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these certificates")

    certificates = course_service.get_certificates_for_user(db, user_id=user_id, skip=skip, limit=limit)
    return certificates

@router.get(
    "/certificates/{certificate_id}", # Path relative to /courses prefix
    response_model=certificate_schema.Certificate,
    summary="Get a specific certificate by its ID",
    dependencies=[Depends(RequirePermission("view_certificate_detail"))]
)
def read_single_certificate(
    certificate_id: int,
    db: Session = Depends(auth_deps.get_db)
    # current_user: UserModel = Depends(auth_deps.get_current_active_user) # If auth needed
):
    certificate = course_service.get_certificate_by_id(db, certificate_id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    # Add auth here if needed, e.g., current_user.id == certificate.user_id or admin
    return certificate

@router.get("/{course_id}/me/progress", response_model=EnrollmentProgress)
def get_my_course_progress(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    enrollment = course_service.get_enrollment(db, user_id=current_user.id, course_id=course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course or course not found.")

    course = db.query(Course).options(
        joinedload(Course.sections).joinedload(CourseSection.lessons)
    ).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    total_lessons = sum(len(section.lessons) for section in course.sections)
    completed_lesson_ids = [
        lesson.id
        for section in course.sections
        for lesson in section.lessons
        if lesson.is_completed
    ]

    progress = round((len(completed_lesson_ids) / total_lessons) * 100, 1) if total_lessons else 0.0

    # Facultatif : mise à jour de l'enrollment
    enrollment.progress_percentage = progress
    enrollment.completed_lessons = completed_lesson_ids
    db.commit()

    return EnrollmentProgress(
        user_id=enrollment.user_id,
        course_id=enrollment.course_id,
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at,
        progress_percentage=progress,
        completed_lessons=completed_lesson_ids,
        completed_sections=enrollment.completed_sections or [],
        test_attempts=enrollment.test_attempts or [],
        test_scores=enrollment.test_scores or [],
    )

@router.post("/{course_id}/lessons/{lesson_id}/complete", response_model=EnrollmentProgress)
def mark_lesson_as_completed(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    # RequirePermission("complete_lesson") could be added if such a permission exists
    enrollment = course_service.mark_lesson_completed(db, user_id=current_user.id, course_id=course_id, lesson_id=lesson_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found or lesson already completed.")
    return enrollment

@router.post("/{course_id}/sections/{section_id}/complete", response_model=EnrollmentProgress)
def mark_section_as_completed(
    course_id: int,
    section_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    # RequirePermission("complete_section")
    enrollment = course_service.mark_section_completed(db, user_id=current_user.id, course_id=course_id, section_id=section_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found or section already completed.")
    return enrollment

@router.post("/{course_id}/tests/{test_id}/attempt", response_model=EnrollmentProgress)
def submit_course_test_attempt(
    course_id: int,
    test_id: int,
    submission: TestSubmissionWithScoreSchema, # Using the schema that includes score and passed status
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    # RequirePermission("attempt_test")
    # Here, we are directly calling record_test_attempt which expects score, passed, and questions_summary.
    # This implies the client or this endpoint (if it had more logic) calculates these.
    # A more robust solution would be for the service layer to calculate score/passed from raw answers.

    # Basic check: Ensure user is enrolled. get_enrollment can do this.
    enrollment_check = course_service.get_enrollment(db, user_id=current_user.id, course_id=course_id)
    if not enrollment_check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not enrolled in this course.")

    # TODO: Add check for course_test.max_attempts if applicable, ideally in service layer.

    updated_enrollment = course_service.record_test_attempt(
        db=db,
        user_id=current_user.id,
        course_id=course_id,
        test_id=test_id,
        score=submission.score,
        passed=submission.passed,
        questions_summary= [s.dict() for s in submission.questions_summary] if submission.questions_summary else [],
        attempted_at=datetime.utcnow()
    )
    if not updated_enrollment:
        # This might happen if get_enrollment inside record_test_attempt fails after the initial check.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to record test attempt. Enrollment issue.")
    return updated_enrollment

@router.post("/{course_id}/me/check-certificate", response_model=Optional[certificate_schema.CertificateDisplay])
def check_and_try_issue_certificate(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    # RequirePermission("request_certificate_issuance")
    result = course_service.check_and_issue_certificate(db, user_id=current_user.id, course_id=course_id)

    if isinstance(result, str):
        if result == "EnrollmentNotFound":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not enrolled in this course.")
        if result == "CourseNotFound":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
        if result == "CertificateAlreadyIssued":
            # Not an error, just return a message or the existing certificate?
            # For now, let's try to fetch and return it.
            existing_cert = course_service.get_certificate_for_course_by_user(db, user_id=current_user.id, course_id=course_id)
            if existing_cert: return existing_cert
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result) # Should not happen if cert exists
        if result == "NotAllLessonsCompleted" or \
           result == "NotAllSectionsCompleted" or \
           result.startswith("PointsNotMet"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Certificate requirements not met: {result}")
        if result == "CertificateCreationError":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create certificate due to an internal error.")
        # Default for other string messages from service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

    if not result: # Should be caught by string checks, but as a fallback
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate requirements not met or already issued and not found.")

    return result # This is the new certificate_model.Certificate object

@router.get(
    "/{course_id}/certificate", # Path relative to /courses prefix
    response_model=Optional[certificate_schema.CertificateDisplay],
    summary="Get the current user's certificate for a specific course",
    dependencies=[Depends(RequirePermission("view_own_course_certificate"))]
)
def read_my_certificate_for_course(
    course_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user)
):
    course = course_service.get_course(db, course_id) # Check course existence
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    certificate = course_service.get_certificate_for_course_by_user(db, user_id=current_user.id, course_id=course_id)
    if not certificate: # Not an error to not have one, returns 200 with null body
        return None
    return certificate
