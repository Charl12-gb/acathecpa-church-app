/**
 * @file Service methods for interacting with Professor Dashboard related APIs.
 */
import apiClient from './index'; // The configured Axios instance
import type {
  ProfessorDashboardStats,
  CoursePerformance,
  StudentEngagement,
  StudentDistributionInProfessorCourses,
  ProfessorRecentActivityItem,
} from '../../types/api/professor_dashboard';

// Base URL for professor dashboard specific endpoints
// apiClient already has /api/v1, and professor router is mounted at /professors
const PROFESSOR_DASHBOARD_BASE_URL = '/professors/dashboard';

/**
 * Fetches overall statistics for the professor's dashboard.
 * @returns A promise that resolves to ProfessorDashboardStats.
 */
export const fetchProfessorDashboardStats = async (): Promise<ProfessorDashboardStats> => {
  try {
    const response = await apiClient.get<ProfessorDashboardStats>(`${PROFESSOR_DASHBOARD_BASE_URL}/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching professor dashboard stats:', error);
    throw error; // Re-throw to be handled by the caller (e.g., Pinia store)
  }
};

/**
 * Fetches performance metrics for courses published by the logged-in professor.
 * @returns A promise that resolves to an array of CoursePerformance.
 */
export const fetchProfessorPublishedCourses = async (): Promise<CoursePerformance[]> => {
  try {
    const response = await apiClient.get<CoursePerformance[]>(`${PROFESSOR_DASHBOARD_BASE_URL}/published-courses`);
    return response.data;
  } catch (error) {
    console.error('Error fetching professor published courses:', error);
    throw error;
  }
};

/**
 * Fetches student engagement metrics for the logged-in professor's courses.
 * @returns A promise that resolves to an array of StudentEngagement.
 */
export const fetchProfessorStudentEngagement = async (): Promise<StudentEngagement[]> => {
  try {
    const response = await apiClient.get<StudentEngagement[]>(`${PROFESSOR_DASHBOARD_BASE_URL}/student-engagement`);
    return response.data;
  } catch (error) {
    console.error('Error fetching professor student engagement:', error);
    throw error;
  }
};

/**
 * Fetches the distribution of students (active, inactive, completed) in the logged-in professor's courses.
 * @returns A promise that resolves to StudentDistributionInProfessorCourses.
 */
export const fetchProfessorStudentDistribution = async (): Promise<StudentDistributionInProfessorCourses> => {
  try {
    const response = await apiClient.get<StudentDistributionInProfessorCourses>(`${PROFESSOR_DASHBOARD_BASE_URL}/student-distribution`);
    return response.data;
  } catch (error) {
    console.error('Error fetching professor student distribution:', error);
    throw error;
  }
};

/**
 * Fetches recent activities (questions, comments) related to the logged-in professor's courses.
 * @returns A promise that resolves to an array of ProfessorRecentActivityItem.
 */
export const fetchProfessorRecentActivities = async (): Promise<ProfessorRecentActivityItem[]> => {
  try {
    const response = await apiClient.get<ProfessorRecentActivityItem[]>(`${PROFESSOR_DASHBOARD_BASE_URL}/recent-activities`);
    return response.data;
  } catch (error) {
    console.error('Error fetching professor recent activities:', error);
    throw error;
  }
};
