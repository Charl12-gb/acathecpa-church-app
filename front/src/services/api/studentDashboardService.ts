/**
 * @file Service methods for interacting with Student Dashboard related APIs.
 */
import apiClient from './index'; // The configured Axios instance
import type {
  StudentDashboardStats,
  EnrolledCourseItem,
  OverallProgress,
  WeeklyActivityItem,
  RecommendedCourseItem,
  RecentCertificateItem,
} from '../../types/api/student_dashboard';

// Base URL for student dashboard specific endpoints
// apiClient already has /api/v1, and student router is mounted at /student/dashboard
const STUDENT_DASHBOARD_BASE_URL = '/student/dashboard';

/**
 * Fetches statistics for the student's dashboard.
 * @returns A promise that resolves to StudentDashboardStats.
 */
export const fetchStudentDashboardStats = async (): Promise<StudentDashboardStats> => {
  try {
    const response = await apiClient.get<StudentDashboardStats>(`${STUDENT_DASHBOARD_BASE_URL}/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student dashboard stats:', error);
    throw error;
  }
};

/**
 * Fetches the list of courses the student is enrolled in.
 * @returns A promise that resolves to an array of EnrolledCourseItem.
 */
export const fetchStudentEnrolledCourses = async (): Promise<EnrolledCourseItem[]> => {
  try {
    const response = await apiClient.get<EnrolledCourseItem[]>(`${STUDENT_DASHBOARD_BASE_URL}/enrolled-courses`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student enrolled courses:', error);
    throw error;
  }
};

/**
 * Fetches the student's overall progress.
 * @returns A promise that resolves to OverallProgress.
 */
export const fetchStudentOverallProgress = async (): Promise<OverallProgress> => {
  try {
    const response = await apiClient.get<OverallProgress>(`${STUDENT_DASHBOARD_BASE_URL}/overall-progress`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student overall progress:', error);
    throw error;
  }
};

/**
 * Fetches the student's study activity for the week.
 * @returns A promise that resolves to an array of WeeklyActivityItem.
 */
export const fetchStudentWeeklyActivity = async (): Promise<WeeklyActivityItem[]> => {
  try {
    const response = await apiClient.get<WeeklyActivityItem[]>(`${STUDENT_DASHBOARD_BASE_URL}/weekly-activity`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student weekly activity:', error);
    throw error;
  }
};

/**
 * Fetches a list of courses recommended for the student.
 * @returns A promise that resolves to an array of RecommendedCourseItem.
 */
export const fetchStudentRecommendedCourses = async (): Promise<RecommendedCourseItem[]> => {
  try {
    const response = await apiClient.get<RecommendedCourseItem[]>(`${STUDENT_DASHBOARD_BASE_URL}/recommended-courses`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student recommended courses:', error);
    throw error;
  }
};

/**
 * Fetches a list of certificates recently obtained by the student.
 * @returns A promise that resolves to an array of RecentCertificateItem.
 */
export const fetchStudentRecentCertificates = async (): Promise<RecentCertificateItem[]> => {
  try {
    const response = await apiClient.get<RecentCertificateItem[]>(`${STUDENT_DASHBOARD_BASE_URL}/recent-certificates`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student recent certificates:', error);
    throw error;
  }
};
