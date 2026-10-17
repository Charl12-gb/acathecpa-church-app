/**
 * @file Defines TypeScript interfaces for Professor Dashboard related API data structures.
 */

/**
 * Represents overall statistics for the professor's dashboard.
 */
export interface ProfessorDashboardStats {
  /** Number of courses published by the professor. */
  published_courses_count: number;
  /** Total number of students enrolled in all of the professor's courses. */
  total_students_count: number;
  /** Certificates earned in the professor's courses. */
  certificates_count: number;
  /** Completed payments for the professor's courses (XOF). */
  revenue: number;
  /** Number of quiz questions written by the professor. */
  total_questions_count: number;
}

/**
 * Represents performance metrics for a specific course taught by the professor.
 */
export interface CoursePerformance {
  /** Course unique identifier. */
  id: number;
  /** Title of the course. */
  title: string;
  /** Number of students enrolled in the course. */
  students_count: number;
  /** Average progress of the course's students (0-100). */
  average_progress: number;
  /** Date when the course was last updated (ISO format string). */
  last_updated: string; // Or Date if transformed during/after fetch
}

/**
 * Represents student engagement metrics for a specific course.
 */
export interface StudentEngagement {
  /** Name of the course. */
  course_name: string;
  /** Average progress of the course's students (0-100). */
  average_progress: number;
}

/**
 * Represents the distribution of students in a professor's courses by their status.
 */
export interface StudentDistributionInProfessorCourses {
  /** Number of students currently active in courses. */
  active_students_count: number;
  /** Number of students who were active but are now inactive. */
  inactive_students_count: number;
  /** Number of students who have completed courses. */
  completed_students_count: number;
}

/**
 * Represents a single recent activity item related to a professor's courses or students.
 */
export interface ProfessorRecentActivityItem {
  /** Activity unique identifier, e.g. "enroll-12". */
  id: string;
  /** Name of the student involved in the activity. */
  student_name: string;
  /** Name of the course related to the activity. */
  course_name: string;
  /** "enrollment", "quiz" or "certificate". */
  activity_type: 'enrollment' | 'quiz' | 'certificate';
  /** Content of the activity (e.g., the question text or comment text). */
  content: string;
  /** Timestamp of when the activity occurred (ISO format string). */
  timestamp: string; // Or Date if transformed
}
