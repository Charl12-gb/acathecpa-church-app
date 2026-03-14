import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { API_URL } from '../config'

export interface Course {
  id: number
  title: string
  description: string
  instructor: {
    id: number
    name: string
  }
  sections: CourseSection[]
  progress: number
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
}

export interface CourseSection {
  id: number
  title: string
  description?: string
  order: number
  lessons: CourseLesson[]
  test?: CourseTest
}

export interface CourseLesson {
  id: number
  title: string
  type: 'video' | 'text' | 'quiz'
  content: string
  duration?: string
  order: number
  completed: boolean
}

export interface CourseTest {
  id: number
  title: string
  description?: string
  duration: number
  passingScore: number
  maxAttempts: number
  questions: TestQuestion[]
}

export interface TestQuestion {
  id: number
  type: 'multiple' | 'true-false' | 'essay'
  question: string
  options?: string[]
  correctAnswer: number | boolean | null
  points: number
}

export const useCourseStore = defineStore('course', () => {
  const loading = ref(false)
  const error = ref('')
  const currentCourse = ref<Course | null>(null)
  const currentTest = ref<CourseTest | null>(null)

  // Get course details
  const getCourse = async (courseId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.get(`${API_URL}/courses/${courseId}`)
      currentCourse.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load course'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Get test details
  const getTest = async (testId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.get(`${API_URL}/tests/${testId}`)
      currentTest.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load test'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Save test
  const saveTest = async (courseId: number, sectionId: number | null, test: CourseTest) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.post(`${API_URL}/courses/${courseId}/tests`, {
        sectionId,
        test
      })
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to save test'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Mark lesson as completed
  const completedLesson = async (courseId: number, lessonId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      await axios.post(`${API_URL}/courses/${courseId}/lessons/${lessonId}/complete`)
      
      if (currentCourse.value) {
        // Update local state
        currentCourse.value.sections.forEach(section => {
          section.lessons.forEach(lesson => {
            if (lesson.id === lessonId) {
              lesson.completed = true
            }
          })
        })
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to mark lesson as completed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Submit test answers
  const submitTest = async (testId: number, answers: any[]) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.post(`${API_URL}/tests/${testId}/submit`, { answers })
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to submit test'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    currentCourse,
    currentTest,
    getCourse,
    getTest,
    saveTest,
    completedLesson,
    submitTest
  }
})