from pydantic import BaseModel, Field
from typing import List, Optional

# Schemas for Student Dashboard

class StudentDashboardStats(BaseModel):
    """Statistics for the student's dashboard."""
    enrolled_courses_count: int = Field(..., description="Number of courses the student is currently enrolled in.")
    certificates_count: int = Field(..., description="Number of certificates obtained by the student.")
    total_study_hours: float = Field(..., description="Total hours spent studying by the student (overall).")
    average_progress: float = Field(..., ge=0, le=100, description="Average progress percentage across all enrolled courses.")

class EnrolledCourse(BaseModel):
    """Details of a course the student is enrolled in."""
    id: int = Field(..., description="Course unique identifier.")
    title: str = Field(..., description="Title of the course.")
    progress: int = Field(..., ge=0, le=100, description="Student's progress percentage in the course.")
    last_activity_timestamp: str = Field(..., description="Timestamp of the student's last activity in the course (ISO format string).") # Or datetime
    image_url: str = Field(..., description="URL of the course image.")

class OverallProgress(BaseModel):
    """Overall progress of the student."""
    completed_percentage: int = Field(..., ge=0, le=100, description="Percentage of courses completed by the student.")
    in_progress_percentage: int = Field(..., ge=0, le=100, description="Percentage of courses currently in progress by the student.")

class WeeklyActivity(BaseModel):
    """Student's study activity for a day of the week."""
    day_of_week: str = Field(..., description="Day of the week (e.g., 'Mon', 'Tue').")
    study_hours: float = Field(..., ge=0, description="Hours spent studying on that day.")

class RecommendedCourse(BaseModel):
    """Details of a course recommended to the student."""
    id: int = Field(..., description="Course unique identifier.")
    title: str = Field(..., description="Title of the recommended course.")
    instructor_name: str = Field(..., description="Name of the course instructor.")
    duration_weeks: int = Field(..., gt=0, description="Duration of the course in weeks.") # Or string like "8 semaines"
    image_url: str = Field(..., description="URL of the course image.")
    category: str = Field(..., description="Category of the course.")

class RecentCertificate(BaseModel):
    """Details of a recently obtained certificate."""
    id: int = Field(..., description="Certificate unique identifier.")
    course_name: str = Field(..., description="Name of the course for which the certificate was obtained.")
    date_obtained: str = Field(..., description="Date when the certificate was obtained (ISO format string).") # Or date
