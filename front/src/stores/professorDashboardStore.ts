/**
 * @file Pinia store for Professor Dashboard state and actions.
 */
import { defineStore } from 'pinia';
import type {
  ProfessorDashboardStats,
  CoursePerformance,
  StudentEngagement,
  StudentDistributionInProfessorCourses,
  ProfessorRecentActivityItem,
} from '../types/api/professor_dashboard';
import {
  fetchProfessorDashboardStats,
  fetchProfessorPublishedCourses,
  fetchProfessorStudentEngagement,
  fetchProfessorStudentDistribution,
  fetchProfessorRecentActivities,
} from '../services/api/professorDashboardService';

/**
 * Interface for the Professor Dashboard store's state.
 */
export interface ProfessorDashboardState {
  stats: ProfessorDashboardStats | null;
  publishedCourses: CoursePerformance[];
  studentEngagement: StudentEngagement[];
  studentDistribution: StudentDistributionInProfessorCourses | null;
  recentActivities: ProfessorRecentActivityItem[];
  isLoading: boolean; // Global loading state for the whole dashboard
  error: string | null; // Global error state for the whole dashboard
}

export const useProfessorDashboardStore = defineStore('professorDashboard', {
  state: (): ProfessorDashboardState => ({
    stats: null,
    publishedCourses: [],
    studentEngagement: [],
    studentDistribution: null,
    recentActivities: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches and loads the professor's dashboard statistics.
     */
    async loadProfessorDashboardStats(): Promise<void> {
      // For individual actions, we can manage a more granular loading state if needed,
      // e.g., this.isLoadingStats = true, but for now, we use the global one.
      this.isLoading = true;
      this.error = null;
      try {
        this.stats = await fetchProfessorDashboardStats();
      } catch (err) {
        const message = err instanceof Error ? err.message : 'An unknown error occurred while fetching professor dashboard stats.';
        this.error = message; // Set global error or a specific error property like this.statsError
        console.error('Error loading professor dashboard stats:', err);
      } finally {
        // If part of loadAll, isLoading will be reset at the end of loadAll.
        // If called individually, this is correct.
        // For simplicity with loadAll, we might let loadAll manage the global isLoading.
        // However, for standalone calls, this is needed.
        // To reconcile, loadAll could set isLoading = true at start, and false at end,
        // and individual loaders don't touch global isLoading if called by loadAll.
        // For now, let's assume they all manage global isLoading for simplicity.
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads the professor's published courses.
     */
    async loadProfessorPublishedCourses(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.publishedCourses = await fetchProfessorPublishedCourses();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching published courses.';
        console.error('Error loading professor published courses:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads student engagement metrics for the professor's courses.
     */
    async loadProfessorStudentEngagement(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.studentEngagement = await fetchProfessorStudentEngagement();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching student engagement data.';
        console.error('Error loading professor student engagement:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads student distribution data in the professor's courses.
     */
    async loadProfessorStudentDistribution(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.studentDistribution = await fetchProfessorStudentDistribution();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching student distribution data.';
        console.error('Error loading professor student distribution:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches and loads recent activities related to the professor's courses.
     */
    async loadProfessorRecentActivities(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.recentActivities = await fetchProfessorRecentActivities();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An unknown error occurred while fetching recent professor activities.';
        console.error('Error loading professor recent activities:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Loads all data for the professor dashboard by calling individual load actions.
     * Uses Promise.allSettled to attempt loading all data even if some calls fail.
     */
    async loadAllProfessorDashboardData(): Promise<void> {
      this.isLoading = true;
      this.error = null; // Clear previous global errors

      const results = await Promise.allSettled([
        this.loadProfessorDashboardStats(), // These will manage their own isLoading if called directly
        this.loadProfessorPublishedCourses(), // but here they are part of a larger operation.
        this.loadProfessorStudentEngagement(),
        this.loadProfessorStudentDistribution(),
        this.loadProfessorRecentActivities(),
      ]);

      // Check for any rejected promises and log them.
      // Individual actions would have set their specific errors if needed,
      // or a global error could be aggregated here.
      results.forEach(result => {
        if (result.status === 'rejected') {
          console.error('A professor dashboard data load action failed:', result.reason);
          // If a global error message is preferred:
          if (!this.error) { // Set first error encountered as the global error
             this.error = result.reason instanceof Error ? result.reason.message : 'One or more dashboard data loads failed.';
          }
        }
      });

      this.isLoading = false; // All settled, set global loading to false.
    }
  },
  // Getters can be added here if needed
});
