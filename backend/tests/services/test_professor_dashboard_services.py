import pytest
from unittest.mock import AsyncMock

# Import service functions to be tested
from app.services.professor_service import (
    get_professor_dashboard_stats_service,
    get_professor_published_courses_service,
    get_professor_student_engagement_service,
    get_professor_student_distribution_service,
    get_professor_recent_activities_service,
)

# Import Pydantic response schemas to validate return types
from app.schemas.professor import (
    ProfessorDashboardStats,
    CoursePerformance,
    StudentEngagement,
    StudentDistributionInProfessorCourses,
    ProfessorRecentActivity,
)
from app.models.user import User as UserModel # For creating dummy user for service functions
from typing import List

# Dummy user data for testing service functions that require a current_user
# Service functions expect a UserModel instance
dummy_user_data = {"id": 1, "username": "testprof", "email": "testprof@example.com", "role": "professor", "is_active": True}
mock_user_instance = UserModel(**dummy_user_data)

@pytest.mark.asyncio
async def test_get_professor_dashboard_stats_service():
    mock_db_session = AsyncMock()
    result = await get_professor_dashboard_stats_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, ProfessorDashboardStats)
    assert result.published_courses_count >= 0
    assert result.total_students_count >= 0
    assert result.average_rating >= 0.0
    assert result.total_questions_count >= 0

@pytest.mark.asyncio
async def test_get_professor_published_courses_service():
    mock_db_session = AsyncMock()
    result = await get_professor_published_courses_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    # Dummy data might return an empty list if user.id % X leads to 0 courses
    # So, only assert type if list is not empty
    if result:
        for item in result:
            assert isinstance(item, CoursePerformance)
            assert item.id >= 0
            assert item.title is not None
            assert item.students_count >= 0
            assert item.rating >= 0.0

@pytest.mark.asyncio
async def test_get_professor_student_engagement_service():
    mock_db_session = AsyncMock()
    result = await get_professor_student_engagement_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    if result:
        for item in result:
            assert isinstance(item, StudentEngagement)
            assert item.course_name is not None
            assert item.average_hours_spent >= 0.0

@pytest.mark.asyncio
async def test_get_professor_student_distribution_service():
    mock_db_session = AsyncMock()
    result = await get_professor_student_distribution_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, StudentDistributionInProfessorCourses)
    assert result.active_students_count >= 0
    assert result.inactive_students_count >= 0
    assert result.completed_students_count >= 0

@pytest.mark.asyncio
async def test_get_professor_recent_activities_service():
    mock_db_session = AsyncMock()
    result = await get_professor_recent_activities_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    if result:
        for item in result:
            assert isinstance(item, ProfessorRecentActivity)
            assert item.id >= 0
            assert item.student_name is not None
            assert item.course_name is not None
            assert item.activity_type is not None
            assert item.content is not None
            assert item.timestamp is not None

print("File backend/tests/services/test_professor_dashboard_services.py created with service unit tests.")
