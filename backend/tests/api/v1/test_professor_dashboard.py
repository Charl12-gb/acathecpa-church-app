# Tests for Professor Dashboard API Endpoints and Schemas
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app # Main FastAPI application
from app.schemas.professor import (
    ProfessorDashboardStats,
    CoursePerformance,
    StudentEngagement,
    StudentDistributionInProfessorCourses,
    ProfessorRecentActivity,
)
from pydantic import ValidationError
from app.core.config import settings
from app.models.user import User as UserModel # For dummy user
# Import the specific dependency to override for endpoint tests
from app.routers.professor_router import get_current_active_professor_user as professor_auth_dependency


# --- Schema Tests ---

def test_professor_dashboard_stats_schema_valid():
    data = {"published_courses_count": 5, "total_students_count": 100, "average_rating": 4.5, "total_questions_count": 50}
    stats = ProfessorDashboardStats(**data)
    assert stats.published_courses_count == data["published_courses_count"]
    assert stats.average_rating == data["average_rating"]

def test_professor_dashboard_stats_schema_invalid_type():
    data = {"published_courses_count": "five", "total_students_count": 100, "average_rating": 4.5, "total_questions_count": 50}
    with pytest.raises(ValidationError):
        ProfessorDashboardStats(**data)

def test_course_performance_schema_valid():
    data = {"id": 1, "title": "Test Course", "students_count": 30, "rating": 4.2, "last_updated": "2023-01-01T10:00:00Z"}
    item = CoursePerformance(**data)
    assert item.title == data["title"]
    assert item.rating == data["rating"]

def test_course_performance_schema_invalid_date():
    data = {"id": 1, "title": "Test Course", "students_count": 30, "rating": 4.2, "last_updated": "yesterday"}
    with pytest.raises(ValidationError):
        CoursePerformance(**data) # Pydantic will try to parse date string

def test_student_engagement_schema_valid():
    data = {"course_name": "Engaging Course", "average_hours_spent": 10.5}
    item = StudentEngagement(**data)
    assert item.course_name == data["course_name"]
    assert item.average_hours_spent == data["average_hours_spent"]

def test_student_engagement_schema_negative_hours():
    data = {"course_name": "Engaging Course", "average_hours_spent": -5}
    # Assuming average_hours_spent: float = Field(..., ge=0)
    with pytest.raises(ValidationError):
         StudentEngagement(**data)

def test_student_distribution_schema_valid():
    data = {"active_students_count": 50, "inactive_students_count": 10, "completed_students_count": 20}
    item = StudentDistributionInProfessorCourses(**data)
    assert item.active_students_count == data["active_students_count"]

def test_student_distribution_schema_invalid_type():
    data = {"active_students_count": "fifty", "inactive_students_count": 10, "completed_students_count": 20}
    with pytest.raises(ValidationError):
        StudentDistributionInProfessorCourses(**data)

def test_professor_recent_activity_schema_valid():
    data = {"id": 1, "student_name": "Student Test", "course_name": "Course X", "activity_type": "question", "content": "Help?", "timestamp": "2023-01-01T12:30:00Z"}
    item = ProfessorRecentActivity(**data)
    assert item.student_name == data["student_name"]
    assert item.activity_type == data["activity_type"]

def test_professor_recent_activity_schema_missing_content():
    data = {"id": 1, "student_name": "Student Test", "course_name": "Course X", "activity_type": "question", "timestamp": "2023-01-01T12:30:00Z"}
    with pytest.raises(ValidationError):
        ProfessorRecentActivity(**data)


# --- API Endpoint Tests (Structure) ---

# Define a reusable dummy professor user
dummy_professor_user_data = {"username": "prof_test", "role": "professor", "id": 2, "email": "prof@test.com", "is_active": True}
mock_professor_user = UserModel(**dummy_professor_user_data)

async def override_get_current_active_professor_user_dependency():
    return mock_professor_user

class TestProfessorDashboardEndpoints:
    client = TestClient(app)

    def setup_method(self):
        app.dependency_overrides[professor_auth_dependency] = override_get_current_active_professor_user_dependency

    def teardown_method(self):
        app.dependency_overrides = {}

    @patch('app.routers.professor_router.dashboard_services.get_professor_dashboard_stats_service', new_callable=AsyncMock)
    def test_get_professor_dashboard_stats_endpoint(self, mock_service):
        expected_data = {"published_courses_count": 3, "total_students_count": 80, "average_rating": 4.1, "total_questions_count": 30}
        # The service returns a Pydantic model, so we mock that
        mock_service.return_value = ProfessorDashboardStats(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/professors/dashboard/stats")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=unittest.mock.ANY, current_user=mock_professor_user)


    @patch('app.routers.professor_router.dashboard_services.get_professor_published_courses_service', new_callable=AsyncMock)
    def test_get_professor_published_courses_endpoint(self, mock_service):
        expected_data = [
            {"id": 10, "title": "Course Alpha", "students_count": 40, "rating": 4.0, "last_updated": "2023-02-01T10:00:00Z"},
        ]
        mock_service.return_value = [CoursePerformance(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/professors/dashboard/published-courses")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=unittest.mock.ANY, current_user=mock_professor_user)

    @patch('app.routers.professor_router.dashboard_services.get_professor_student_engagement_service', new_callable=AsyncMock)
    def test_get_professor_student_engagement_endpoint(self, mock_service):
        expected_data = [
            {"course_name": "Course Alpha", "average_hours_spent": 12.0},
        ]
        mock_service.return_value = [StudentEngagement(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/professors/dashboard/student-engagement")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=unittest.mock.ANY, current_user=mock_professor_user)

    @patch('app.routers.professor_router.dashboard_services.get_professor_student_distribution_service', new_callable=AsyncMock)
    def test_get_professor_student_distribution_endpoint(self, mock_service):
        expected_data = {"active_students_count": 70, "inactive_students_count": 5, "completed_students_count": 15}
        mock_service.return_value = StudentDistributionInProfessorCourses(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/professors/dashboard/student-distribution")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=unittest.mock.ANY, current_user=mock_professor_user)

    @patch('app.routers.professor_router.dashboard_services.get_professor_recent_activities_service', new_callable=AsyncMock)
    def test_get_professor_recent_activities_endpoint(self, mock_service):
        expected_data = [
            {"id": 101, "student_name": "Jane Doe", "course_name": "Course Alpha", "activity_type": "comment", "content": "Loved it!", "timestamp": "2023-02-05T10:00:00Z"},
        ]
        mock_service.return_value = [ProfessorRecentActivity(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/professors/dashboard/recent-activities")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=unittest.mock.ANY, current_user=mock_professor_user)

print("File backend/tests/api/v1/test_professor_dashboard.py created with schema tests and endpoint tests structure.")
# Need to add unittest.mock.ANY to imports if not already there. It's part of unittest.mock
# from unittest.mock import patch, AsyncMock, ANY
# For the assert_called_once_with, the db session comes from Depends(get_db) which is not easily comparable directly in mock args.
# Using ANY for the db session is a common practice.
# The current_user should be the mock_professor_user object.
# The endpoint tests are now more complete.
# Added `from unittest.mock import ANY` if it's needed, usually it's part of `unittest.mock` itself.
# Corrected assert_called_once_with to include db=unittest.mock.ANY and current_user=mock_professor_user
# The file content now includes the endpoint tests.
from unittest.mock import ANY # Make sure ANY is imported for test_get_professor_dashboard_stats_endpoint
