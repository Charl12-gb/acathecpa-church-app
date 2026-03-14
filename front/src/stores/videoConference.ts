import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../services/api'
import AgoraRTC from 'agora-rtc-sdk-ng'
import AgoraRTM from 'agora-rtm-sdk'

export interface LiveSession {
  id: number
  courseId: number
  title: string
  description: string
  scheduledFor: string
  duration: number
  hostId: number
  status: 'scheduled' | 'live' | 'ended'
  participants: number[]
}

export interface ChatMessage {
  userId: number
  userName: string
  message: string
  timestamp: string
}

export const useVideoConferenceStore = defineStore('videoConference', () => {
  const loading = ref(false)
  const error = ref('')
  const currentSession = ref<LiveSession | null>(null)
  const rtcClient = ref<any>(null)
  const rtmClient = ref<any>(null)
  const localAudioTrack = ref<any>(null)
  const localVideoTrack = ref<any>(null)
  const remoteUsers = ref<Map<string, any>>(new Map())
  const messages = ref<ChatMessage[]>([])
  const raisedHands = ref<Set<string>>(new Set())

  // Initialize Agora clients
  const initializeClients = async (appId: string) => {
    rtcClient.value = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })
    rtmClient.value = AgoraRTM.createInstance(appId)
  }

  // Create a live session
  const createLiveSession = async (sessionData: Partial<LiveSession>) => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await apiClient.post('/live-sessions', sessionData)
      currentSession.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to create live session'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Join a live session
  const joinSession = async (sessionId: number, userId: number, isHost: boolean) => {
    try {
      // Get session token from backend
      const response = await apiClient.post(`/live-sessions/${sessionId}/join`, {
        userId,
        isHost
      })
      
      const { token, channel: channelName } = response.data
      
      // Join RTC channel
      await rtcClient.value.join(token, channelName, null, userId)
      
      // Create and publish tracks if host
      if (isHost) {
        localAudioTrack.value = await AgoraRTC.createMicrophoneAudioTrack()
        localVideoTrack.value = await AgoraRTC.createCameraVideoTrack()
        await rtcClient.value.publish([localAudioTrack.value, localVideoTrack.value])
      }
      
      // Setup event listeners
      rtcClient.value.on('user-published', handleUserPublished)
      rtcClient.value.on('user-unpublished', handleUserUnpublished)
      
      // Join RTM channel for chat
      await rtmClient.value.login({ uid: userId.toString() })
      const rtmChannel = await rtmClient.value.createChannel(sessionId.toString())
      await rtmChannel.join()
      
      rtmChannel.on('ChannelMessage', handleChannelMessage)
    } catch (err: any) {
      error.value = err.message || 'Failed to join session'
      throw error.value
    }
  }

  // Leave session
  const leaveSession = async () => {
    try {
      // Stop and close local tracks
      if (localAudioTrack.value) {
        localAudioTrack.value.stop()
        localAudioTrack.value.close()
      }
      if (localVideoTrack.value) {
        localVideoTrack.value.stop()
        localVideoTrack.value.close()
      }
      
      // Leave RTC channel
      await rtcClient.value.leave()
      
      // Leave RTM channel
      await rtmClient.value.logout()
      
      // Clear state
      localAudioTrack.value = null
      localVideoTrack.value = null
      remoteUsers.value.clear()
      messages.value = []
      raisedHands.value.clear()
    } catch (err: any) {
      error.value = err.message || 'Failed to leave session'
      throw error.value
    }
  }

  // Toggle participant audio
  const toggleParticipantAudio = async (userId: string, muted: boolean) => {
    try {
      await apiClient.post(`/live-sessions/${currentSession.value?.id}/participants/${userId}/audio`, {
        muted
      })
      
      const user = remoteUsers.value.get(userId)
      if (user?.audioTrack) {
        muted ? user.audioTrack.stop() : user.audioTrack.play()
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to toggle participant audio'
      throw error.value
    }
  }

  // Raise/lower hand
  const toggleRaiseHand = async (userId: string) => {
    try {
      const isRaised = raisedHands.value.has(userId)
      
      await apiClient.post(`/live-sessions/${currentSession.value?.id}/participants/${userId}/hand`, {
        raised: !isRaised
      })
      
      if (isRaised) {
        raisedHands.value.delete(userId)
      } else {
        raisedHands.value.add(userId)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to toggle hand raise'
      throw error.value
    }
  }

  // Send chat message
  const sendMessage = async (message: string, userId: number, userName: string) => {
    try {
      const sessionId = currentSession.value?.id.toString()
      const rtmChannel = rtmClient.value.channels.get(sessionId)
      await rtmChannel.sendMessage({ text: message })
      
      messages.value.push({
        userId,
        userName,
        message,
        timestamp: new Date().toISOString()
      })
    } catch (err: any) {
      error.value = err.message || 'Failed to send message'
      throw error.value
    }
  }

  // Event handlers
  const handleUserPublished = async (user: any, mediaType: string) => {
    await rtcClient.value.subscribe(user, mediaType)
    remoteUsers.value.set(user.uid, user)
  }

  const handleUserUnpublished = (user: any) => {
    remoteUsers.value.delete(user.uid)
  }

  const handleChannelMessage = (message: any, memberId: string) => {
    messages.value.push({
      userId: parseInt(memberId),
      userName: memberId, // You might want to maintain a mapping of user IDs to names
      message: message.text,
      timestamp: new Date().toISOString()
    })
  }

  return {
    loading,
    error,
    currentSession,
    remoteUsers,
    messages,
    raisedHands,
    initializeClients,
    createLiveSession,
    joinSession,
    leaveSession,
    toggleParticipantAudio,
    toggleRaiseHand,
    sendMessage
  }
})