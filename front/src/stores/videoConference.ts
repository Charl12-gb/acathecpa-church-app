import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import AgoraRTC, {
  type IAgoraRTCClient,
  type IMicrophoneAudioTrack,
  type ICameraVideoTrack,
  type ILocalVideoTrack,
  type IAgoraRTCRemoteUser,
} from 'agora-rtc-sdk-ng'
import AgoraRTM from 'agora-rtm-sdk'
import apiClient from '../services/api'

export interface Participant {
  uid: number
  name: string
  hasAudio: boolean
  hasVideo: boolean
  isHost: boolean
  videoTrack?: any
  audioTrack?: any
}

export interface ChatMessage {
  userId: number
  userName: string
  message: string
  timestamp: string
}

export const useVideoConferenceStore = defineStore('videoConference', () => {
  // RTC
  const rtcClient = ref<IAgoraRTCClient | null>(null)
  const localAudioTrack = ref<IMicrophoneAudioTrack | null>(null)
  const localVideoTrack = ref<ICameraVideoTrack | null>(null)
  const screenVideoTrack = ref<ILocalVideoTrack | null>(null)

  // RTM
  const rtmClient = ref<any>(null)
  const rtmChannel = ref<any>(null)

  // State
  const isJoined = ref(false)
  const isAudioOn = ref(true)
  const isVideoOn = ref(true)
  const isScreenSharing = ref(false)
  const participants = ref(new Map<number, Participant>())
  const messages = ref<ChatMessage[]>([])
  const error = ref('')

  const participantList = computed(() => Array.from(participants.value.values()))
  const participantCount = computed(() => participants.value.size + 1)

  // Create local tracks for preview (before joining)
  async function createLocalTracks() {
    try {
      if (!localAudioTrack.value) {
        localAudioTrack.value = await AgoraRTC.createMicrophoneAudioTrack()
      }
      if (!localVideoTrack.value) {
        localVideoTrack.value = await AgoraRTC.createCameraVideoTrack()
      }
    } catch (e: any) {
      console.error('Failed to create local tracks:', e)
      error.value = "Impossible d'accéder à la caméra/microphone"
    }
  }

  function disposeLocalTracks() {
    if (localAudioTrack.value) {
      localAudioTrack.value.stop()
      localAudioTrack.value.close()
      localAudioTrack.value = null
    }
    if (localVideoTrack.value) {
      localVideoTrack.value.stop()
      localVideoTrack.value.close()
      localVideoTrack.value = null
    }
  }

  // Join a meeting via the backend /join endpoint
  async function joinMeeting(sessionId: number, userId: number, userName: string) {
    error.value = ''

    try {
      // 1. Get join config from backend
      const { data: joinConfig } = await apiClient.post(`/live-sessions/${sessionId}/join`)
      const { app_id, channel, token, uid } = joinConfig

      // 2. Create RTC client
      rtcClient.value = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

      // 3. Setup event handlers BEFORE joining
      rtcClient.value.on('user-joined', (user: IAgoraRTCRemoteUser) => {
        if (!participants.value.has(user.uid as number)) {
          participants.value.set(user.uid as number, {
            uid: user.uid as number,
            name: `Participant ${user.uid}`,
            hasAudio: false,
            hasVideo: false,
            isHost: false,
          })
        }
      })

      rtcClient.value.on('user-published', async (user: IAgoraRTCRemoteUser, mediaType: string) => {
        await rtcClient.value!.subscribe(user, mediaType)
        const existing = participants.value.get(user.uid as number)
        const p = existing || {
          uid: user.uid as number,
          name: `Participant ${user.uid}`,
          hasAudio: false,
          hasVideo: false,
          isHost: false,
        }
        if (mediaType === 'audio') {
          p.hasAudio = true
          p.audioTrack = user.audioTrack
          user.audioTrack?.play()
        }
        if (mediaType === 'video') {
          p.hasVideo = true
          p.videoTrack = user.videoTrack
        }
        participants.value.set(user.uid as number, { ...p })
      })

      rtcClient.value.on('user-unpublished', (user: IAgoraRTCRemoteUser, mediaType: string) => {
        const p = participants.value.get(user.uid as number)
        if (p) {
          if (mediaType === 'audio') { p.hasAudio = false; p.audioTrack = undefined }
          if (mediaType === 'video') { p.hasVideo = false; p.videoTrack = undefined }
          participants.value.set(user.uid as number, { ...p })
        }
      })

      rtcClient.value.on('user-left', (user: IAgoraRTCRemoteUser) => {
        participants.value.delete(user.uid as number)
      })

      // 4. Join RTC channel
      await rtcClient.value.join(app_id, channel, token || null, uid || userId)

      // 5. Create and publish local tracks
      if (!localAudioTrack.value) {
        localAudioTrack.value = await AgoraRTC.createMicrophoneAudioTrack()
      }
      if (!localVideoTrack.value) {
        localVideoTrack.value = await AgoraRTC.createCameraVideoTrack()
      }
      await rtcClient.value.publish([localAudioTrack.value, localVideoTrack.value])

      // 6. Setup RTM for chat and participant names
      try {
        rtmClient.value = AgoraRTM.createInstance(app_id)
        await rtmClient.value.login({ uid: userId.toString() })
        rtmChannel.value = rtmClient.value.createChannel(channel)
        await rtmChannel.value.join()

        rtmChannel.value.sendMessage({
          text: JSON.stringify({ type: 'user-info', userId, userName })
        })

        rtmChannel.value.on('ChannelMessage', (msg: any, senderId: string) => {
          try {
            const data = JSON.parse(msg.text)
            if (data.type === 'chat') {
              messages.value.push({
                userId: data.userId,
                userName: data.userName,
                message: data.message,
                timestamp: new Date().toISOString()
              })
            } else if (data.type === 'user-info') {
              const p = participants.value.get(data.userId)
              if (p) {
                p.name = data.userName
                participants.value.set(data.userId, { ...p })
              }
            }
          } catch { /* ignore malformed messages */ }
        })
      } catch (e) {
        console.warn('RTM setup failed, chat disabled:', e)
      }

      isJoined.value = true
      isAudioOn.value = true
      isVideoOn.value = true

    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Erreur de connexion'
      throw e
    }
  }

  // Leave meeting
  async function leaveMeeting() {
    try {
      if (screenVideoTrack.value) {
        screenVideoTrack.value.stop()
        screenVideoTrack.value.close()
        screenVideoTrack.value = null
      }
      if (localAudioTrack.value) {
        localAudioTrack.value.stop()
        localAudioTrack.value.close()
        localAudioTrack.value = null
      }
      if (localVideoTrack.value) {
        localVideoTrack.value.stop()
        localVideoTrack.value.close()
        localVideoTrack.value = null
      }
      if (rtcClient.value) {
        await rtcClient.value.leave()
        rtcClient.value = null
      }
      if (rtmChannel.value) {
        await rtmChannel.value.leave()
        rtmChannel.value = null
      }
      if (rtmClient.value) {
        await rtmClient.value.logout()
        rtmClient.value = null
      }
    } catch { /* cleanup errors are expected */ }

    participants.value.clear()
    messages.value = []
    isJoined.value = false
    isAudioOn.value = true
    isVideoOn.value = true
    isScreenSharing.value = false
    error.value = ''
  }

  function toggleAudio() {
    if (localAudioTrack.value) {
      const newState = !isAudioOn.value
      localAudioTrack.value.setEnabled(newState)
      isAudioOn.value = newState
    }
  }

  function toggleVideo() {
    if (localVideoTrack.value) {
      const newState = !isVideoOn.value
      localVideoTrack.value.setEnabled(newState)
      isVideoOn.value = newState
    }
  }

  async function startScreenShare() {
    if (!rtcClient.value) return
    try {
      screenVideoTrack.value = await AgoraRTC.createScreenVideoTrack({}) as ILocalVideoTrack
      if (localVideoTrack.value) await rtcClient.value.unpublish(localVideoTrack.value)
      await rtcClient.value.publish(screenVideoTrack.value)
      isScreenSharing.value = true
      screenVideoTrack.value.on('track-ended', () => { stopScreenShare() })
    } catch (e) {
      console.error('Screen share failed:', e)
    }
  }

  async function stopScreenShare() {
    if (!rtcClient.value || !screenVideoTrack.value) return
    try {
      await rtcClient.value.unpublish(screenVideoTrack.value)
      screenVideoTrack.value.stop()
      screenVideoTrack.value.close()
      screenVideoTrack.value = null
      if (localVideoTrack.value) await rtcClient.value.publish(localVideoTrack.value)
      isScreenSharing.value = false
    } catch { /* ignore */ }
  }

  async function sendChatMessage(message: string, userId: number, userName: string) {
    if (rtmChannel.value) {
      try {
        await rtmChannel.value.sendMessage({
          text: JSON.stringify({ type: 'chat', userId, userName, message })
        })
      } catch { /* ignore */ }
    }
    messages.value.push({ userId, userName, message, timestamp: new Date().toISOString() })
  }

  return {
    isJoined,
    isAudioOn,
    isVideoOn,
    isScreenSharing,
    localAudioTrack,
    localVideoTrack,
    screenVideoTrack,
    participants,
    participantList,
    participantCount,
    messages,
    error,
    createLocalTracks,
    disposeLocalTracks,
    joinMeeting,
    leaveMeeting,
    toggleAudio,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
    sendChatMessage,
  }
})