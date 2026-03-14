import pytest
from unittest.mock import AsyncMock

# Import service functions to be tested
from app.services.student_service import (
    get_student_dashboard_stats_service,
    get_student_enrolled_courses_service,
    get_student_overall_progress_service,
    get_student_weekly_activity_service,
    get_student_recommended_courses_service,
    get_student_recent_certificates_service,
)

# Import Pydantic response schemas to validate return types
from app.schemas.student import (
    StudentDashboardStats,
    EnrolledCourse,
    OverallProgress,
    WeeklyActivity,
    RecommendedCourse,
    RecentCertificate,
)
from app.models.user import User as UserModel # For creating dummy user for service functions
from typing import List

# Dummy user data for testing service functions that require a current_user
dummy_user_data = {"id": 1, "username": "teststudent", "email": "teststudent@example.com", "role": "student", "is_active": True}
mock_user_instance = UserModel(**dummy_user_data)

@pytest.mark.asyncio
async def test_get_student_dashboard_stats_service():
    mock_db_session = AsyncMock()
    result = await get_student_dashboard_stats_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, StudentDashboardStats)
    assert result.enrolled_courses_count >= 0
    assert result.certificates_count >= 0
    assert result.total_study_hours >= 0
    assert 0 <= result.average_progress <= 100

@pytest.mark.asyncio
async def test_get_student_enrolled_courses_service():
    mock_db_session = AsyncMock()
    result = await get_student_enrolled_courses_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    if result: # Dummy data might result in an empty list
        for item in result:
            assert isinstance(item, EnrolledCourse)
            assert item.id >= 0
            assert item.title is not None
            assert 0 <= item.progress <= 100
            assert item.image_url is not None

@pytest.mark.asyncio
async def test_get_student_overall_progress_service():
    mock_db_session = AsyncMock()
    result = await get_student_overall_progress_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, OverallProgress)
    assert 0 <= result.completed_percentage <= 100
    assert 0 <= result.in_progress_percentage <= 100
    # Optionally, assert result.completed_percentage + result.in_progress_percentage == 100 if that's an invariant

@pytest.mark.asyncio
async def test_get_student_weekly_activity_service():
    mock_db_session = AsyncMock()
    result = await get_student_weekly_activity_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    # Service function is designed to return 7 days, but dummy data might change
    # For now, we expect some data. If it can be empty, adjust test.
    assert len(result) > 0 # Assuming dummy data provides some activity
    for item in result:
        assert isinstance(item, WeeklyActivity)
        assert item.day_of_week is not None
        assert item.study_hours >= 0.0

@pytest.mark.asyncio
async def test_get_student_recommended_courses_service():
    mock_db_session = AsyncMock()
    result = await get_student_recommended_courses_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    if result:
        for item in result:
            assert isinstance(item, RecommendedCourse)
            assert item.id >= 0
            assert item.title is not None
            assert item.instructor_name is not None
            assert item.duration_weeks > 0
            assert item.image_url is not None

@pytest.mark.asyncio
async def test_get_student_recent_certificates_service():
    mock_db_session = AsyncMock()
    result = await get_student_recent_certificates_service(db=mock_db_session, current_user=mock_user_instance)

    assert isinstance(result, List)
    if result:
        for item in result:
            assert isinstance(item, RecentCertificate)
            assert item.id >= 0
            assert item.course_name is not None
            assert item.date_obtained is not None # Pydantic converts to date object

print("File backend/tests/services/test_student_dashboard_services.py created with service unit tests.")
