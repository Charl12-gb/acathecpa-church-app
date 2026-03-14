import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { API_URL } from '../config'

export interface Content {
  id: number
  title: string
  description: string
  content: string
  type: 'article' | 'podcast'
  format?: 'audio' | 'video' | 'text' | 'pdf'
  mediaUrl?: string
  isPremium: boolean
  price?: number
  author: {
    id: number
    name: string
  }
  status: 'draft' | 'published'
  tags: string[]
  created_at: string
  updated_at: string
}

export const useContentStore = defineStore('content', () => {
  const loading = ref(false)
  const error = ref('')
  const currentContent = ref<Content | null>(null)
  const userContents = ref<Content[]>([])

  // Get content list
  const getContents = async (type?: 'article' | 'podcast') => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.get(`${API_URL}/contents${type ? `?type=${type}` : ''}`)
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load contents'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Get single content
  const getContent = async (contentId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.get(`${API_URL}/contents/${contentId}`)
      currentContent.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load content'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Create/Update content
  const saveContent = async (content: Partial<Content>) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.post(`${API_URL}/contents`, content)
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to save content'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Delete content
  const deleteContent = async (contentId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      await axios.delete(`${API_URL}/contents/${contentId}`)
    } catch (err: any) {
      error.value = err.message || 'Failed to delete content'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Get user's contents
  const getUserContents = async () => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.get(`${API_URL}/user/contents`)
      userContents.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load user contents'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Publish content
  const publishContent = async (contentId: number) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await axios.post(`${API_URL}/contents/${contentId}/publish`)
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to publish content'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    currentContent,
    userContents,
    getContents,
    getContent,
    saveContent,
    deleteContent,
    getUserContents,
    publishContent
  }
})