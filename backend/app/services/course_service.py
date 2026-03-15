from typing import Optional, List, Union
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models import course as course_model
from app.models import course_section as course_section_model
from app.models import course_lesson
from app.models import course_test
from app.models import test_question as test_question_model
from app.models import user as user_model
from app.models import certificate as certificate_model
from app.models.enrollments import Enrollment as enrollment_model

from app.schemas import course as course_schema
from app.schemas import course_section as section_schema
from app.schemas import course_lesson as lesson_schema
from app.schemas import course_test as test_schema
from app.schemas import test_question as question_schema
from app.schemas import certificate as certificate_schema

from app.models.course_section import CourseSectionType # UPDATED IMPORT
from app.models.test_question import QuestionType

from datetime import datetime

# Course CRUD (functions: create_course, get_course, get_all_courses, update_course, delete_course, publish_course)
# These functions are not directly affected by CourseSectionType renaming, so they remain as they were.
# For brevity, I'll include only the affected functions and stubs for the others.

def create_course(db: Session, course: course_schema.CourseCreate, instructor_id: int) -> course_model.Course:
    db_course = course_model.Course(
        **course.dict(exclude={"points_required_for_certificate"}),
        instructor_id=instructor_id,
        points_required_for_certificate=course.points_required_for_certificate
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course(db: Session, course_id: int, eager_load_content: bool = False) -> Optional[course_model.Course]:
    query = db.query(course_model.Course)
    if eager_load_content:
        query = query.options(
            selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.lessons),
            selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.test).selectinload(course_test.CourseTest.questions)
        )
    return query.filter(course_model.Course.id == course_id).first()

def get_all_courses(db: Session, skip: int = 0, limit: int = 100, status: Optional[course_model.CourseStatus] = course_model.CourseStatus.published, sort_by: Optional[str] = None, sort_order: Optional[str] = "asc") -> List[course_model.Course]:
    query = db.query(course_model.Course)
    if status:
        query = query.filter(course_model.Course.status == status)

    if sort_by == "created_at":
        if sort_order == "desc":
            query = query.order_by(course_model.Course.created_at.desc())
        else:
            query = query.order_by(course_model.Course.created_at.asc())
    # Add other sortable fields here if needed

    return query.offset(skip).limit(limit).all()

def update_course(db: Session, course_id: int, course_update: course_schema.CourseUpdate, current_user: user_model.User) -> Optional[Union[course_model.Course, str]]:
    db_course = get_course(db, course_id)
    if not db_course:
        return None
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int, current_user: user_model.User) -> Optional[Union[course_model.Course, str]]:
    # Implementation from previous step
    db_course = get_course(db, course_id)
    if not db_course: return None
    # Add authorization logic here
    db.delete(db_course)
    db.commit()
    return db_course


def publish_course(db: Session, course_id: int, current_user: user_model.User) -> Optional[Union[course_model.Course, str]]:
    # Implementation from previous step
    db_course = get_course(db, course_id)
    if not db_course: return None
    # Add authorization logic here
    db_course.status = course_model.CourseStatus.published
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# CourseSection CRUD
def create_course_section(db: Session, section_in: section_schema.CourseSectionCreate, course_id: int) -> course_section_model.CourseSection:
    section_data_dict = section_in.dict(exclude={"test"})

    db_section = course_section_model.CourseSection(**section_data_dict, course_id=course_id)

    # Use CourseSectionType for comparisons
    if db_section.content_type == CourseSectionType.VIDEO:
        db_section.text_content = None
    elif db_section.content_type == CourseSectionType.TEXT:
        db_section.video_url = None
    elif db_section.content_type == CourseSectionType.QUIZ:
        db_section.video_url = None
        db_section.text_content = None

    db.add(db_section)
    db.commit()
    db.refresh(db_section)

    if db_section.content_type == CourseSectionType.QUIZ and section_in.test: # Use CourseSectionType
        create_course_test(db=db, test_data=section_in.test, section_id=db_section.id)
        db.refresh(db_section)

    return db_section

def get_course_section(db: Session, section_id: int) -> Optional[course_section_model.CourseSection]:
    return db.query(course_section_model.CourseSection).filter(course_section_model.CourseSection.id == section_id).options(selectinload(course_section_model.CourseSection.test)).first()

def get_course_sections(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[course_section_model.CourseSection]:
    return db.query(course_section_model.CourseSection).filter(course_section_model.CourseSection.course_id == course_id).order_by(course_section_model.CourseSection.order).offset(skip).limit(limit).all()

def update_course_section(db: Session, section_id: int, section_update: section_schema.CourseSectionUpdate) -> Optional[course_section_model.CourseSection]:
    db_section = get_course_section(db, section_id)
    if not db_section: return None

    update_payload = section_update.dict(exclude_unset=True, exclude={"test"})

    new_content_type = update_payload.get("content_type", db_section.content_type)
    # Ensure new_content_type is CourseSectionType enum member if coming from string payload
    if isinstance(new_content_type, str):
        new_content_type = CourseSectionType(new_content_type)


    if "content_type" in update_payload and db_section.content_type != new_content_type:
        # Use CourseSectionType for comparisons
        if db_section.content_type == CourseSectionType.VIDEO:
            db_section.video_url = None
        elif db_section.content_type == CourseSectionType.TEXT:
            db_section.text_content = None
        elif db_section.content_type == CourseSectionType.QUIZ:
            if db_section.test:
                delete_course_test(db, db_section.test.id)
                db_section.test = None

    for field_name, field_value in update_payload.items():
        setattr(db_section, field_name, field_value)

    # Use CourseSectionType for comparisons
    if new_content_type == CourseSectionType.VIDEO:
        if "text_content" not in update_payload: db_section.text_content = None
        if db_section.test and new_content_type != CourseSectionType.QUIZ:
             delete_course_test(db, db_section.test.id)
             db_section.test = None
    elif new_content_type == CourseSectionType.TEXT:
        if "video_url" not in update_payload: db_section.video_url = None
        if db_section.test and new_content_type != CourseSectionType.QUIZ:
             delete_course_test(db, db_section.test.id)
             db_section.test = None
    elif new_content_type == CourseSectionType.QUIZ:
        if "video_url" not in update_payload: db_section.video_url = None
        if "text_content" not in update_payload: db_section.text_content = None

        if section_update.test is not None:
            if db_section.test:
                update_course_test(db, db_section.test.id, section_update.test)
            else:
                try:
                    test_create_payload = test_schema.CourseTestCreate(**section_update.test.dict(exclude_unset=True))
                    create_course_test(db, test_create_payload, section_id=db_section.id)
                except Exception as e:
                    pass # Error handling for creating test from update payload

    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def delete_course_section(db: Session, section_id: int) -> Optional[course_section_model.CourseSection]:
    # Implementation from previous step
    db_section = get_course_section(db, section_id)
    if not db_section: return None
    db.delete(db_section)
    db.commit()
    return db_section

# CourseLesson CRUD (Unaffected by CourseSectionType rename, kept for completeness)
def create_course_lesson(db: Session, lesson: lesson_schema.CourseLessonCreate, section_id: int) -> course_lesson.CourseLesson:
    db_lesson = course_lesson.CourseLesson(**lesson.dict(exclude_unset=True), section_id=section_id)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

def get_course_lesson(db: Session, lesson_id: int) -> Optional[course_lesson.CourseLesson]:
    return db.query(course_lesson.CourseLesson).filter(course_lesson.CourseLesson.id == lesson_id).first()

def get_course_lessons(db: Session, section_id: int, skip: int = 0, limit: int = 100) -> List[course_lesson.CourseLesson]:
    return db.query(course_lesson.CourseLesson).filter(course_lesson.CourseLesson.section_id == section_id).order_by(course_lesson.CourseLesson.order).offset(skip).limit(limit).all()

def update_course_lesson(db: Session, lesson_id: int, lesson_update: lesson_schema.CourseLessonUpdate) -> Optional[course_lesson.CourseLesson]:
    db_lesson = get_course_lesson(db, lesson_id)
    if not db_lesson: return None
    update_data = lesson_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lesson, field, value)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

def delete_course_lesson(db: Session, lesson_id: int) -> Optional[course_lesson.CourseLesson]:
    db_lesson = get_course_lesson(db, lesson_id)
    if not db_lesson: return None
    db.delete(db_lesson)
    db.commit()
    return db_lesson

# CourseTest CRUD (Unaffected by CourseSectionType rename, kept for completeness)
# TestQuestion CRUD uses QuestionType, which is distinct and unchanged.
def create_course_test(db: Session, test_data: test_schema.CourseTestCreate, section_id: Optional[int]) -> course_test.CourseTest:
    test_model_data = test_data.dict(exclude={"questions"})
    db_test_obj = course_test.CourseTest(**test_model_data, section_id=section_id)
    db.add(db_test_obj)
    db.commit()
    db.refresh(db_test_obj)

    if test_data.questions:
        for q_data in test_data.questions:
            create_test_question(db=db, question_data=q_data, test_id=db_test_obj.id)

    db.refresh(db_test_obj)
    return db_test_obj

def get_course_test(db: Session, test_id: int) -> Optional[course_test.CourseTest]:
    return db.query(course_test.CourseTest).filter(course_test.CourseTest.id == test_id).options(selectinload(course_test.CourseTest.questions)).first()

def get_course_test_for_section(db: Session, section_id: int) -> Optional[course_test.CourseTest]:
    return db.query(course_test.CourseTest).filter(course_test.CourseTest.section_id == section_id).first()

def update_course_test(db: Session, test_id: int, test_update: test_schema.CourseTestUpdate) -> Optional[course_test.CourseTest]:
    db_test_obj = get_course_test(db, test_id)
    if not db_test_obj: return None

    update_data = test_update.dict(exclude_unset=True, exclude={"questions"})
    for field, value in update_data.items():
        setattr(db_test_obj, field, value)

    if test_update.questions is not None:
        for existing_q in db_test_obj.questions:
            db.delete(existing_q)
        # db_test_obj.questions = [] # Clearing collection might not be needed if cascade handles it.
                                   # Or if questions are managed through their own service calls.

        for q_create_data in test_update.questions:
            create_test_question(db, question_data=q_create_data, test_id=db_test_obj.id)

    db.add(db_test_obj)
    db.commit()
    db.refresh(db_test_obj)
    return db_test_obj

def delete_course_test(db: Session, test_id: int) -> Optional[course_test.CourseTest]:
    db_test_obj = get_course_test(db, test_id)
    if not db_test_obj: return None
    db.delete(db_test_obj)
    db.commit()
    return db_test_obj

# TestQuestion CRUD (Unaffected by CourseSectionType rename)
def create_test_question(db: Session, question_data: question_schema.TestQuestionCreate, test_id: int) -> test_question_model.TestQuestion:
    options_as_json_list = None
    if question_data.options:
        options_as_json_list = [opt.dict() for opt in question_data.options]

    derived_correct_answer_data = None
    if question_data.question_type == QuestionType.MULTIPLE_CHOICE and question_data.options:
        correct_options_list = [opt.dict() for opt in question_data.options if opt.is_correct]
        if correct_options_list:
            derived_correct_answer_data = correct_options_list

    db_question = test_question_model.TestQuestion(
        test_id=test_id,
        question_text=question_data.question_text,
        points=question_data.points,
        question_type=question_data.question_type,
        options=options_as_json_list,
        correct_answer_data=derived_correct_answer_data
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_test_question(db: Session, question_id: int) -> Optional[test_question_model.TestQuestion]:
    return db.query(test_question_model.TestQuestion).filter(test_question_model.TestQuestion.id == question_id).first()

def get_test_questions(db: Session, test_id: int, skip: int = 0, limit: int = 100) -> List[test_question_model.TestQuestion]:
    return db.query(test_question_model.TestQuestion).filter(test_question_model.TestQuestion.test_id == test_id).offset(skip).limit(limit).all()

def update_test_question(db: Session, question_id: int, question_update: question_schema.TestQuestionUpdate) -> Optional[test_question_model.TestQuestion]:
    db_question = get_test_question(db, question_id)
    if not db_question: return None

    update_data = question_update.dict(exclude_unset=True, exclude={"options", "correct_answer_data"})

    for field, value in update_data.items():
        setattr(db_question, field, value)

    current_question_type = db_question.question_type

    if question_update.options is not None:
        db_question.options = [opt.dict() for opt in question_update.options]
        if current_question_type == QuestionType.MULTIPLE_CHOICE:
            correct_options = [opt.dict() for opt in question_update.options if opt.is_correct]
            db_question.correct_answer_data = correct_options if correct_options else None
        elif "correct_answer_data" in question_update.dict(exclude_unset=False): # If not MCQ but correct_answer_data is provided
             db_question.correct_answer_data = question_update.correct_answer_data
    elif "question_type" in update_data and current_question_type == QuestionType.MULTIPLE_CHOICE and db_question.options:
        # If only type changed to MCQ and options already existed (were not in payload)
        correct_options = [opt for opt in db_question.options if isinstance(opt, dict) and opt.get("is_correct")]
        db_question.correct_answer_data = correct_options if correct_options else None
    elif "correct_answer_data" in question_update.dict(exclude_unset=False) and current_question_type != QuestionType.MULTIPLE_CHOICE:
        db_question.correct_answer_data = question_update.correct_answer_data


    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def delete_test_question(db: Session, question_id: int) -> Optional[test_question_model.TestQuestion]:
    db_question = get_test_question(db, question_id)
    if not db_question: return None
    db.delete(db_question)
    db.commit()
    return db_question

# Enrollment and Certificate functions
def get_enrollment(db: Session, user_id: int, course_id: int) -> Optional[enrollment_model]:
    """Helper function to get a specific enrollment."""
    return db.query(enrollment_model).filter_by(user_id=user_id, course_id=course_id).first()

def enroll_student_in_course(db: Session, course_id: int, user_id: int) -> Optional[Union[enrollment_model, str]]:
    course = get_course(db, course_id)
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()

    if not course or not user:
        return "NotFound"
    if course.status != course_model.CourseStatus.published:
        return "CourseNotPublished"

    existing_enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if existing_enrollment:
        return "AlreadyEnrolled"

    # Payment gate: non-free courses require a completed payment
    if not course.is_free and (course.price is not None and course.price > 0):
        from app.services.payment_service import has_completed_payment
        if not has_completed_payment(db, user_id, course_id):
            return "PaymentRequired"

    enrollment = enrollment_model(
        user_id=user_id,
        course_id=course_id,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def unenroll_student_from_course(db: Session, course_id: int, user_id: int) -> Optional[str]:
    # No need to fetch course and user unless for specific checks not covered by enrollment existence
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if not enrollment:
        return "NotEnrolled" # Or "NotFound" if we consider enrollment itself the target resource

    db.delete(enrollment)
    db.commit()
    return "UnenrolledSuccessfully" # Or return the deleted enrollment object if preferred


def get_user_enrolled_courses(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[course_model.Course]:
    user = db.query(user_model.User).options(
        selectinload(user_model.User.enrollments).selectinload(enrollment_model.course)
    ).filter(user_model.User.id == user_id).first()

    if not user:
        return []

    # Extract Course objects from enrollments
    enrolled_courses_list = [enrollment.course for enrollment in user.enrollments if enrollment.course]
    return enrolled_courses_list[skip : skip + limit]


def get_course_instructor_courses(db: Session, instructor_id: int, skip: int = 0, limit: int = 100) -> List[course_model.Course]:
    # Implementation from previous step
    return db.query(course_model.Course).filter(course_model.Course.instructor_id == instructor_id).offset(skip).limit(limit).all()

# --- Progress Tracking Functions ---

def _calculate_progress_percentage(db: Session, enrollment: enrollment_model) -> float:
    """Helper function to calculate course completion percentage based on lessons completed."""
    course = db.query(course_model.Course).options(
        selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.lessons)
    ).filter(course_model.Course.id == enrollment.course_id).first()

    if not course:
        return 0.0

    total_lessons = sum(len(section.lessons) for section in course.sections)
    if total_lessons == 0:
        return 0.0

    completed_lessons_count = len(enrollment.completed_lessons or [])
    return min(round((completed_lessons_count / total_lessons) * 100, 1), 100.0)

def mark_lesson_completed(db: Session, user_id: int, course_id: int, lesson_id: int) -> Optional[enrollment_model]:
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if not enrollment:
        return None

    if lesson_id not in enrollment.completed_lessons:
        new_completed_lessons = list(enrollment.completed_lessons)
        new_completed_lessons.append(lesson_id)
        enrollment.completed_lessons = new_completed_lessons

        # Auto-complete parent section if all its lessons are now done
        _auto_complete_sections(db, enrollment, course_id)

        enrollment.progress_percentage = _calculate_progress_percentage(db, enrollment)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
    return enrollment


def _auto_complete_sections(db: Session, enrollment: enrollment_model, course_id: int):
    """Auto-mark sections as completed when all their lessons are done."""
    course = db.query(course_model.Course).options(
        selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.lessons)
    ).filter(course_model.Course.id == course_id).first()
    if not course:
        return

    completed_lesson_ids = set(enrollment.completed_lessons or [])
    completed_section_ids = set(enrollment.completed_sections or [])
    changed = False

    for section in course.sections:
        if section.id in completed_section_ids:
            continue
        section_lesson_ids = {lesson.id for lesson in section.lessons}
        if section_lesson_ids and section_lesson_ids.issubset(completed_lesson_ids):
            completed_section_ids.add(section.id)
            changed = True

    if changed:
        enrollment.completed_sections = list(completed_section_ids)

def mark_section_completed(db: Session, user_id: int, course_id: int, section_id: int) -> Optional[enrollment_model]:
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if not enrollment:
        return None # Or raise HTTPException

    if section_id not in enrollment.completed_sections:
        new_completed_sections = list(enrollment.completed_sections)
        new_completed_sections.append(section_id)
        enrollment.completed_sections = new_completed_sections

        enrollment.progress_percentage = _calculate_progress_percentage(db, enrollment)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
    return enrollment

def record_test_attempt(db: Session, user_id: int, course_id: int, test_id: int, score: float, passed: bool, questions_summary: List[dict], attempted_at: datetime) -> Optional[enrollment_model]:
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if not enrollment:
        return None # Or raise HTTPException

    attempt_details = {
        "test_id": test_id,
        "score": score,
        "passed": passed,
        "attempted_at": attempted_at.isoformat(),
        "questions_summary": questions_summary # e.g., [{"question_id": 1, "correct": true, "points_earned": 5}]
    }

    new_test_attempts = list(enrollment.test_attempts)
    new_test_attempts.append(attempt_details)
    enrollment.test_attempts = new_test_attempts

    # Update test_scores as well
    # This assumes we only keep the latest score per test_id, or all scores if desired.
    # For simplicity, let's store all scores, but often you might want to store the highest or latest.
    score_detail = {"test_id": test_id, "score": score}
    new_test_scores = list(enrollment.test_scores)

    # Optional: Update if already exists, or just append
    existing_score_index = -1
    for i, s in enumerate(new_test_scores):
        if s.get("test_id") == test_id:
            existing_score_index = i
            break
    if existing_score_index != -1: # Example: update existing score to latest
        new_test_scores[existing_score_index] = score_detail
    else:
        new_test_scores.append(score_detail)
    enrollment.test_scores = new_test_scores

    # Potentially recalculate progress if tests contribute to it
    # enrollment.progress_percentage = _calculate_progress_percentage(db, enrollment)

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

# --- End Progress Tracking Functions ---

def check_and_issue_certificate(db: Session, user_id: int, course_id: int) -> Optional[Union[certificate_model.Certificate, str]]:
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if not enrollment:
        return "EnrollmentNotFound"

    course = db.query(course_model.Course).options(
        selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.lessons),
        selectinload(course_model.Course.sections).selectinload(course_section_model.CourseSection.test) # Load tests for points calculation
    ).filter(course_model.Course.id == course_id).first()

    if not course:
        return "CourseNotFound"

    # 1. Check if certificate already issued
    existing_certificate = get_certificate_for_course_by_user(db, user_id=user_id, course_id=course_id)
    if existing_certificate:
        return "CertificateAlreadyIssued"

    # 2. Check completion of all lessons
    all_lesson_ids = set()
    for section in course.sections:
        for lesson in section.lessons:
            all_lesson_ids.add(lesson.id)

    completed_lesson_ids = set(enrollment.completed_lessons or [])
    if not all_lesson_ids.issubset(completed_lesson_ids):
        return "NotAllLessonsCompleted"

    # 3. Auto-complete sections whose lessons are all done, then verify
    _auto_complete_sections(db, enrollment, course_id)
    db.add(enrollment)
    db.flush()

    all_section_ids = {s.id for s in course.sections}
    completed_section_ids = set(enrollment.completed_sections or [])
    if not all_section_ids.issubset(completed_section_ids):
        return "NotAllSectionsCompleted"

    # 4. Check points required for certificate
    if course.points_required_for_certificate is not None and course.points_required_for_certificate > 0:
        total_earned_points = 0
        # This assumes scores in test_scores are final scores for tests that grant points.
        # And that test_id in test_scores corresponds to CourseTest's id.
        # A more robust system might link scores directly to questions or have a clear "points_value" for each test.

        # For simplicity, let's sum scores from enrollment.test_scores.
        # This needs to be aligned with how points are actually awarded and stored.
        # Assuming each score in test_scores contributes to the points_required_for_certificate.
        # This part might need significant refinement based on actual point system.
        # Example: sum all scores. This might not be correct if scores are percentages.
        # A better way would be to sum points from `test_attempts.questions_summary.points_earned` if available and accurate.

        # Let's assume test_scores contains objects like {"test_id": X, "score": Y, "points_awarded": Z}
        # Or, if points are directly from CourseTest.pass_mark or similar

        # Simplistic sum of scores stored (assuming these are points, not percentages)
        for score_info in enrollment.test_scores:
            total_earned_points += score_info.get("score", 0) # Needs refinement

        if total_earned_points < course.points_required_for_certificate:
            return f"PointsNotMet:{total_earned_points}/{course.points_required_for_certificate}"

    # All conditions met, issue certificate
    certificate_data = certificate_schema.CertificateCreate(
        user_id=user_id,
        course_id=course_id,
        issue_date=datetime.utcnow(),
        # certificate_url and verification_code can be generated here or by another service
    )
    new_certificate = create_certificate(db, certificate_data)

    if new_certificate:
        enrollment.completed_at = datetime.utcnow()
        enrollment.progress_percentage = 100.0 # Mark as fully completed
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return new_certificate
    else:
        # This case should ideally not happen if create_certificate is robust
        return "CertificateCreationError"


def create_certificate(db: Session, certificate_in: certificate_schema.CertificateCreate) -> Optional[certificate_model.Certificate]:
    import uuid
    existing_certificate = db.query(certificate_model.Certificate).filter(
        certificate_model.Certificate.user_id == certificate_in.user_id,
        certificate_model.Certificate.course_id == certificate_in.course_id
    ).first()
    if existing_certificate: return existing_certificate

    verification_code = f"CERT-{uuid.uuid4().hex[:10].upper()}"
    certificate_url = f"/certificates/verify/{verification_code}"

    db_certificate = certificate_model.Certificate(
        user_id=certificate_in.user_id,
        course_id=certificate_in.course_id,
        issue_date=certificate_in.issue_date,
        verification_code=verification_code,
        certificate_url=certificate_url,
    )
    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


def get_certificate_by_id(db: Session, certificate_id: int) -> Optional[certificate_model.Certificate]:
    # Implementation from previous step
    return db.query(certificate_model.Certificate).filter(certificate_model.Certificate.id == certificate_id).first()


def get_certificates_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[certificate_model.Certificate]:
    # Implementation from previous step
    return db.query(certificate_model.Certificate).filter(
        certificate_model.Certificate.user_id == user_id
    ).options(
        joinedload(certificate_model.Certificate.course)
    ).order_by(
        certificate_model.Certificate.issue_date.desc()
    ).offset(skip).limit(limit).all()


def get_certificate_for_course_by_user(db: Session, user_id: int, course_id: int) -> Optional[certificate_model.Certificate]:
    # Implementation from previous step
    return db.query(certificate_model.Certificate).filter(
        certificate_model.Certificate.user_id == user_id,
        certificate_model.Certificate.course_id == course_id
    ).first()
