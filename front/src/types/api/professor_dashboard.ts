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
  /** Average rating across all of the professor's courses. */
  average_rating: number;
  /** Total number of questions asked by students in the professor's courses. */
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
  /** Average rating of the course. */
  rating: number;
  /** Date when the course was last updated (ISO format string). */
  last_updated: string; // Or Date if transformed during/after fetch
}

/**
 * Represents student engagement metrics for a specific course.
 */
export interface StudentEngagement {
  /** Name of the course. */
  course_name: string;
  /** Average hours spent by students in the course. */
  average_hours_spent: number;
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
  /** Activity log entry unique identifier. */
  id: number;
  /** Name of the student involved in the activity. */
  student_name: string;
  /** Name of the course related to the activity. */
  course_name: string;
  /** Type of activity (e.g., "question", "comment"). */
  activity_type: string;
  /** Content of the activity (e.g., the question text or comment text). */
  content: string;
  /** Timestamp of when the activity occurred (ISO format string). */
  timestamp: string; // Or Date if transformed
}
