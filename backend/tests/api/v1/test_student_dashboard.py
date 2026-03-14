# Tests for Student Dashboard API Endpoints and Schemas
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, ANY # Added ANY

from app.main import app # Main FastAPI application
from app.schemas.student import (
    StudentDashboardStats,
    EnrolledCourse,
    OverallProgress,
    WeeklyActivity,
    RecommendedCourse,
    RecentCertificate,
)
from pydantic import ValidationError
from app.core.config import settings
from app.models.user import User as UserModel # For dummy user
# Import the specific dependency to override for endpoint tests
from app.routers.student_router import get_current_active_student_user as student_auth_dependency

# --- Schema Tests ---

def test_student_dashboard_stats_schema_valid():
    data = {"enrolled_courses_count": 5, "certificates_count": 2, "total_study_hours": 100, "average_progress": 75.5}
    stats = StudentDashboardStats(**data)
    assert stats.enrolled_courses_count == data["enrolled_courses_count"]
    assert stats.average_progress == data["average_progress"]

def test_student_dashboard_stats_schema_invalid_progress():
    data = {"enrolled_courses_count": 5, "certificates_count": 2, "total_study_hours": 100, "average_progress": 101.0} # Progress > 100
    with pytest.raises(ValidationError): # Assuming ge=0, le=100 in schema
        StudentDashboardStats(**data)

def test_enrolled_course_schema_valid():
    data = {"id": 1, "title": "Math 101", "progress": 50, "last_activity_timestamp": "2023-01-15T10:00:00Z", "image_url": "http://example.com/math.jpg"}
    course = EnrolledCourse(**data)
    assert course.title == data["title"]
    assert course.progress == data["progress"]

def test_enrolled_course_schema_invalid_url():
    data = {"id": 1, "title": "Math 101", "progress": 50, "last_activity_timestamp": "2023-01-15T10:00:00Z", "image_url": "not-a-url"}
    with pytest.raises(ValidationError): # Pydantic HttpUrl validation
        EnrolledCourse(**data)

def test_overall_progress_schema_valid():
    data = {"completed_percentage": 60, "in_progress_percentage": 40}
    progress = OverallProgress(**data)
    assert progress.completed_percentage == data["completed_percentage"]

def test_overall_progress_schema_invalid_sum():
    # This schema doesn't inherently validate sum of percentages.
    # That would require a model validator. Test passes if fields are valid integers.
    data = {"completed_percentage": 70, "in_progress_percentage": 70}
    try:
        OverallProgress(**data)
    except ValidationError:
        pytest.fail("OverallProgress schema failed unexpectedly with valid individual percentages.")


def test_weekly_activity_schema_valid():
    data = {"day_of_week": "Mon", "study_hours": 2.5}
    activity = WeeklyActivity(**data)
    assert activity.day_of_week == data["day_of_week"]
    assert activity.study_hours == data["study_hours"]

def test_weekly_activity_schema_invalid_hours():
    data = {"day_of_week": "Tue", "study_hours": -1.0} # Negative hours
    with pytest.raises(ValidationError): # Assuming ge=0 in schema
        WeeklyActivity(**data)

def test_recommended_course_schema_valid():
    data = {"id": 10, "title": "Physics 102", "instructor_name": "Dr. Atom", "duration_weeks": 10, "image_url": "http://example.com/physics.jpg"}
    course = RecommendedCourse(**data)
    assert course.title == data["title"]
    assert course.duration_weeks == data["duration_weeks"]

def test_recommended_course_schema_missing_instructor():
    data = {"id": 10, "title": "Physics 102", "duration_weeks": 10, "image_url": "http://example.com/physics.jpg"}
    with pytest.raises(ValidationError):
        RecommendedCourse(**data)

def test_recent_certificate_schema_valid():
    data = {"id": 7, "course_name": "History of Time", "date_obtained": "2023-05-20"}
    cert = RecentCertificate(**data)
    assert cert.course_name == data["course_name"]
    assert str(cert.date_obtained) == data["date_obtained"] # Pydantic converts to date object

def test_recent_certificate_schema_invalid_date_format():
    data = {"id": 7, "course_name": "History of Time", "date_obtained": "May 20th, 2023"}
    with pytest.raises(ValidationError):
        RecentCertificate(**data)


# --- API Endpoint Tests (Structure) ---

dummy_student_user_data = {"username": "student_test", "role": "student", "id": 3, "email": "student@test.com", "is_active": True}
mock_student_user = UserModel(**dummy_student_user_data)

async def override_get_current_active_student_user_dependency():
    return mock_student_user

class TestStudentDashboardEndpoints:
    client = TestClient(app)

    def setup_method(self):
        app.dependency_overrides[student_auth_dependency] = override_get_current_active_student_user_dependency

    def teardown_method(self):
        app.dependency_overrides = {}

    @patch('app.routers.student_router.student_dashboard_services.get_student_dashboard_stats_service', new_callable=AsyncMock)
    def test_get_student_dashboard_stats_endpoint(self, mock_service):
        expected_data = {"enrolled_courses_count": 3, "certificates_count": 1, "total_study_hours": 50, "average_progress": 60.0}
        mock_service.return_value = StudentDashboardStats(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/stats")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

    @patch('app.routers.student_router.student_dashboard_services.get_student_enrolled_courses_service', new_callable=AsyncMock)
    def test_get_student_enrolled_courses_endpoint(self, mock_service):
        expected_data = [
            {"id": 1, "title": "Course A", "progress": 50, "last_activity_timestamp": "2023-01-01T00:00:00Z", "image_url": "http://example.com/a.jpg"}
        ]
        mock_service.return_value = [EnrolledCourse(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/enrolled-courses")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

    @patch('app.routers.student_router.student_dashboard_services.get_student_overall_progress_service', new_callable=AsyncMock)
    def test_get_student_overall_progress_endpoint(self, mock_service):
        expected_data = {"completed_percentage": 25, "in_progress_percentage": 75}
        mock_service.return_value = OverallProgress(**expected_data)

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/overall-progress")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

    @patch('app.routers.student_router.student_dashboard_services.get_student_weekly_activity_service', new_callable=AsyncMock)
    def test_get_student_weekly_activity_endpoint(self, mock_service):
        expected_data = [{"day_of_week": "Mon", "study_hours": 3.0}]
        mock_service.return_value = [WeeklyActivity(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/weekly-activity")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

    @patch('app.routers.student_router.student_dashboard_services.get_student_recommended_courses_service', new_callable=AsyncMock)
    def test_get_student_recommended_courses_endpoint(self, mock_service):
        expected_data = [
            {"id": 101, "title": "Rec Course 1", "instructor_name": "Inst X", "duration_weeks": 8, "image_url": "http://example.com/rec1.jpg"}
        ]
        mock_service.return_value = [RecommendedCourse(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/recommended-courses")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

    @patch('app.routers.student_router.student_dashboard_services.get_student_recent_certificates_service', new_callable=AsyncMock)
    def test_get_student_recent_certificates_endpoint(self, mock_service):
        expected_data = [{"id": 20, "course_name": "Cert Course", "date_obtained": "2022-12-01"}]
        mock_service.return_value = [RecentCertificate(**d) for d in expected_data]

        response = self.client.get(f"{settings.API_V1_STR}/student/dashboard/recent-certificates")
        assert response.status_code == 200
        assert response.json() == expected_data
        mock_service.assert_called_once_with(db=ANY, current_user=mock_student_user)

print("File backend/tests/api/v1/test_student_dashboard.py created with schema tests and endpoint tests.")
