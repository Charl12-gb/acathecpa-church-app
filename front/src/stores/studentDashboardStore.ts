/**
 * @file Pinia store for Student Dashboard state and actions.
 */
import { defineStore } from 'pinia';
import type {
  StudentDashboardStats,
  EnrolledCourseItem,
  OverallProgress,
  WeeklyActivityItem,
  RecommendedCourseItem,
  RecentCertificateItem,
} from '../types/api/student_dashboard';
import {
  fetchStudentDashboardStats,
  fetchStudentEnrolledCourses,
  fetchStudentOverallProgress,
  fetchStudentWeeklyActivity,
  fetchStudentRecommendedCourses,
  fetchStudentRecentCertificates,
} from '../services/api/studentDashboardService';

/**
 * Interface for the Student Dashboard store's state.
 */
export interface StudentDashboardState {
  stats: StudentDashboardStats | null;
  enrolledCourses: EnrolledCourseItem[];
  overallProgress: OverallProgress | null;
  weeklyActivity: WeeklyActivityItem[];
  recommendedCourses: RecommendedCourseItem[];
  recentCertificates: RecentCertificateItem[];
  isLoading: boolean;
  error: string | null;
}

export const useStudentDashboardStore = defineStore('studentDashboard', {
  state: (): StudentDashboardState => ({
    stats: null,
    enrolledCourses: [],
    overallProgress: null,
    weeklyActivity: [],
    recommendedCourses: [],
    recentCertificates: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async loadStudentDashboardStats(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.stats = await fetchStudentDashboardStats();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load dashboard stats.';
        console.error('Error loading student dashboard stats:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async loadStudentEnrolledCourses(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.enrolledCourses = await fetchStudentEnrolledCourses();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load enrolled courses.';
        console.error('Error loading student enrolled courses:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async loadStudentOverallProgress(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.overallProgress = await fetchStudentOverallProgress();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load overall progress.';
        console.error('Error loading student overall progress:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async loadStudentWeeklyActivity(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.weeklyActivity = await fetchStudentWeeklyActivity();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load weekly activity.';
        console.error('Error loading student weekly activity:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async loadStudentRecommendedCourses(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.recommendedCourses = await fetchStudentRecommendedCourses();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load recommended courses.';
        console.error('Error loading student recommended courses:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async loadStudentRecentCertificates(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        this.recentCertificates = await fetchStudentRecentCertificates();
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to load recent certificates.';
        console.error('Error loading student recent certificates:', err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Loads all data for the student dashboard.
     */
    async loadAllStudentDashboardData(): Promise<void> {
      this.isLoading = true;
      this.error = null;

      const results = await Promise.allSettled([
        this.loadStudentDashboardStats(),
        this.loadStudentEnrolledCourses(),
        this.loadStudentOverallProgress(),
        this.loadStudentWeeklyActivity(),
        this.loadStudentRecommendedCourses(),
        this.loadStudentRecentCertificates(),
      ]);

      results.forEach(result => {
        if (result.status === 'rejected') {
          console.error('A student dashboard data load action failed:', result.reason);
          if (!this.error) { // Set first error encountered
            this.error = result.reason instanceof Error ? result.reason.message : 'One or more student dashboard data loads failed.';
          }
        }
      });

      this.isLoading = false;
    }
  },
});
