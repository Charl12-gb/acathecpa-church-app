import unittest
from unittest.mock import MagicMock, patch, call
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Set

# Models to mock (adjust imports based on actual model locations if needed)
from app.models.user import User
from app.models.course import Course, CourseStatus
from app.models.enrollments import Enrollment
from app.models.course_section import CourseSection
from app.models.course_lesson import CourseLesson
from app.models.certificate import Certificate
from app.models.course_test import CourseTest

# Schemas (for creating certificate payload)
from app.schemas.certificate import CertificateCreate

# Service functions to test
from app.services import course_service

# Helper to create a mock DB session
def get_mock_db_session():
    return MagicMock(spec=Session)

class TestCourseServiceProgress(unittest.TestCase):

    def setUp(self):
        self.db = get_mock_db_session()
        self.user_id = 1
        self.course_id = 1
        self.test_id = 101
        self.lesson_id = 201
        self.section_id = 301

        # Mock enrollment object that can be returned by get_enrollment
        self.mock_enrollment = Enrollment(
            user_id=self.user_id,
            course_id=self.course_id,
            completed_lessons=[],
            completed_sections=[],
            test_attempts=[],
            test_scores=[],
            progress_percentage=0.0,
            enrolled_at=datetime.utcnow()
        )

    @patch('app.services.course_service.get_enrollment')
    def test_record_test_attempt_first_attempt(self, mock_get_enrollment):
        mock_get_enrollment.return_value = self.mock_enrollment

        attempt_time = datetime.utcnow()
        questions_summary = [{"question_id": 1, "correct": True, "points_earned": 10}]

        result_enrollment = course_service.record_test_attempt(
            db=self.db,
            user_id=self.user_id,
            course_id=self.course_id,
            test_id=self.test_id,
            score=90.0,
            passed=True,
            questions_summary=questions_summary,
            attempted_at=attempt_time
        )

        self.assertEqual(len(result_enrollment.test_attempts), 1)
        self.assertEqual(result_enrollment.test_attempts[0]['test_id'], self.test_id)
        self.assertEqual(result_enrollment.test_attempts[0]['score'], 90.0)
        self.assertEqual(result_enrollment.test_attempts[0]['passed'], True)
        self.assertEqual(result_enrollment.test_attempts[0]['attempted_at'], attempt_time.isoformat())
        self.assertEqual(result_enrollment.test_attempts[0]['questions_summary'], questions_summary)

        self.assertEqual(len(result_enrollment.test_scores), 1)
        self.assertEqual(result_enrollment.test_scores[0]['test_id'], self.test_id)
        self.assertEqual(result_enrollment.test_scores[0]['score'], 90.0)

        self.db.add.assert_called_once_with(self.mock_enrollment)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(self.mock_enrollment)

    @patch('app.services.course_service.get_enrollment')
    def test_record_test_attempt_multiple_attempts_same_test(self, mock_get_enrollment):
        # Simulate enrollment already has one attempt
        initial_attempt_time = datetime(2023, 1, 1, 10, 0, 0)
        initial_summary = [{"question_id": 1, "correct": False, "points_earned": 0}]
        self.mock_enrollment.test_attempts = [{
            "test_id": self.test_id, "score": 50.0, "passed": False,
            "attempted_at": initial_attempt_time.isoformat(), "questions_summary": initial_summary
        }]
        self.mock_enrollment.test_scores = [{"test_id": self.test_id, "score": 50.0}]
        mock_get_enrollment.return_value = self.mock_enrollment

        # Second attempt
        new_attempt_time = datetime.utcnow()
        new_summary = [{"question_id": 1, "correct": True, "points_earned": 10}]
        result_enrollment = course_service.record_test_attempt(
            db=self.db,
            user_id=self.user_id,
            course_id=self.course_id,
            test_id=self.test_id, # Same test_id
            score=95.0,
            passed=True,
            questions_summary=new_summary,
            attempted_at=new_attempt_time
        )

        self.assertEqual(len(result_enrollment.test_attempts), 2)
        self.assertEqual(result_enrollment.test_attempts[1]['score'], 95.0)
        self.assertEqual(result_enrollment.test_attempts[1]['passed'], True)

        # Test scores should be updated (latest score for the test_id)
        self.assertEqual(len(result_enrollment.test_scores), 1)
        self.assertEqual(result_enrollment.test_scores[0]['test_id'], self.test_id)
        self.assertEqual(result_enrollment.test_scores[0]['score'], 95.0) # Updated to latest score

        self.assertEqual(self.db.add.call_count, 1)
        self.assertEqual(self.db.commit.call_count, 1)
        self.assertEqual(self.db.refresh.call_count, 1)

    @patch('app.services.course_service.get_enrollment')
    def test_record_test_attempt_multiple_attempts_different_tests(self, mock_get_enrollment):
        # Simulate enrollment already has one attempt for a different test
        other_test_id = 102
        initial_attempt_time = datetime(2023, 1, 1, 10, 0, 0)
        initial_summary = [{"question_id": 1, "correct": False, "points_earned": 0}]
        self.mock_enrollment.test_attempts = [{
            "test_id": other_test_id, "score": 50.0, "passed": False,
            "attempted_at": initial_attempt_time.isoformat(), "questions_summary": initial_summary
        }]
        self.mock_enrollment.test_scores = [{"test_id": other_test_id, "score": 50.0}]
        mock_get_enrollment.return_value = self.mock_enrollment

        # New attempt for self.test_id
        new_attempt_time = datetime.utcnow()
        new_summary = [{"question_id": 1, "correct": True, "points_earned": 10}]
        result_enrollment = course_service.record_test_attempt(
            db=self.db,
            user_id=self.user_id,
            course_id=self.course_id,
            test_id=self.test_id,
            score=90.0,
            passed=True,
            questions_summary=new_summary,
            attempted_at=new_attempt_time
        )

        self.assertEqual(len(result_enrollment.test_attempts), 2) # One for other_test_id, one for self.test_id
        self.assertEqual(result_enrollment.test_attempts[1]['test_id'], self.test_id)
        self.assertEqual(result_enrollment.test_attempts[1]['score'], 90.0)

        self.assertEqual(len(result_enrollment.test_scores), 2)
        # Ensure the new score is added and old one is retained
        scores_by_test_id = {ts['test_id']: ts['score'] for ts in result_enrollment.test_scores}
        self.assertEqual(scores_by_test_id[other_test_id], 50.0)
        self.assertEqual(scores_by_test_id[self.test_id], 90.0)


    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service._calculate_progress_percentage')
    def test_mark_lesson_completed(self, mock_calc_progress, mock_get_enrollment):
        mock_get_enrollment.return_value = self.mock_enrollment
        mock_calc_progress.return_value = 10.0 # Assume progress calculation returns 10%

        result_enrollment = course_service.mark_lesson_completed(
            db=self.db, user_id=self.user_id, course_id=self.course_id, lesson_id=self.lesson_id
        )

        self.assertIn(self.lesson_id, result_enrollment.completed_lessons)
        self.assertEqual(result_enrollment.progress_percentage, 10.0)
        mock_calc_progress.assert_called_once_with(self.db, self.mock_enrollment)
        self.db.add.assert_called_once_with(self.mock_enrollment)

    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service._calculate_progress_percentage')
    def test_mark_lesson_completed_already_completed(self, mock_calc_progress, mock_get_enrollment):
        self.mock_enrollment.completed_lessons = [self.lesson_id]
        self.mock_enrollment.progress_percentage = 10.0
        mock_get_enrollment.return_value = self.mock_enrollment

        result_enrollment = course_service.mark_lesson_completed(
            db=self.db, user_id=self.user_id, course_id=self.course_id, lesson_id=self.lesson_id
        )

        self.assertEqual(len(result_enrollment.completed_lessons), 1) # Should not add duplicate
        self.assertEqual(result_enrollment.progress_percentage, 10.0) # Should remain same
        mock_calc_progress.assert_not_called() # Progress should not be recalculated
        self.db.add.assert_not_called() # No change, no db.add

    # Similar tests for mark_section_completed

    @patch('app.services.course_service.get_enrollment')
    def test_calculate_progress_percentage_empty_course(self, mock_get_enrollment):
        # This test is more for _calculate_progress_percentage directly
        mock_course = MagicMock(spec=Course)
        mock_course.sections = [] # No sections, so no lessons

        with patch('app.services.course_service.db.query') as mock_query: # Patch query within the service module
            mock_query.return_value.options.return_value.filter.return_value.first.return_value = mock_course

            progress = course_service._calculate_progress_percentage(self.db, self.mock_enrollment)
            self.assertEqual(progress, 0.0)

    @patch('app.services.course_service.get_enrollment')
    def test_calculate_progress_percentage_basic(self, mock_get_enrollment):
        # This test is more for _calculate_progress_percentage directly
        mock_course = MagicMock(spec=Course)
        section1_lessons = [MagicMock(spec=CourseLesson) for _ in range(2)]
        section2_lessons = [MagicMock(spec=CourseLesson) for _ in range(2)]
        mock_section1 = MagicMock(spec=CourseSection, lessons=section1_lessons)
        mock_section2 = MagicMock(spec=CourseSection, lessons=section2_lessons)
        mock_course.sections = [mock_section1, mock_section2] # 2 sections, 4 lessons total

        self.mock_enrollment.completed_lessons = [section1_lessons[0].id] # 1 of 4 lessons done
        self.mock_enrollment.completed_sections = [] # 0 of 2 sections done

        with patch('app.services.course_service.db.query') as mock_query:
            mock_query.return_value.options.return_value.filter.return_value.first.return_value = mock_course

            progress = course_service._calculate_progress_percentage(self.db, self.mock_enrollment)
            # (1/4)*50 for lessons + (0/2)*50 for sections = 12.5 + 0 = 12.5
            self.assertEqual(progress, 12.5)

        self.mock_enrollment.completed_lessons = [lesson.id for lesson in section1_lessons] # 2 of 4 lessons
        self.mock_enrollment.completed_sections = [mock_section1.id] # 1 of 2 sections
        with patch('app.services.course_service.db.query') as mock_query:
            mock_query.return_value.options.return_value.filter.return_value.first.return_value = mock_course
            progress = course_service._calculate_progress_percentage(self.db, self.mock_enrollment)
            # (2/4)*50 for lessons + (1/2)*50 for sections = 25 + 25 = 50.0
            self.assertEqual(progress, 50.0)

    # --- Certificate Issuance Tests ---
    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service.get_certificate_for_course_by_user')
    @patch('app.services.course_service.create_certificate') # Mock the actual creation
    def test_check_and_issue_certificate_success(self, mock_create_cert, mock_get_existing_cert, mock_get_enrollment):
        # Setup
        mock_get_enrollment.return_value = self.mock_enrollment
        mock_get_existing_cert.return_value = None # No existing certificate

        mock_course_obj = MagicMock(spec=Course)
        mock_course_obj.id = self.course_id
        mock_course_obj.points_required_for_certificate = 50

        # Simulate course with lessons and sections
        lesson1, lesson2 = MagicMock(id=201), MagicMock(id=202)
        section1 = MagicMock(id=301, lessons=[lesson1, lesson2])
        mock_course_obj.sections = [section1]

        # Configure the mock session (self.db) to return the mock_course_obj
        self.db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_course_obj

        # Student has completed all lessons and sections
        self.mock_enrollment.completed_lessons = [201, 202]
        self.mock_enrollment.completed_sections = [301]
        # Student has enough points (example from test_scores)
        self.mock_enrollment.test_scores = [{"test_id": 101, "score": 60.0}] # score > points_required

        mock_new_certificate = MagicMock(spec=Certificate)
        mock_create_cert.return_value = mock_new_certificate

        # Action
        result = course_service.check_and_issue_certificate(self.db, self.user_id, self.course_id)

        # Assertions
        self.assertEqual(result, mock_new_certificate)
        mock_create_cert.assert_called_once()
        # Check that enrollment completed_at and progress_percentage are updated
        self.assertIsNotNone(self.mock_enrollment.completed_at)
        self.assertEqual(self.mock_enrollment.progress_percentage, 100.0)
        self.db.add.assert_called_with(self.mock_enrollment)
        self.db.commit.assert_called_once() # Should be 1 commit for enrollment + cert creation in create_certificate
        self.db.refresh.assert_called_with(self.mock_enrollment)


    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service.get_certificate_for_course_by_user')
    def test_check_and_issue_certificate_already_issued(self, mock_get_existing_cert, mock_get_enrollment):
        mock_get_enrollment.return_value = self.mock_enrollment
        mock_existing_certificate = MagicMock(spec=Certificate)
        mock_get_existing_cert.return_value = mock_existing_certificate

        # Mock course query on self.db (the mock session)
        mock_course_obj = MagicMock(spec=Course)
        self.db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_course_obj

        result = course_service.check_and_issue_certificate(self.db, self.user_id, self.course_id)
        self.assertEqual(result, "CertificateAlreadyIssued")

    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service.get_certificate_for_course_by_user')
    def test_check_and_issue_certificate_lessons_not_completed(self, mock_get_existing_cert, mock_get_enrollment):
        mock_get_enrollment.return_value = self.mock_enrollment
        mock_get_existing_cert.return_value = None

        mock_course_obj = MagicMock(spec=Course)
        lesson1, lesson2 = MagicMock(id=201), MagicMock(id=202)
        section1 = MagicMock(id=301, lessons=[lesson1, lesson2])
        mock_course_obj.sections = [section1]
        self.db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_course_obj

        self.mock_enrollment.completed_lessons = [201] # Missing lesson 202

        result = course_service.check_and_issue_certificate(self.db, self.user_id, self.course_id)
        self.assertEqual(result, "NotAllLessonsCompleted")

    @patch('app.services.course_service.get_enrollment')
    @patch('app.services.course_service.get_certificate_for_course_by_user')
    def test_check_and_issue_certificate_points_not_met(self, mock_get_existing_cert, mock_get_enrollment):
        mock_get_enrollment.return_value = self.mock_enrollment
        mock_get_existing_cert.return_value = None

        mock_course_obj = MagicMock(spec=Course)
        mock_course_obj.points_required_for_certificate = 100
        lesson1 = MagicMock(id=201)
        section1 = MagicMock(id=301, lessons=[lesson1])
        mock_course_obj.sections = [section1]
        self.db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_course_obj

        self.mock_enrollment.completed_lessons = [201]
        self.mock_enrollment.completed_sections = [301]
        self.mock_enrollment.test_scores = [{"test_id": 101, "score": 50.0}] # score < points_required

        result = course_service.check_and_issue_certificate(self.db, self.user_id, self.course_id)
        self.assertEqual(result, "PointsNotMet:50.0/100")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Note: To run this in a notebook or similar, you might need to adjust how unittest.main is called.
# For a proper test suite, this would be run by a test runner like pytest or 'python -m unittest'.
