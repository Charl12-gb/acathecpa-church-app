import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  login as apiLogin,
  register as apiRegister,
  getMe as apiGetMe,
  requestPasswordReset as apiRequestPasswordReset,
  resetPassword as apiResetPassword
} from '../services/api/auth'
import type { User as ApiUser, UserRole } from '../types/api/userTypes'
import router from '../router'

export type User = Omit<ApiUser, 'role'> & {
  role: ApiUser['role'] | { name: ApiUser['role'] }
}

export const useAuthStore = defineStore('auth', () => {
  type RoleName = UserRole

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

  const getRoleName = (role: User['role']): RoleName => {
    return typeof role === 'string' ? role : role.name
  }
  
  const hasRole = (role: RoleName | RoleName[]) => {
    if (!user.value) return false
    const userRoleName = getRoleName(user.value.role)
    
    if (Array.isArray(role)) {
      return role.includes(userRoleName)
    }
    
    return userRoleName === role
  }

  // Actions
  const login = async (identifier: string, password: string) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await apiLogin({ username: identifier, password })
      
      token.value = response.access_token as string
      localStorage.setItem('token', response.access_token)
      if (response.refresh_token) {
        localStorage.setItem('refreshToken', response.refresh_token)
      }
      
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
      await apiRegister(userData as any)
      
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
    loading.value = true
    error.value = ''
    try {
      const response = await apiRequestPasswordReset(email)
      return { success: true, message: response.message }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to request password reset'
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  const resetPassword = async (token: string, newPassword: string) => {
    loading.value = true
    error.value = ''
    try {
      const response = await apiResetPassword(token, newPassword)
      return { success: true, message: response.message }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to reset password'
      return { success: false }
    } finally {
      loading.value = false
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
