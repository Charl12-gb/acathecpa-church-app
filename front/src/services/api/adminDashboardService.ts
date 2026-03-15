/**
 * @file Service methods for interacting with Admin Dashboard related APIs.
 */
import apiClient from './index'; // Assuming this exports the configured Axios instance
import type {
  AdminDashboardStats,
  ProfessorStat,
  RecentActivityItem,
  UserDistribution,
  MonthlyRegistration,
} from '../../types/api/admin_dashboard'; // Corrected path if types are in ../../types/api
import type { Course } from '../../types/api/courseTypes';

const ADMIN_DASHBOARD_BASE_URL = '/admin/dashboard'; // Endpoints are relative to API_V1_STR already in apiClient

/**
 * Fetches overall statistics for the admin dashboard.
 * @returns A promise that resolves to AdminDashboardStats.
 */
export const fetchAdminDashboardStats = async (): Promise<AdminDashboardStats> => {
  try {
    const response = await apiClient.get<AdminDashboardStats>(`${ADMIN_DASHBOARD_BASE_URL}/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin dashboard stats:', error);
    // In a real app, you might throw a more specific error or return a default/error object
    throw error;
  }
};

/**
 * Fetches a list of statistics for all professors.
 * @returns A promise that resolves to an array of ProfessorStat.
 */
export const fetchAdminProfessors = async (): Promise<ProfessorStat[]> => {
  try {
    const response = await apiClient.get<ProfessorStat[]>(`${ADMIN_DASHBOARD_BASE_URL}/professors`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin professors stats:', error);
    throw error;
  }
};

export const fetchAdminProfessorCourses = async (
  professorId: number,
  skip: number = 0,
  limit: number = 100,
): Promise<Course[]> => {
  try {
    const response = await apiClient.get<Course[]>(
      `${ADMIN_DASHBOARD_BASE_URL}/professors/${professorId}/courses`,
      { params: { skip, limit } },
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching admin professor courses:', error);
    throw error;
  }
};

/**
 * Fetches a list of recent activities across the platform.
 * @returns A promise that resolves to an array of RecentActivityItem.
 */
export const fetchAdminRecentActivities = async (): Promise<RecentActivityItem[]> => {
  try {
    const response = await apiClient.get<RecentActivityItem[]>(`${ADMIN_DASHBOARD_BASE_URL}/recent-activities`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin recent activities:', error);
    throw error;
  }
};

/**
 * Fetches the distribution of users by role.
 * @returns A promise that resolves to UserDistribution.
 */
export const fetchAdminUserDistribution = async (): Promise<UserDistribution> => {
  try {
    const response = await apiClient.get<UserDistribution>(`${ADMIN_DASHBOARD_BASE_URL}/user-distribution`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin user distribution:', error);
    throw error;
  }
};

/**
 * Fetches the number of new user registrations per month.
 * @returns A promise that resolves to an array of MonthlyRegistration.
 */
export const fetchAdminMonthlyRegistrations = async (): Promise<MonthlyRegistration[]> => {
  try {
    const response = await apiClient.get<MonthlyRegistration[]>(`${ADMIN_DASHBOARD_BASE_URL}/monthly-registrations`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin monthly registrations:', error);
    throw error;
  }
};
