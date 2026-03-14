<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">{{ isNewSession ? 'Créer une session live' : session?.title }}</h1>
            <p class="text-muted mb-0">{{ isNewSession ? 'Programmez une nouvelle session en direct' : 'Gérez votre session en direct' }}</p>
          </div>
          <div v-if="!isNewSession && session?.status === 'live'">
            <button class="btn btn-danger" @click="endSession">
              <i class="bi bi-stop-circle me-2"></i>Terminer la session
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Form (New Session) -->
    <div v-if="isNewSession" class="row">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <form @submit.prevent="createSession">
              <div class="mb-3">
                <label class="form-label">Titre de la session</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="sessionForm.title"
                  required
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  v-model="sessionForm.description"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="sessionForm.date"
                    required
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Heure</label>
                  <input 
                    type="time" 
                    class="form-control" 
                    v-model="sessionForm.time"
                    required
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Durée (minutes)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="sessionForm.duration"
                    min="15"
                    required
                  >
                </div>
              </div>

              <div class="mt-4">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Programmer la session
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="mb-3">Conseils pour une session réussie</h5>
            <ul class="list-unstyled">
              <li class="mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                Testez votre audio et vidéo avant la session
              </li>
              <li class="mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                Préparez votre contenu à l'avance
              </li>
              <li class="mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                Assurez-vous d'avoir une bonne connexion internet
              </li>
              <li class="mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                Choisissez un environnement calme
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Session Interface -->
    <div v-else class="row g-4">
      <!-- Video Grid -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-0">
            <div class="video-grid">
              <!-- Host Video -->
              <div class="video-container host-video">
                <div ref="localVideo" class="video-element"></div>
                <div class="video-overlay">
                  <span class="badge bg-primary">Vous (Host)</span>
                  <div class="controls">
                    <button 
                      class="btn btn-light btn-sm"
                      @click="toggleAudio"
                    >
                      <i :class="['bi', isAudioEnabled ? 'bi-mic' : 'bi-mic-mute']"></i>
                    </button>
                    <button 
                      class="btn btn-light btn-sm"
                      @click="toggleVideo"
                    >
                      <i :class="['bi', isVideoEnabled ? 'bi-camera-video' : 'bi-camera-video-off']"></i>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Participant Videos -->
              <div 
                v-for="[uid, user] in Array.from(remoteUsers)"
                :key="uid"
                class="video-container"
              >
                <div :ref="(el: any) => { if (el) (instance?.proxy as any)['remote-' + uid] = el }" class="video-element"></div>
                <div class="video-overlay">
                  <span class="badge bg-secondary">{{ (user as any).name }}</span>
                  <div class="controls">
                    <button 
                      class="btn btn-light btn-sm"
                      @click="toggleParticipantAudio(uid)"
                    >
                      <i :class="['bi', (user as any).isAudioEnabled ? 'bi-mic' : 'bi-mic-mute']"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat and Participants -->
      <div class="col-lg-4">
        <!-- Tabs -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white">
            <ul class="nav nav-tabs card-header-tabs">
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'chat' }"
                  @click="activeTab = 'chat'"
                  href="#"
                >
                  Chat
                </a>
              </li>
              <li class="nav-item">
                <a 
                  class="nav-link" 
                  :class="{ active: activeTab === 'participants' }"
                  @click="activeTab = 'participants'"
                  href="#"
                >
                  Participants
                  <span class="badge bg-primary ms-2">{{ remoteUsers.size }}</span>
                </a>
              </li>
            </ul>
          </div>
          
          <div class="card-body p-0">
            <!-- Chat -->
            <div v-if="activeTab === 'chat'" class="chat-container">
              <div class="chat-messages" ref="chatMessages">
                <div 
                  v-for="message in messages" 
                  :key="message.timestamp"
                  class="message"
                  :class="{ 'message-own': message.userId === currentUser?.id }"
                >
                  <div class="message-header">
                    <strong>{{ message.userName }}</strong>
                    <small class="text-muted">{{ formatTime(message.timestamp) }}</small>
                  </div>
                  <div class="message-content">
                    {{ message.message }}
                  </div>
                </div>
              </div>
              
              <div class="chat-input">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="newMessage"
                    @keyup.enter="sendMessage"
                    placeholder="Écrivez votre message..."
                  >
                  <button 
                    class="btn btn-primary"
                    @click="sendMessage"
                  >
                    <i class="bi bi-send"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Participants -->
            <div v-else class="participants-list">
              <div 
                v-for="[uid, user] in Array.from(remoteUsers)"
                :key="uid"
                class="participant-item"
              >
                <div class="d-flex align-items-center">
                  <div class="participant-avatar">
                    {{ (user as any).name.charAt(0) }}
                  </div>
                  <div class="participant-info">
                    <div class="participant-name">
                      {{ (user as any).name }}
                      <span 
                        v-if="raisedHands.has(uid)"
                        class="badge bg-warning text-dark ms-2"
                      >
                        <i class="bi bi-hand-index-thumb"></i>
                      </span>
                    </div>
                    <small class="text-muted">Étudiant</small>
                  </div>
                  <div class="participant-controls ms-auto">
                    <button 
                      class="btn btn-sm"
                      :class="(user as any).isAudioEnabled ? 'btn-outline-danger' : 'btn-outline-success'"
                      @click="toggleParticipantAudio(uid)"
                    >
                      <i :class="['bi', (user as any).isAudioEnabled ? 'bi-mic-mute' : 'bi-mic']"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Session Info -->
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="mb-3">Informations de la session</h5>
            <div class="mb-2">
              <strong>Durée:</strong> {{ formatDuration(sessionDuration) }}
            </div>
            <div class="mb-2">
              <strong>Participants:</strong> {{ remoteUsers.size }} / 50
            </div>
            <div class="mb-2">
              <strong>Mains levées:</strong> {{ raisedHands.size }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, getCurrentInstance } from 'vue'
import { useRoute } from 'vue-router'
import { useVideoConferenceStore } from '../../../stores/videoConference'
import { useAuthStore } from '../../../stores/auth'

const route = useRoute()
const videoStore = useVideoConferenceStore()
const authStore = useAuthStore()

const isNewSession = computed(() => !route.params.id)
const currentUser = computed(() => authStore.user)

// State
const sessionForm = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  duration: 60
})

const activeTab = ref('chat')
const newMessage = ref('')
const chatMessages = ref<HTMLElement | null>(null)
const localVideo = ref<HTMLElement | null>(null)
const isAudioEnabled = ref(true)
const isVideoEnabled = ref(true)
const sessionDuration = ref(0)
const sessionInterval = ref<number | null>(null)

// Computed
const session = computed(() => videoStore.currentSession)
const remoteUsers = computed(() => videoStore.remoteUsers)
const messages = computed(() => videoStore.messages)
const raisedHands = computed(() => videoStore.raisedHands)
const loading = computed(() => videoStore.loading)

const instance = getCurrentInstance();

// Methods
const createSession = async () => {
  try {
    const scheduledFor = `${sessionForm.value.date}T${sessionForm.value.time}`
    await videoStore.createLiveSession({
      title: sessionForm.value.title,
      description: sessionForm.value.description,
      scheduledFor,
      duration: sessionForm.value.duration,
      hostId: currentUser.value?.id
    })
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

const initializeSession = async () => {
  if (!isNewSession.value) {
    await videoStore.joinSession(
      parseInt(route.params.id as string),
      currentUser.value?.id as number,
      true
    )
    
    // Start session timer
    sessionInterval.value = setInterval(() => {
      sessionDuration.value++
    }, 1000)
  }
}

const endSession = async () => {
  if (confirm('Êtes-vous sûr de vouloir terminer la session ?')) {
    await videoStore.leaveSession()
    if (sessionInterval.value) {
      clearInterval(sessionInterval.value)
    }
  }
}

const toggleAudio = () => {
  isAudioEnabled.value = !isAudioEnabled.value
  const track = (videoStore as any).localAudioTrack;
  if (track) {
    isAudioEnabled.value ? 
      track.setEnabled(true) :
      track.setEnabled(false)
  }
}

const toggleVideo = () => {
  isVideoEnabled.value = !isVideoEnabled.value
  const track = (videoStore as any).localVideoTrack;
  if (track) {
    isVideoEnabled.value ? 
      track.setEnabled(true) :
      track.setEnabled(false)
  }
}

const toggleParticipantAudio = async (userId: string) => {
  const user = remoteUsers.value.get(userId)
  if (user) {
    await videoStore.toggleParticipantAudio(userId, user.isAudioEnabled)
  }
}

const sendMessage = async () => {
  if (newMessage.value.trim()) {
    await videoStore.sendMessage(
      newMessage.value,
      currentUser.value?.id as number,
      currentUser.value?.name as string
    )
    newMessage.value = ''
    
    // Scroll to bottom
    setTimeout(() => {
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    }, 100)
  }
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// Lifecycle
onMounted(async () => {
  await videoStore.initializeClients(import.meta.env.VITE_AGORA_APP_ID)
  await initializeSession()
})

onUnmounted(async () => {
  if (!isNewSession.value) {
    await videoStore.leaveSession()
  }
  if (sessionInterval.value) {
    clearInterval(sessionInterval.value)
  }
})
</script>

<style scoped lang="scss">
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.video-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; // 16:9 aspect ratio

  &.host-video {
    grid-column: 1 / -1;
  }
}

.video-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 0.5rem;
}

.video-overlay {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0.25rem;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 400px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.message {
  margin-bottom: 1rem;
  
  &-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }
  
  &-content {
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 0.25rem;
  }
  
  &-own {
    .message-content {
      background: #e3f2fd;
    }
  }
}

.participants-list {
  height: 400px;
  overflow-y: auto;
}

.participant-item {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  
  &:last-child {
    border-bottom: none;
  }
}

.participant-avatar {
  width: 40px;
  height: 40px;
  background: #e9ecef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-weight: bold;
}

.nav-link {
  cursor: pointer;
}
</style>