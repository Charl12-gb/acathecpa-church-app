import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
// import axios from 'axios' // Removed axios
// import { API_URL } from '../config' // Removed API_URL
import {
  login as apiLogin,
  register as apiRegister,
  getMe as apiGetMe,
  requestPasswordReset as apiRequestPasswordReset, // Added
  resetPassword as apiResetPassword // Added
} from '../services/api/auth'
import router from '../router'

export interface User {
  id: number
  name: string
  email: string
  phone?: string
  role: {
    name: 'student' | 'professor' | 'admin' | 'super_admin'
  }
  country?: string
  birthdate?: string
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref('')

  // Load token from localStorage on initialization
  const storedToken = localStorage.getItem('token')
  const storedUser = localStorage.getItem('user')
  
  if (storedToken) {
    token.value = storedToken
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  }

  // Computed
  const isAuthenticated = computed(() => !!token.value)
  
  const hasRole = (role: string | string[]) => {
    if (!user.value) return false
    
    if (Array.isArray(role)) {
      return role.includes(user.value.role?.name)
    }
    
    return user.value.role?.name === role
  }

  // Actions
  const login = async (identifier: string, password: string) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await apiLogin({ username: identifier, password })
      
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('refreshToken', response.refresh_token)
      
      const userDetails = await apiGetMe()
      user.value = userDetails
      localStorage.setItem('user', JSON.stringify(userDetails))
      
      // The API client interceptor handles setting the Authorization header
      router.push('/dashboard')
    } catch (err: any) {
      error.value = "Mot de passe ou identifiant incorrect"
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: {
    name: string
    email: string
    phone: string
    country: string
    birthdate: string
    password: string
  }) => {
    loading.value = true
    error.value = '' // Ensure error is cleared at the start
    
    try {
      // Call apiRegister - Note: apiRegister in services returns User
      await apiRegister(userData)
      
      // Registration successful, redirect to login page
      router.push('/login')
      // Optionally, set a success message here for the login page to display
      // e.g., someStore.setSuccessMessage('Registration successful! Please log in.')

    } catch (err: any) {
      // Ensure error.value is set appropriately from the caught error
      if (err.response && err.response.data && err.response.data.detail) {
        error.value = err.response.data.detail;
      } else if (err.message) {
        error.value = err.message;
      } else {
        error.value = 'Registration failed due to an unknown error.';
      }
    } finally {
      loading.value = false // Ensure loading is set to false in finally block
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // The API client interceptor handles setting/unsetting the Authorization header
    // or rather, requests made without a token won't have the header.
    router.push('/login')
  }

  const requestPasswordReset = async (email: string) => {
    try {
      const response = await apiRequestPasswordReset(email)
      return response.message // Assuming the backend returns a message
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to request password reset')
    }
  }

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      const response = await apiResetPassword(token, newPassword)
      return response.message // Assuming the backend returns a message
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Failed to reset password')
    }
  }

  const checkAuth = async () => {
    if (!token.value) return
    
    loading.value = true
    
    try {
      const userDetails = await apiGetMe()
      user.value = userDetails
    } catch (err) {
      // Assuming a 401 or other error means the token is invalid or session expired
      logout()
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    hasRole,
    login,
    register,
    logout,
    checkAuth,
    requestPasswordReset, // Added
    resetPassword // Added
  }
})