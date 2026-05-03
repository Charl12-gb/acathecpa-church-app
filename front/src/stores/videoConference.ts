import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
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

interface LocalTrackLike {
  play: (container: HTMLElement) => void
  setEnabled: (enabled: boolean) => void
  stop: () => void
  close: () => void
}

class BrowserMediaTrack implements LocalTrackLike {
  private mediaTrack: MediaStreamTrack
  private kind: 'audio' | 'video'

  constructor(track: MediaStreamTrack, kind: 'audio' | 'video') {
    this.mediaTrack = track
    this.kind = kind
  }

  play(container: HTMLElement) {
    const stream = new MediaStream([this.mediaTrack])
    const element = document.createElement(this.kind === 'video' ? 'video' : 'audio') as HTMLVideoElement | HTMLAudioElement
    element.autoplay = true
    if (this.kind === 'video') {
      ;(element as HTMLVideoElement).playsInline = true
      ;(element as HTMLVideoElement).muted = true
    }
    element.srcObject = stream
    container.innerHTML = ''
    container.appendChild(element)
  }

  setEnabled(enabled: boolean) {
    this.mediaTrack.enabled = enabled
  }

  stop() {
    this.mediaTrack.stop()
  }

  close() {
    this.stop()
  }
}

export const useVideoConferenceStore = defineStore('videoConference', () => {
  const localAudioTrack = ref<LocalTrackLike | null>(null)
  const localVideoTrack = ref<LocalTrackLike | null>(null)
  const screenVideoTrack = ref<LocalTrackLike | null>(null)
  const activeMeetingUrl = ref('')
  const activeSessionId = ref<number | null>(null)

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
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
      const audio = stream.getAudioTracks()[0]
      const video = stream.getVideoTracks()[0]

      if (!localAudioTrack.value) {
        localAudioTrack.value = new BrowserMediaTrack(audio, 'audio')
      }
      if (!localVideoTrack.value) {
        localVideoTrack.value = new BrowserMediaTrack(video, 'video')
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

  // Join a meeting via backend /join and expose the Jitsi URL for in-page embedding.
  async function joinMeeting(sessionId: number, userName: string) {
    error.value = ''

    try {
      const { data: joinConfig } = await apiClient.post(`/live-sessions/${sessionId}/join`)

      const joinUrl = new URL(joinConfig.url)
      if (joinConfig.jwt) {
        joinUrl.searchParams.set('jwt', joinConfig.jwt)
      }
      joinUrl.hash = [
        'config.prejoinPageEnabled=false',
        'config.startWithAudioMuted=false',
        'config.startWithVideoMuted=false',
        `userInfo.displayName="${encodeURIComponent(userName)}"`
      ].join('&')

      isJoined.value = true
      isAudioOn.value = true
      isVideoOn.value = true
      activeMeetingUrl.value = joinUrl.toString()
      activeSessionId.value = sessionId

    } catch (e: any) {
      error.value = e?.response?.data?.detail || e?.message || 'Erreur de connexion'
      throw e
    }
  }

  // Leave meeting
  async function leaveMeeting() {
    // Notify backend of leave
    if (activeSessionId.value) {
      try {
        await apiClient.post(`/live-sessions/${activeSessionId.value}/leave`)
      } catch { /* best-effort */ }
    }

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
    } catch { /* cleanup errors are expected */ }

    participants.value.clear()
    messages.value = []
    isJoined.value = false
    isAudioOn.value = true
    isVideoOn.value = true
    isScreenSharing.value = false
    activeMeetingUrl.value = ''
    activeSessionId.value = null
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
    if (!navigator.mediaDevices || !('getDisplayMedia' in navigator.mediaDevices)) return
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
      const screenTrack = stream.getVideoTracks()[0]
      screenVideoTrack.value = new BrowserMediaTrack(screenTrack, 'video')
      isScreenSharing.value = true
      screenTrack.onended = () => { stopScreenShare() }
    } catch (e) {
      console.error('Screen share failed:', e)
    }
  }

  async function stopScreenShare() {
    if (!screenVideoTrack.value) return
    try {
      screenVideoTrack.value.stop()
      screenVideoTrack.value.close()
      screenVideoTrack.value = null
      isScreenSharing.value = false
    } catch { /* ignore */ }
  }

  async function sendChatMessage(message: string, userId: number, userName: string) {
    // Local only (Jitsi chat is handled inside Jitsi UI).
    messages.value.push({ userId, userName, message, timestamp: new Date().toISOString() })
  }

  return {
    isJoined,
    isAudioOn,
    isVideoOn,
    isScreenSharing,
    activeMeetingUrl,
    activeSessionId,
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