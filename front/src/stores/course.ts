import { defineStore } from 'pinia'
import apiClient from '../services/api'
import { CourseTest } from '../types/api'

export const useCourseStore = defineStore('course', {
  state: () => ({
    loading: false,
    error: '',
    currentCourse: null as any,
    currentTest: null as CourseTest | null,
  }),
  actions: {
    // Get course details
    async getCourse(courseId: number) {
      this.loading = true
      this.error = ''

      try {
        const response = await apiClient.get(`/courses/${courseId}`)
        this.currentCourse = response.data
      } catch (err: any) {
        this.error = err.message || 'Failed to load course'
        throw this.error
      } finally {
        this.loading = false
      }
    },

    // Get test details
    async getTest(testId: number) {
      this.loading = true
      this.error = ''

      try {
        const response = await apiClient.get(`/courses/tests/${testId}`)
        this.currentTest = response.data
      } catch (err: any) {
        this.error = err.message || 'Failed to load test'
        throw this.error
      } finally {
        this.loading = false
      }
    },

    // Save test
    async saveTest(_courseId: number, sectionId: number | null, test: CourseTest) {
      this.loading = true
      this.error = ''

      try {
        const response = await apiClient.post(`/courses/sections/${sectionId}/tests/`, test)
        return response.data
      } catch (err: any) {
        this.error = err.message || 'Failed to save test'
        throw this.error
      } finally {
        this.loading = false
      }
    },

    // Mark lesson as completed
    async completedLesson(courseId: number, lessonId: number) {
      this.loading = true
      this.error = ''
      
      try {
        await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/complete`)

        if (this.currentCourse) {
          // Update local state
          this.currentCourse.sections.forEach((section: any) => {
            section.lessons.forEach((lesson: any) => {
              if (lesson.id === lessonId) {
                lesson.is_completed = true
              }
            })
          })
        }
      } catch (err: any) {
        this.error = err.message || 'Failed to mark lesson as completed'
        throw this.error
      } finally {
        this.loading = false
      }
    },

    // Submit test answers
    async submitTest(courseId: number, testId: number, answers: any[]) {
      this.loading = true
      this.error = ''

      try {
        const response = await apiClient.post(`/courses/${courseId}/tests/${testId}/attempt`, { answers })
        return response.data
      } catch (err: any) {
        this.error = err.message || 'Failed to submit test'
        throw this.error
      } finally {
        this.loading = false
      }
    }
  }
})
