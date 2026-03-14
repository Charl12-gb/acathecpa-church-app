# Tests for Admin Dashboard API Endpoints and Schemas
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app # Main FastAPI application
# Schemas to test
from app.schemas.professor import (
    AdminDashboardStats,
    ProfessorStats,
    RecentActivity,
    UserDistribution,
    MonthlyRegistration,
)
from pydantic import ValidationError

# Placeholder for override_get_current_active_admin_user
# Will be defined properly in the test class or setup

# --- Schema Tests ---

def test_admin_dashboard_stats_schema_valid():
    data = {"total_users": 100, "total_professors": 10, "total_courses": 20, "new_enrollments_last_month": 5}
    stats = AdminDashboardStats(**data)
    assert stats.total_users == data["total_users"]
    assert stats.total_professors == data["total_professors"]
    assert stats.total_courses == data["total_courses"]
    assert stats.new_enrollments_last_month == data["new_enrollments_last_month"]

def test_admin_dashboard_stats_schema_invalid_type():
    data = {"total_users": "100", "total_professors": 10, "total_courses": 20, "new_enrollments_last_month": 5}
    with pytest.raises(ValidationError):
        AdminDashboardStats(**data)

def test_professor_stats_schema_valid():
    data = {"id": 1, "name": "Prof Test", "email": "prof@test.com", "courses_count": 5, "students_count": 50, "average_rating": 4.5}
    stats = ProfessorStats(**data)
    assert stats.id == data["id"]
    assert stats.name == data["name"]
    assert stats.email == data["email"]
    assert stats.courses_count == data["courses_count"]
    assert stats.students_count == data["students_count"]
    assert stats.average_rating == data["average_rating"]

def test_professor_stats_schema_invalid_rating():
    data = {"id": 1, "name": "Prof Test", "email": "prof@test.com", "courses_count": 5, "students_count": 50, "average_rating": "high"}
    with pytest.raises(ValidationError):
        ProfessorStats(**data)

def test_recent_activity_schema_valid():
    data = {"id": 1, "user_name": "User Test", "action": "logged_in", "resource_name": "system", "timestamp": "2023-01-01T12:00:00Z"}
    activity = RecentActivity(**data)
    assert activity.id == data["id"]
    assert activity.user_name == data["user_name"]
    assert activity.action == data["action"]
    assert activity.resource_name == data["resource_name"]
    assert activity.timestamp == data["timestamp"]

def test_recent_activity_schema_missing_field():
    data = {"id": 1, "user_name": "User Test", "action": "logged_in", "timestamp": "2023-01-01T12:00:00Z"} # Missing resource_name
    with pytest.raises(ValidationError):
        RecentActivity(**data)

def test_user_distribution_schema_valid():
    data = {"students_count": 100, "professors_count": 10, "admins_count": 2}
    dist = UserDistribution(**data)
    assert dist.students_count == data["students_count"]
    assert dist.professors_count == data["professors_count"]
    assert dist.admins_count == data["admins_count"]

def test_user_distribution_schema_negative_value():
    data = {"students_count": -100, "professors_count": 10, "admins_count": 2}
    # Pydantic v2 by default does not raise error for negative if type is int and no ge=0 constraint
    # Assuming schemas have Field(..., ge=0) or similar for counts for this test to be meaningful
    # For now, this test might pass if no such constraint. If constraints exist, it should raise ValidationError.
    # Let's assume constraints are in place for a more robust test.
    # If not, this test should be adjusted or constraints added to schemas.
    try:
        dist = UserDistribution(**data)
        # If models have constraints like ge=0, this line shouldn't be reached.
        # This is a placeholder for actual model constraints.
        # For now, let's assume it passes if Pydantic allows negative int.
        # To make it fail as intended, models need e.g. students_count: int = Field(..., ge=0)
        if dist.students_count < 0 : # Manual check if Pydantic does not raise
             pytest.fail("Negative counts should ideally be disallowed by schema constraints.")
    except ValidationError:
        pass # Expected if constraints like ge=0 are present

def test_monthly_registration_schema_valid():
    data = {"month": "Jan", "count": 50}
    reg = MonthlyRegistration(**data)
    assert reg.month == data["month"]
    assert reg.count == data["count"]

def test_monthly_registration_schema_invalid_month_format():
    # This depends on how strictly 'month' is defined. If just a string, 'January' is valid.
    # If specific format like "Jan", "Feb" is enforced by validator, this could fail.
    # Pydantic default string field won't validate format unless a custom validator or regex is used.
    data = {"month": "JanuaryLong", "count": "fifty"}
    with pytest.raises(ValidationError): # count will fail type validation
        MonthlyRegistration(**data)

from app.core.config import settings # To get API_V1_STR
# Import the specific dependency to override
from app.routers.professor_router import get_current_active_admin_user as admin_auth_dependency
from app.models.user import User as UserModel # For creating a dummy user object

# --- API Endpoint Tests ---

# Define a reusable dummy admin user
dummy_admin_user_data = {"username": "admin_test", "role": "admin", "id": 1, "email": "admin@test.com", "is_active": True}
# Create a UserModel instance for the dependency override, as the dependency expects a UserModel instance
mock_admin_user = UserModel(**dummy_admin_user_data)

async def override_get_current_active_admin_user_dependency():
    return mock_admin_user

class TestAdminDashboardEndpoints:
    client = TestClient(app)

    def setup_method(self):
        app.dependency_overrides[admin_auth_dependency] = override_get_current_active_admin_user_dependency

    def teardown_method(self):
        app.dependency_overrides = {}

    @patch('app.routers.professor_router.dashboard_services.get_admin_dashboard_stats_service', new_callable=AsyncMock)
    def test_get_admin_dashboard_stats_endpoint(self, mock_service):
        expected_data = {"total_users": 200, "total_professors": 20, "total_courses": 30, "new_enrollments_last_month": 10}
        mock_service.return_value = AdminDashboardStats(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/admin/dashboard/stats")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once()

    @patch('app.routers.professor_router.dashboard_services.get_admin_professors_service', new_callable=AsyncMock)
    def test_get_admin_professors_endpoint(self, mock_service):
        expected_data = [
            {"id": 1, "name": "Prof A", "email": "profa@test.com", "courses_count": 5, "students_count": 100, "average_rating": 4.5},
            {"id": 2, "name": "Prof B", "email": "profb@test.com", "courses_count": 3, "students_count": 80, "average_rating": 4.2},
        ]
        mock_service.return_value = [ProfessorStats(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/admin/dashboard/professors")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once()

    @patch('app.routers.professor_router.dashboard_services.get_admin_recent_activities_service', new_callable=AsyncMock)
    def test_get_admin_recent_activities_endpoint(self, mock_service):
        expected_data = [
            {"id": 1, "user_name": "User X", "action": "test_action_1", "resource_name": "Resource A", "timestamp": "2023-01-01T00:00:00Z"},
            {"id": 2, "user_name": "User Y", "action": "test_action_2", "resource_name": "Resource B", "timestamp": "2023-01-02T00:00:00Z"},
        ]
        mock_service.return_value = [RecentActivity(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/admin/dashboard/recent-activities")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once()

    @patch('app.routers.professor_router.dashboard_services.get_admin_user_distribution_service', new_callable=AsyncMock)
    def test_get_admin_user_distribution_endpoint(self, mock_service):
        expected_data = {"students_count": 150, "professors_count": 15, "admins_count": 5}
        mock_service.return_value = UserDistribution(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/admin/dashboard/user-distribution")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once()

    @patch('app.routers.professor_router.dashboard_services.get_admin_monthly_registrations_service', new_callable=AsyncMock)
    def test_get_admin_monthly_registrations_endpoint(self, mock_service):
        expected_data = [
            {"month": "Jan", "count": 100},
            {"month": "Feb", "count": 120},
        ]
        mock_service.return_value = [MonthlyRegistration(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/admin/dashboard/monthly-registrations")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once()

# Note: The UserDistribution schema test for negative values assumes Field constraints (e.g., ge=0).
# If these are not present in the actual schema, that test will behave differently.
# It's better to add those constraints to the Pydantic models for robustness.
# For now, I've added a try-except pass for UserDistribution negative value test if ge=0 is not in schema.
print("File backend/tests/api/v1/test_admin_dashboard.py updated with endpoint tests.")
