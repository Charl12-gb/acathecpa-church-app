import pytest
from unittest.mock import AsyncMock, MagicMock # AsyncMock for async functions, MagicMock for db session

# Import service functions to be tested
from app.services.professor_service import (
    get_admin_dashboard_stats_service,
    get_admin_professors_service,
    get_admin_recent_activities_service,
    get_admin_user_distribution_service,
    get_admin_monthly_registrations_service,
)

# Import Pydantic response schemas to validate return types
from app.schemas.professor import (
    AdminDashboardStats,
    ProfessorStats,
    RecentActivity,
    UserDistribution,
    MonthlyRegistration,
)
from typing import List

@pytest.mark.asyncio
async def test_get_admin_dashboard_stats_service():
    mock_db_session = AsyncMock() # Mock the DB session for an async context if needed by service

    # Call the service function
    # Since services currently return hardcoded data, db session isn't actively used by them for these dummy functions yet.
    result = await get_admin_dashboard_stats_service(db=mock_db_session)

    # Assert that the result is an instance of the correct schema
    assert isinstance(result, AdminDashboardStats)

    # Assert specific dummy data values (optional, but good for consistency)
    assert result.total_users >= 0
    assert result.total_professors >= 0
    assert result.total_courses >= 0
    assert result.new_enrollments_last_month >= 0
    # Example of checking one specific value if it's fixed in dummy data
    # assert result.total_users == 1605 # As per dummy data in service

@pytest.mark.asyncio
async def test_get_admin_professors_service():
    mock_db_session = AsyncMock()
    result = await get_admin_professors_service(db=mock_db_session)

    assert isinstance(result, List)
    assert len(result) > 0  # Assuming dummy data returns at least one professor
    for item in result:
        assert isinstance(item, ProfessorStats)
        assert item.id >= 0
        assert item.name is not None
        assert "@" in item.email # Simple email format check
        assert item.courses_count >= 0
        assert item.students_count >= 0
        assert item.average_rating >= 0.0 and item.average_rating <= 5.0 # Assuming a 0-5 scale

@pytest.mark.asyncio
async def test_get_admin_recent_activities_service():
    mock_db_session = AsyncMock()
    result = await get_admin_recent_activities_service(db=mock_db_session)

    assert isinstance(result, List)
    assert len(result) > 0 # Assuming dummy data returns at least one activity
    for item in result:
        assert isinstance(item, RecentActivity)
        assert item.id >= 0
        assert item.user_name is not None
        assert item.action is not None
        assert item.resource_name is not None
        assert item.timestamp is not None # Could also validate ISO format

@pytest.mark.asyncio
async def test_get_admin_user_distribution_service():
    mock_db_session = AsyncMock()
    result = await get_admin_user_distribution_service(db=mock_db_session)

    assert isinstance(result, UserDistribution)
    assert result.students_count >= 0
    assert result.professors_count >= 0
    assert result.admins_count >= 0

@pytest.mark.asyncio
async def test_get_admin_monthly_registrations_service():
    mock_db_session = AsyncMock()
    result = await get_admin_monthly_registrations_service(db=mock_db_session)

    assert isinstance(result, List)
    assert len(result) > 0 # Assuming dummy data returns at least one month
    for item in result:
        assert isinstance(item, MonthlyRegistration)
        assert item.month is not None
        assert len(item.month) >= 3 # e.g., "Jan", "Feb"
        assert item.count >= 0

print("File backend/tests/services/test_admin_dashboard_services.py created with service unit tests.")
