/**
 * @file Defines TypeScript interfaces for Student Dashboard related API data structures.
 */

/**
 * Represents statistics for the student's dashboard.
 */
export interface StudentDashboardStats {
  /** Number of courses the student is currently enrolled in. */
  enrolled_courses_count: number;
  /** Number of certificates obtained by the student. */
  certificates_count: number;
  /** Total hours spent studying by the student (e.g., overall or a specific period). */
  total_study_hours: number;
  /** Average progress percentage across all enrolled courses. */
  average_progress: number;
}

/**
 * Represents details of a course the student is enrolled in.
 */
export interface EnrolledCourseItem {
  /** Course unique identifier. */
  id: number;
  /** Title of the course. */
  title: string;
  /** Student's progress percentage in the course. */
  progress: number;
  /** Timestamp of the student's last activity in the course (ISO format string). */
  last_activity_timestamp: string;
  /** URL of the course image. */
  image_url: string;
}

/**
 * Represents the student's overall progress across courses.
 */
export interface OverallProgress {
  /** Percentage of courses completed by the student. */
  completed_percentage: number;
  /** Percentage of courses currently in progress by the student. */
  in_progress_percentage: number;
}

/**
 * Represents the student's study activity for a specific day of the week.
 */
export interface WeeklyActivityItem {
  /** Day of the week (e.g., "Mon", "Tue"). */
  day_of_week: string;
  /** Hours spent studying on that day. */
  study_hours: number;
}

/**
 * Represents details of a course recommended to the student.
 */
export interface RecommendedCourseItem {
  /** Course unique identifier. */
  id: number;
  /** Title of the recommended course. */
  title: string;
  /** Name of the course instructor. */
  instructor_name: string;
  /** Duration of the course in weeks. */
  duration_weeks: number;
  /** URL of the course image. */
  image_url: string;
  /** Category of the course. */
  category?: string;
}

/**
 * Represents details of a certificate recently obtained by the student.
 */
export interface RecentCertificateItem {
  /** Certificate unique identifier. */
  id: number;
  /** Name of the course for which the certificate was obtained. */
  course_name: string;
  /** Date when the certificate was obtained (ISO format string). */
  date_obtained: string;
}
