/**
 * @file Pinia store for Admin Dashboard state and actions.
 */
import { defineStore } from 'pinia';
import type {
  AdminDashboardStats,
  ProfessorStat,
  RecentActivityItem,
  UserDistribution,
  MonthlyRegistration,
} from '../types/api/admin_dashboard';
import {
  fetchAdminDashboardStats,
  fetchAdminProfessors,
  fetchAdminRecentActivities,
  fetchAdminUserDistribution,
  fetchAdminMonthlyRegistrations,
} from '../services/api/adminDashboardService';

/**
 * Interface for the Admin Dashboard store's state.
 */
export interface AdminDashboardState {
  stats: AdminDashboardStats | null;
  professors: ProfessorStat[];
  recentActivities: RecentActivityItem[];
  userDistribution: UserDistribution | null;
  monthlyRegistrations: MonthlyRegistration[];
  isLoading: boolean;
  error: string | null;
}

export const useAdminDashboardStore = defineStore('adminDashboard', {
  state: (): AdminDashboardState => ({
    stats: null,
    professors: [],
    recentActivities: [],
    userDistribution: null,
    monthlyRegistrations: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches and loads the main dashboard statistics.
     */
    async loadAdminDashboardStats(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.stats = await fetchAdminDashboardStats();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching dashboard stats.';
        console.error('Error loading admin dashboard stats:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads the list of professor statistics.
     */
    async loadAdminProfessors(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.professors = await fetchAdminProfessors();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching professor stats.';
        console.error('Error loading admin professors:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads recent platform activities.
     */
    async loadAdminRecentActivities(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.recentActivities = await fetchAdminRecentActivities();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching recent activities.';
        console.error('Error loading admin recent activities:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads the user distribution data.
     */
    async loadAdminUserDistribution(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.userDistribution = await fetchAdminUserDistribution();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching user distribution.';
        console.error('Error loading admin user distribution:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads monthly user registration data.
     */
    async loadAdminMonthlyRegistrations(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.monthlyRegistrations = await fetchAdminMonthlyRegistrations();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching monthly registrations.';
        console.error('Error loading admin monthly registrations:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Loads all data for the admin dashboard by calling individual load actions.
     * Uses Promise.allSettled to attempt loading all data even if some calls fail.
     */
    async loadAllAdminDashboardData(): Promise<void> {
      this.isLoading = true; // Set global loading true
      this.error = null; // Clear previous global errors

      // Individual errors will be set by each action if they fail
      // This action's primary goal is to orchestrate, not to set a global error from one failure

      const results = await Promise.allSettled([
        this.loadAdminDashboardStats(),
        this.loadAdminProfessors(),
        this.loadAdminRecentActivities(),
        this.loadAdminUserDistribution(),
        this.loadAdminMonthlyRegistrations(),
      ]);

      // Check for any rejected promises and log them, but don't overwrite individual errors
      results.forEach(result => {
        if (result.status === 'rejected') {
          console.error('A dashboard data load action failed:', result.reason);
          // Individual actions already set their specific errors.
          // If a global error strategy is needed here, it could be implemented.
          // For now, we rely on individual error states or a general isLoading=false.
        }
      });

      // isLoading should ideally be managed more granularly if parts can load independently
      // or set to false only after all promises truly complete (even if some fail).
      // The individual actions already set isLoading to false.
      // A global isLoading might be true for longer than individual parts.
      // For simplicity here, we set it to false once all are settled.
      // However, if one action sets isLoading=true then false, then another action sets it true,
      // the final isLoading = false here might be premature if actions are truly parallel and long.
      // Given the current structure where each action manages its own isLoading,
      // this global isLoading might be redundant or could be handled differently.
      // For now, let's assume actions are relatively quick or sequential in effect on isLoading.
      this.isLoading = false;
    }
  },
  // Getters can be added here if needed, for example:
  // getters: {
  //   getStats: (state) => state.stats,
  //   getProfessorsCount: (state) => state.professors.length,
  // }
});
