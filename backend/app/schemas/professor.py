from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
class EducationEntryBase(BaseModel):
    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field_of_study: Optional[str] = None
    start_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    end_year: Optional[int] = Field(default=None, ge=1900, le=2100) 
    description: Optional[str] = None

class EducationEntry(EducationEntryBase):
    pass

class ExperienceEntryBase(BaseModel):
    company: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class ExperienceEntry(ExperienceEntryBase):
    pass

class SocialLinksBase(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    orcid: Optional[str] = None
    google_scholar: Optional[str] = None

class SocialLinks(SocialLinksBase):
    pass

class ProfessorProfileBase(BaseModel):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[List[EducationEntry]] = Field(default_factory=list)
    experience: Optional[List[ExperienceEntry]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    social_links: Optional[SocialLinks] = Field(default_factory=SocialLinks)


class ProfessorProfileCreateForExistingUser(ProfessorProfileBase):
    specialization: str = Field(..., min_length=1)

class ProfessorProfileUpdate(ProfessorProfileBase):
    pass

class ProfessorProfileInDBBase(ProfessorProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True 

class ProfessorProfile(ProfessorProfileInDBBase):
    pass


# Schemas for Admin Dashboard
class AdminDashboardStats(BaseModel):
    """Statistics for the admin dashboard."""
    total_users: int = Field(..., description="Total number of users in the system.")
    total_professors: int = Field(..., description="Total number of professors.")
    total_courses: int = Field(..., description="Total number of courses offered.")
    new_enrollments_last_month: int = Field(..., description="Number of new course enrollments in the last month.")


class ProfessorStats(BaseModel):
    """Statistics for a specific professor."""
    id: int = Field(..., description="Professor's unique identifier.")
    name: str = Field(..., description="Professor's full name.")
    email: str = Field(..., description="Professor's email address.")
    courses_count: int = Field(..., description="Number of courses taught by the professor.")
    published_courses_count: int = Field(..., description="Number of published courses by the professor.")
    students_count: int = Field(..., description="Total number of students enrolled in the professor's courses.")
    active_students_count: int = Field(..., description="Number of active students enrolled in the professor's courses.")
    average_rating: float = Field(..., description="Average rating of the professor's courses.")
    specialization: Optional[str] = Field(default=None, description="Professor specialization.")
    phone: Optional[str] = Field(default=None, description="Professor phone number.")
    is_active: bool = Field(..., description="Whether the professor account is active.")
    latest_course_published_at: Optional[str] = Field(default=None, description="Latest published course date in ISO format.")


class RecentActivity(BaseModel):
    """Represents a recent activity log entry."""
    id: str = Field(..., description="Activity log entry unique identifier.")
    user_name: str = Field(..., description="Name of the user who performed the action.")
    action: str = Field(..., description="Description of the action performed (e.g., 'created_course', 'enrolled_in_section').")
    resource_name: str = Field(..., description="Name of the resource involved (e.g., course title, section name).")
    timestamp: str = Field(..., description="Timestamp of when the activity occurred (ISO format string).") # Or datetime


class UserDistribution(BaseModel):
    """Distribution of users by role."""
    students_count: int = Field(..., description="Total number of students.")
    professors_count: int = Field(..., description="Total number of professors.")
    admins_count: int = Field(..., description="Total number of administrators.")


class MonthlyRegistration(BaseModel):
    """Number of registrations for a specific month."""
    month: str = Field(..., description="Month (e.g., 'Jan', 'Feb').")
    count: int = Field(..., description="Number of registrations in that month.")


# Schemas for Professor Dashboard
class ProfessorDashboardStats(BaseModel):
    """Statistics for the professor's dashboard."""
    published_courses_count: int = Field(..., description="Number of courses published by the professor.")
    total_students_count: int = Field(..., description="Total number of students enrolled in all of the professor's courses.")
    average_rating: float = Field(..., description="Average rating across all of the professor's courses.")
    total_questions_count: int = Field(..., description="Total number of questions asked by students in the professor's courses.")


class CoursePerformance(BaseModel):
    """Performance metrics for a specific course."""
    id: int = Field(..., description="Course unique identifier.")
    title: str = Field(..., description="Title of the course.")
    students_count: int = Field(..., description="Number of students enrolled in the course.")
    rating: float = Field(..., description="Average rating of the course.")
    last_updated: str = Field(..., description="Date when the course was last updated (ISO format string).") # Or date/datetime


class StudentEngagement(BaseModel):
    """Student engagement metrics for a course."""
    course_name: str = Field(..., description="Name of the course.")
    average_hours_spent: float = Field(..., description="Average hours spent by students in the course.")


class StudentDistributionInProfessorCourses(BaseModel):
    """Distribution of students in a professor's courses by status."""
    active_students_count: int = Field(..., description="Number of students currently active in courses.")
    inactive_students_count: int = Field(..., description="Number of students who were active but are now inactive.")
    completed_students_count: int = Field(..., description="Number of students who have completed courses.")


class ProfessorRecentActivity(BaseModel):
    """Represents a recent activity related to a professor's courses or students."""
    id: int = Field(..., description="Activity log entry unique identifier.")
    student_name: str = Field(..., description="Name of the student involved in the activity.")
    course_name: str = Field(..., description="Name of the course related to the activity.")
    activity_type: str = Field(..., description="Type of activity (e.g., 'question', 'comment').")
    content: str = Field(..., description="Content of the activity (e.g., the question text or comment text).")
    timestamp: str = Field(..., description="Timestamp of when the activity occurred (ISO format string).") # Or datetime
