import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status, HTTPException # For status codes

# Assuming your FastAPI app instance is accessible for TestClient
# from app.main import app # Adjust if your app instance is elsewhere
# For now, let's assume a way to get the router or app
# If app.main imports routers, it might cause issues if not structured for tests.
# A common pattern is to have a create_app function.
# For this task, I'll focus on testing the router instance directly if possible,
# or assume 'app' can be imported. Let's mock the app for now.

from app.routers.course_router import router as course_router
from app.schemas.enrollment import EnrollmentProgress
from app.schemas.certificate import CertificateDisplay
from app.schemas.course_test import TestSubmissionWithScoreSchema, TestQuestionAttemptSummaryInputSchema # For request body
from app.models.user import User as UserModel # For current_user mock
from app.models.enrollments import Enrollment as EnrollmentModel # For service return mock
from app.models.certificate import Certificate as CertificateModel # For service return mock

# Create a new FastAPI app instance and include the router for isolated testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(course_router)


class TestCourseRouterProgress(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app) # Use the app with our router
        self.course_id = 1
        self.lesson_id = 101
        self.section_id = 201
        self.test_id = 301

        # Mock current user
        self.mock_user = UserModel(id=1, email="test@example.com", name="Test User", is_active=True)

        # Default headers for authenticated user
        self.auth_headers = {"Authorization": "Bearer faketoken"}


    # --- Test GET /{course_id}/me/progress ---
    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.get_enrollment')
    def test_get_my_course_progress_success(self, mock_get_enrollment, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        mock_enrollment_data = EnrollmentModel(
            user_id=self.mock_user.id, course_id=self.course_id, progress_percentage=50.0,
            completed_lessons=[1], completed_sections=[2],
            test_attempts=[], test_scores=[]
        )
        mock_get_enrollment.return_value = mock_enrollment_data

        response = self.client.get(f"/api/v1/courses/{self.course_id}/me/progress", headers=self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['user_id'], self.mock_user.id)
        self.assertEqual(data['course_id'], self.course_id)
        self.assertEqual(data['progress_percentage'], 50.0)
        mock_get_enrollment.assert_called_once_with(mock_db_session, user_id=self.mock_user.id, course_id=self.course_id)

    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.get_enrollment')
    def test_get_my_course_progress_not_enrolled(self, mock_get_enrollment, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_get_db.return_value = MagicMock()
        mock_get_enrollment.return_value = None # Simulate not enrolled

        response = self.client.get(f"/api/v1/courses/{self.course_id}/me/progress", headers=self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Test POST /{course_id}/lessons/{lesson_id}/complete ---
    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.mark_lesson_completed')
    def test_mark_lesson_as_completed_success(self, mock_mark_lesson, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        mock_enrollment_data = EnrollmentModel(user_id=self.mock_user.id, course_id=self.course_id, progress_percentage=10.0, completed_lessons=[self.lesson_id])
        mock_mark_lesson.return_value = mock_enrollment_data

        response = self.client.post(f"/api/v1/courses/{self.course_id}/lessons/{self.lesson_id}/complete", headers=self.auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['completed_lessons'], [self.lesson_id])
        mock_mark_lesson.assert_called_once_with(mock_db_session, user_id=self.mock_user.id, course_id=self.course_id, lesson_id=self.lesson_id)

    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.mark_lesson_completed')
    def test_mark_lesson_as_completed_not_found(self, mock_mark_lesson, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_get_db.return_value = MagicMock()
        mock_mark_lesson.return_value = None # Simulate enrollment not found or lesson already completed leading to None

        response = self.client.post(f"/api/v1/courses/{self.course_id}/lessons/{self.lesson_id}/complete", headers=self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Similar tests for POST /{course_id}/sections/{section_id}/complete would follow

    # --- Test POST /{course_id}/tests/{test_id}/attempt ---
    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.get_enrollment') # For the pre-check in router
    @patch('app.routers.course_router.course_service.record_test_attempt')
    def test_submit_test_attempt_success(self, mock_record_attempt, mock_get_enrollment_check, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        # Simulate enrollment exists for the pre-check
        mock_get_enrollment_check.return_value = MagicMock(spec=EnrollmentModel)

        mock_updated_enrollment = EnrollmentModel(user_id=self.mock_user.id, course_id=self.course_id, test_attempts=[{"test_id": self.test_id, "score": 80.0}])
        mock_record_attempt.return_value = mock_updated_enrollment

        submission_payload = {"score": 80.0, "passed": True, "questions_summary": [{"question_id": 1, "is_correct": True}]}

        response = self.client.post(
            f"/api/v1/courses/{self.course_id}/tests/{self.test_id}/attempt",
            json=submission_payload,
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()['test_attempts']) > 0)
        mock_record_attempt.assert_called_once()
        # We could also assert the arguments passed to mock_record_attempt if needed for more detail

    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.get_enrollment') # For the pre-check in router
    @patch('app.routers.course_router.course_service.record_test_attempt')
    def test_submit_test_attempt_rerun_success(self, mock_record_attempt, mock_get_enrollment_check, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session
        mock_get_enrollment_check.return_value = MagicMock(spec=EnrollmentModel)

        # First attempt response
        mock_enrollment_first_attempt = EnrollmentModel(user_id=self.mock_user.id, course_id=self.course_id, test_attempts=[{"test_id": self.test_id, "score": 70.0}])
        # Second attempt response
        mock_enrollment_second_attempt = EnrollmentModel(user_id=self.mock_user.id, course_id=self.course_id, test_attempts=[
            {"test_id": self.test_id, "score": 70.0},
            {"test_id": self.test_id, "score": 90.0} # Rerun score
        ])

        # Configure mock_record_attempt to return different values on subsequent calls if needed, or just the final state
        mock_record_attempt.side_effect = [mock_enrollment_first_attempt, mock_enrollment_second_attempt]

        submission_payload_1 = {"score": 70.0, "passed": True}
        submission_payload_2 = {"score": 90.0, "passed": True}

        # First attempt
        response1 = self.client.post(f"/api/v1/courses/{self.course_id}/tests/{self.test_id}/attempt", json=submission_payload_1, headers=self.auth_headers)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.json()['test_attempts']), 1)

        # Second attempt (rerun)
        response2 = self.client.post(f"/api/v1/courses/{self.course_id}/tests/{self.test_id}/attempt", json=submission_payload_2, headers=self.auth_headers)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.json()['test_attempts']), 2)
        self.assertEqual(mock_record_attempt.call_count, 2)


    # --- Test POST /{course_id}/me/check-certificate ---
    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.check_and_issue_certificate')
    def test_check_and_issue_certificate_success(self, mock_check_issue, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        mock_certificate = CertificateModel(id=1, user_id=self.mock_user.id, course_id=self.course_id, issue_date=datetime.utcnow())
        mock_check_issue.return_value = mock_certificate

        response = self.client.post(f"/api/v1/courses/{self.course_id}/me/check-certificate", headers=self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], mock_certificate.id)
        mock_check_issue.assert_called_once_with(mock_db_session, user_id=self.mock_user.id, course_id=self.course_id)

    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.check_and_issue_certificate')
    def test_check_and_issue_certificate_requirements_not_met(self, mock_check_issue, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_get_db.return_value = MagicMock()
        mock_check_issue.return_value = "NotAllLessonsCompleted" # Service returns a string message

        response = self.client.post(f"/api/v1/courses/{self.course_id}/me/check-certificate", headers=self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("NotAllLessonsCompleted", response.json()['detail'])

    @patch('app.routers.course_router.auth_deps.get_current_active_user')
    @patch('app.routers.course_router.auth_deps.get_db')
    @patch('app.routers.course_router.course_service.check_and_issue_certificate')
    @patch('app.routers.course_router.course_service.get_certificate_for_course_by_user') # For already issued case
    def test_check_and_issue_certificate_already_issued_fetches_existing(self, mock_get_existing_cert, mock_check_issue, mock_get_db, mock_get_current_user):
        mock_get_current_user.return_value = self.mock_user
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        mock_check_issue.return_value = "CertificateAlreadyIssued"

        # If "CertificateAlreadyIssued", the endpoint tries to fetch it
        mock_existing_certificate_data = CertificateModel(id=5, user_id=self.mock_user.id, course_id=self.course_id)
        mock_get_existing_cert.return_value = mock_existing_certificate_data

        response = self.client.post(f"/api/v1/courses/{self.course_id}/me/check-certificate", headers=self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], mock_existing_certificate_data.id)
        mock_get_existing_cert.assert_called_once_with(mock_db_session, user_id=self.mock_user.id, course_id=self.course_id)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
