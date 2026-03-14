/**
 * @file Defines TypeScript interfaces for Admin Dashboard related API data structures.
 */

/**
 * Represents overall statistics for the admin dashboard.
 */
export interface AdminDashboardStats {
  /** Total number of users in the system. */
  total_users: number;
  /** Total number of professors. */
  total_professors: number;
  /** Total number of courses offered. */
  total_courses: number;
  /** Number of new course enrollments in the last month. */
  new_enrollments_last_month: number;
}

/**
 * Represents statistics for a single professor, typically used in lists on the admin dashboard.
 */
export interface ProfessorStat {
  /** Professor's unique identifier. */
  id: number;
  /** Professor's full name. */
  name: string;
  /** Professor's email address. */
  email: string;
  /** Number of courses taught by the professor. */
  courses_count: number;
  /** Total number of students enrolled in the professor's courses. */
  students_count: number;
  /** Average rating of the professor's courses. */
  average_rating: number;
}

/**
 * Represents a single recent activity item in the system.
 */
export interface RecentActivityItem {
  /** Activity log entry unique identifier. */
  id: number;
  /** Name of the user who performed the action. */
  user_name: string;
  /** Description of the action performed (e.g., 'created_course', 'enrolled_in_section'). */
  action: string;
  /** Name of the resource involved (e.g., course title, section name). */
  resource_name: string;
  /** Timestamp of when the activity occurred (ISO format string). */
  timestamp: string;
}

/**
 * Represents the distribution of users by role.
 */
export interface UserDistribution {
  /** Total number of students. */
  students_count: number;
  /** Total number of professors. */
  professors_count: number;
  /** Total number of administrators. */
  admins_count: number;
}

/**
 * Represents the number of user registrations for a specific month.
 */
export interface MonthlyRegistration {
  /** Month identifier (e.g., "Jan", "Feb", "Mar"). */
  month: string;
  /** Number of registrations in that month. */
  count: number;
}
