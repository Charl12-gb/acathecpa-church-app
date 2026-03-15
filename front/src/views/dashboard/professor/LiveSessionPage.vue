<template>
  <!-- ======================== MEETING MODE ======================== -->
  <div v-if="inMeeting" class="meeting-container">
    <!-- Top bar -->
    <div class="meeting-topbar">
      <div class="meeting-info">
        <span class="meeting-title">{{ session?.title }}</span>
        <span class="meeting-separator">|</span>
        <span class="meeting-timer">{{ formatDuration(sessionDuration) }}</span>
      </div>
      <div class="meeting-topbar-right">
        <span class="participant-badge">
          <i class="bi bi-people-fill"></i> {{ videoStore.participantCount }}
        </span>
      </div>
    </div>

    <!-- Main area -->
    <div class="meeting-body">
      <div class="meeting-stage" :class="{ 'has-panel': showPanel }">
        <div class="video-grid" :class="gridLayoutClass">
          <!-- Local video tile -->
          <div class="video-tile" :class="{ 'screen-sharing': videoStore.isScreenSharing }">
            <div ref="localVideoEl" class="video-frame"></div>
            <div v-if="!videoStore.isVideoOn && !videoStore.isScreenSharing" class="video-off-overlay">
              <div class="avatar-circle avatar-lg">
                {{ currentUser?.name?.charAt(0)?.toUpperCase() || 'V' }}
              </div>
            </div>
            <div class="tile-bottom">
              <span class="tile-name">Vous</span>
              <i v-if="!videoStore.isAudioOn" class="bi bi-mic-mute-fill tile-mic-icon"></i>
            </div>
          </div>

          <!-- Remote participant tiles -->
          <div
            v-for="p in videoStore.participantList"
            :key="p.uid"
            class="video-tile"
          >
            <div :ref="el => setRemoteVideoRef(p.uid, el)" class="video-frame"></div>
            <div v-if="!p.hasVideo" class="video-off-overlay">
              <div class="avatar-circle avatar-lg">
                {{ p.name?.charAt(0)?.toUpperCase() || '?' }}
              </div>
            </div>
            <div class="tile-bottom">
              <span class="tile-name">{{ p.name }}</span>
              <i v-if="!p.hasAudio" class="bi bi-mic-mute-fill tile-mic-icon"></i>
            </div>
          </div>

          <!-- Waiting for participants -->
          <div v-if="videoStore.participantList.length === 0" class="video-tile waiting-tile">
            <div class="waiting-content">
              <i class="bi bi-people fs-1 mb-2 d-block"></i>
              <p class="mb-1">En attente de participants...</p>
              <small class="text-muted">Partagez le lien de la session</small>
              <button class="btn btn-sm btn-outline-light mt-3" @click="copySessionLink">
                <i class="bi bi-link-45deg me-1"></i>Copier le lien
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Side panel (participants / chat) -->
      <transition name="panel-slide">
        <div v-if="showPanel" class="meeting-panel">
          <div class="panel-header">
            <div class="panel-tabs">
              <button
                :class="{ active: activePanel === 'participants' }"
                @click="activePanel = 'participants'"
              >
                <i class="bi bi-people me-1"></i>Participants ({{ videoStore.participantCount }})
              </button>
              <button
                :class="{ active: activePanel === 'chat' }"
                @click="activePanel = 'chat'"
              >
                <i class="bi bi-chat-dots me-1"></i>Chat
              </button>
            </div>
            <button class="panel-close-btn" @click="showPanel = false">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <!-- Participants list -->
          <div v-if="activePanel === 'participants'" class="panel-body">
            <div class="participant-item">
              <div class="avatar-circle avatar-sm">{{ currentUser?.name?.charAt(0)?.toUpperCase() || 'V' }}</div>
              <div class="p-name">{{ currentUser?.name || 'Vous' }} <small class="text-muted">(Organisateur)</small></div>
              <div class="p-icons">
                <i class="bi" :class="videoStore.isAudioOn ? 'bi-mic-fill' : 'bi-mic-mute-fill text-danger'"></i>
                <i class="bi" :class="videoStore.isVideoOn ? 'bi-camera-video-fill' : 'bi-camera-video-off-fill text-danger'"></i>
              </div>
            </div>
            <div v-for="p in videoStore.participantList" :key="p.uid" class="participant-item">
              <div class="avatar-circle avatar-sm">{{ p.name?.charAt(0)?.toUpperCase() || '?' }}</div>
              <div class="p-name">{{ p.name }}</div>
              <div class="p-icons">
                <i class="bi" :class="p.hasAudio ? 'bi-mic-fill' : 'bi-mic-mute-fill text-danger'"></i>
                <i class="bi" :class="p.hasVideo ? 'bi-camera-video-fill' : 'bi-camera-video-off-fill text-danger'"></i>
              </div>
            </div>
            <div v-if="videoStore.participantList.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-person-plus d-block mb-2" style="font-size: 1.5rem;"></i>
              Aucun autre participant
            </div>
          </div>

          <!-- Chat panel -->
          <div v-else class="panel-body panel-chat-body">
            <div class="chat-messages-list" ref="chatScrollRef">
              <div
                v-for="(msg, i) in videoStore.messages"
                :key="i"
                class="chat-bubble"
                :class="{ own: msg.userId === currentUser?.id }"
              >
                <div class="chat-meta">
                  <strong>{{ msg.userName }}</strong>
                  <small>{{ formatTime(msg.timestamp) }}</small>
                </div>
                <div class="chat-text">{{ msg.message }}</div>
              </div>
              <div v-if="videoStore.messages.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-chat-dots d-block mb-2" style="font-size: 1.5rem;"></i>
                Aucun message
              </div>
            </div>
            <div class="chat-input-area">
              <input
                v-model="chatInput"
                @keyup.enter="handleSendChat"
                placeholder="Envoyer un message..."
                class="chat-input-field"
              >
              <button class="chat-send-btn" @click="handleSendChat" :disabled="!chatInput.trim()">
                <i class="bi bi-send-fill"></i>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Control bar -->
    <div class="meeting-controls">
      <div class="controls-center">
        <button
          class="ctrl-btn"
          :class="{ off: !videoStore.isAudioOn }"
          @click="videoStore.toggleAudio()"
          :title="videoStore.isAudioOn ? 'Couper le micro' : 'Activer le micro'"
        >
          <i class="bi" :class="videoStore.isAudioOn ? 'bi-mic-fill' : 'bi-mic-mute-fill'"></i>
        </button>
        <button
          class="ctrl-btn"
          :class="{ off: !videoStore.isVideoOn }"
          @click="videoStore.toggleVideo()"
          :title="videoStore.isVideoOn ? 'Couper la caméra' : 'Activer la caméra'"
        >
          <i class="bi" :class="videoStore.isVideoOn ? 'bi-camera-video-fill' : 'bi-camera-video-off-fill'"></i>
        </button>
        <button
          class="ctrl-btn"
          :class="{ active: videoStore.isScreenSharing }"
          @click="videoStore.isScreenSharing ? videoStore.stopScreenShare() : videoStore.startScreenShare()"
          title="Partager l'écran"
        >
          <i class="bi bi-display"></i>
        </button>
        <button
          class="ctrl-btn"
          :class="{ active: handRaised }"
          @click="handRaised = !handRaised"
          title="Lever la main"
        >
          <i class="bi bi-hand-index-thumb-fill"></i>
        </button>
        <div class="ctrl-divider"></div>
        <button
          class="ctrl-btn"
          :class="{ active: showPanel && activePanel === 'chat' }"
          @click="togglePanel('chat')"
          title="Chat"
        >
          <i class="bi bi-chat-dots-fill"></i>
          <span v-if="unreadMessages > 0" class="ctrl-badge">{{ unreadMessages }}</span>
        </button>
        <button
          class="ctrl-btn"
          :class="{ active: showPanel && activePanel === 'participants' }"
          @click="togglePanel('participants')"
          title="Participants"
        >
          <i class="bi bi-people-fill"></i>
        </button>
        <button class="ctrl-btn" @click="copySessionLink" title="Copier le lien">
          <i class="bi bi-link-45deg"></i>
        </button>
        <div class="ctrl-divider"></div>
        <button class="ctrl-btn ctrl-leave" @click="handleLeaveMeeting" title="Quitter l'appel">
          <i class="bi bi-telephone-x-fill"></i>
        </button>
        <button
          v-if="session?.host_id === currentUser?.id"
          class="ctrl-btn ctrl-end"
          @click="handleEndMeeting"
          title="Terminer pour tous"
        >
          <i class="bi bi-stop-circle-fill"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- ======================== MANAGEMENT MODE ======================== -->
  <div v-else class="live-session-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>

    <template v-else>
      <!-- Back link -->
      <RouterLink to="/live-sessions" class="back-link mb-3 d-inline-flex align-items-center">
        <i class="bi bi-arrow-left me-2"></i>Retour aux sessions
      </RouterLink>

      <!-- Page Header -->
      <div class="page-header mb-4">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h1 class="page-title mb-1">{{ isNewSession ? 'Nouvelle session live' : (session ? session.title : 'Session') }}</h1>
            <p class="page-subtitle mb-0">{{ isNewSession ? 'Programmez une nouvelle session en direct' : 'Gérez votre session en direct' }}</p>
          </div>
          <div v-if="!isNewSession && session" class="d-flex gap-2">
            <span class="status-badge" :class="'badge-' + session.status">
              <i class="bi" :class="statusIcon(session.status)"></i>
              {{ statusLabel(session.status) }}
            </span>
          </div>
        </div>
      </div>

      <!-- ==================== CREATE / EDIT FORM ==================== -->
      <div v-if="isNewSession || isEditing" class="row g-4">
        <div class="col-lg-8">
          <div class="form-card">
            <div class="form-card-header">
              <i class="bi bi-camera-video me-2"></i>
              {{ isNewSession ? 'Détails de la session' : 'Modifier la session' }}
            </div>
            <div class="form-card-body">
              <form @submit.prevent="isNewSession ? createSession() : saveSession()">
                <div class="form-group mb-3" v-if="isNewSession">
                  <label class="form-label-custom">Type de session</label>
                  <div class="d-flex gap-2">
                    <button type="button" class="btn flex-fill" :class="sessionForm.isInstant ? 'btn-outline-custom' : 'btn-primary-custom'" @click="sessionForm.isInstant = false">
                      <i class="bi bi-calendar-event me-1"></i>Programmée
                    </button>
                    <button type="button" class="btn flex-fill" :class="sessionForm.isInstant ? 'btn-primary-custom' : 'btn-outline-custom'" @click="setInstantMeet()">
                      <i class="bi bi-lightning-fill me-1"></i>Meet instantané
                    </button>
                  </div>
                </div>
                <div class="form-group mb-3">
                  <label class="form-label-custom">Cours associé <span class="text-muted fw-normal">(optionnel)</span></label>
                  <select class="form-select-custom" v-model="sessionForm.course_id" :disabled="!isNewSession">
                    <option :value="null">Aucun cours (meet libre)</option>
                    <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
                  </select>
                </div>
                <div class="form-group mb-3">
                  <label class="form-label-custom">Titre <span class="text-danger">*</span></label>
                  <input type="text" class="form-input-custom" v-model="sessionForm.title" placeholder="Ex: Introduction au Marketing Digital" required>
                </div>
                <div class="form-group mb-3">
                  <label class="form-label-custom">Description</label>
                  <textarea class="form-input-custom" v-model="sessionForm.description" rows="3" placeholder="Décrivez le contenu de cette session..."></textarea>
                </div>
                <div class="row g-3" v-if="!sessionForm.isInstant">
                  <div class="col-md-4">
                    <label class="form-label-custom">Date <span class="text-danger">*</span></label>
                    <input type="date" class="form-input-custom" v-model="sessionForm.date" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label-custom">Heure <span class="text-danger">*</span></label>
                    <input type="time" class="form-input-custom" v-model="sessionForm.time" required>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label-custom">Durée (minutes)</label>
                    <input type="number" class="form-input-custom" v-model.number="sessionForm.duration_minutes" min="15" max="480" placeholder="60">
                  </div>
                </div>
                <div v-else class="mb-3">
                  <div class="alert alert-info-custom mb-0 d-flex align-items-center">
                    <i class="bi bi-lightning-fill me-2"></i>
                    La session démarrera immédiatement après sa création.
                  </div>
                </div>
                <div class="d-flex gap-2 mt-4">
                  <button type="submit" class="btn btn-primary-custom" :disabled="formLoading || !sessionForm.title.trim()">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ isNewSession ? (sessionForm.isInstant ? 'Démarrer le meet' : 'Programmer la session') : 'Enregistrer les modifications' }}
                  </button>
                  <button v-if="isEditing" type="button" class="btn btn-outline-custom" @click="isEditing = false">Annuler</button>
                </div>
              </form>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="tips-card">
            <div class="tips-header"><i class="bi bi-lightbulb me-2"></i>Conseils</div>
            <ul class="tips-list">
              <li><i class="bi bi-check2 text-success me-2"></i>Testez votre audio et vidéo avant la session</li>
              <li><i class="bi bi-check2 text-success me-2"></i>Préparez votre contenu à l'avance</li>
              <li><i class="bi bi-check2 text-success me-2"></i>Bonne connexion internet recommandée</li>
              <li><i class="bi bi-check2 text-success me-2"></i>Choisissez un environnement calme</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- ==================== PRE-JOIN / SESSION DETAIL ==================== -->
      <div v-else-if="session" class="row g-4">
        <!-- Pre-join screen when session is live -->
        <div v-if="session.status === 'live'" class="col-12">
          <div class="prejoin-card">
            <div class="prejoin-main">
              <div class="prejoin-video-wrapper">
                <div ref="previewVideoEl" class="prejoin-video"></div>
                <div v-if="!previewVideoOn" class="video-off-overlay">
                  <div class="avatar-circle avatar-xl">
                    {{ currentUser?.name?.charAt(0)?.toUpperCase() || 'V' }}
                  </div>
                </div>
                <div class="prejoin-controls">
                  <button class="prejoin-ctrl-btn" :class="{ off: !previewAudioOn }" @click="togglePreviewAudio">
                    <i class="bi" :class="previewAudioOn ? 'bi-mic-fill' : 'bi-mic-mute-fill'"></i>
                  </button>
                  <button class="prejoin-ctrl-btn" :class="{ off: !previewVideoOn }" @click="togglePreviewVideo">
                    <i class="bi" :class="previewVideoOn ? 'bi-camera-video-fill' : 'bi-camera-video-off-fill'"></i>
                  </button>
                </div>
              </div>
              <div class="prejoin-info">
                <h2>{{ session.title }}</h2>
                <p class="text-muted" v-if="session.description">{{ session.description }}</p>
                <div class="prejoin-meta">
                  <span><i class="bi bi-clock me-1"></i>{{ formatDate(session.scheduled_for) }}</span>
                </div>
                <div v-if="videoStore.error" class="alert alert-danger mt-3 small">
                  {{ videoStore.error }}
                </div>
                <button
                  class="btn btn-primary-custom btn-lg mt-4"
                  @click="handleJoinMeeting"
                  :disabled="joiningMeeting"
                >
                  <span v-if="joiningMeeting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-camera-video-fill me-2"></i>
                  Rejoindre maintenant
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Session detail view (scheduled / ended) -->
        <template v-else>
          <div class="col-lg-8">
            <div class="detail-card">
              <div class="detail-card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-info-circle me-2"></i>Informations de la session</span>
                <button v-if="session.status !== 'ended'" class="btn btn-sm btn-outline-custom" @click="startEditing">
                  <i class="bi bi-pencil me-1"></i>Modifier
                </button>
              </div>
              <div class="detail-card-body">
                <div class="detail-row">
                  <span class="detail-label">Titre</span>
                  <span class="detail-value">{{ session.title }}</span>
                </div>
                <div class="detail-row" v-if="session.description">
                  <span class="detail-label">Description</span>
                  <span class="detail-value">{{ session.description }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Date & Heure</span>
                  <span class="detail-value">{{ formatDate(session.scheduled_for) }}</span>
                </div>
                <div class="detail-row" v-if="session.duration_minutes">
                  <span class="detail-label">Durée</span>
                  <span class="detail-value">{{ session.duration_minutes }} minutes</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Statut</span>
                  <span class="status-badge" :class="'badge-' + session.status">
                    <i class="bi" :class="statusIcon(session.status)"></i>
                    {{ statusLabel(session.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-4">
            <div class="action-card">
              <div class="action-card-header">Actions rapides</div>
              <div class="action-card-body">
                <button class="action-btn" @click="copySessionLink">
                  <i class="bi bi-link-45deg"></i><span>Copier le lien</span>
                </button>
                <button v-if="session.status === 'scheduled'" class="action-btn action-btn-success" @click="changeStatus('live')" :disabled="actionLoading">
                  <i class="bi bi-play-fill"></i><span>Démarrer la session</span>
                </button>
                <button v-if="session.status === 'live'" class="action-btn action-btn-danger" @click="changeStatus('ended')" :disabled="actionLoading">
                  <i class="bi bi-stop-fill"></i><span>Terminer la session</span>
                </button>
                <button class="action-btn action-btn-danger" @click="deleteCurrentSession">
                  <i class="bi bi-trash3"></i><span>Supprimer la session</span>
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </template>

    <!-- Toast -->
    <div v-if="toastMessage" class="copy-toast">
      <i class="bi bi-check-circle me-2"></i>{{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../../stores/auth'
import { useVideoConferenceStore } from '../../../stores/videoConference'
import {
  createLiveSession as apiCreate,
  getLiveSessionById,
  updateLiveSession as apiUpdate,
  updateLiveSessionStatus,
  deleteLiveSession as apiDelete,
} from '../../../services/api/liveSession'
import { getInstructorCourses } from '../../../services/api/course'
import type { LiveSession } from '../../../types/api/liveSessionTypes'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const videoStore = useVideoConferenceStore()

const currentUser = computed(() => authStore.user)
const isNewSession = computed(() => !route.params.id)

// Management state
const session = ref<LiveSession | null>(null)
const courses = ref<{ id: number; title: string }[]>([])
const pageLoading = ref(true)
const formLoading = ref(false)
const actionLoading = ref(false)
const isEditing = ref(false)
const toastMessage = ref('')

const sessionForm = ref({
  course_id: null as number | null,
  title: '',
  description: '',
  date: '',
  time: '',
  duration_minutes: 60,
  isInstant: false,
})

// Meeting state
const inMeeting = ref(false)
const showPanel = ref(false)
const activePanel = ref<'participants' | 'chat'>('participants')
const chatInput = ref('')
const sessionDuration = ref(0)
const durationInterval = ref<ReturnType<typeof setInterval> | null>(null)
const handRaised = ref(false)
const unreadMessages = ref(0)
const joiningMeeting = ref(false)

// Pre-join state
const previewVideoEl = ref<HTMLElement | null>(null)
const previewAudioOn = ref(true)
const previewVideoOn = ref(true)

// Meeting refs
const localVideoEl = ref<HTMLElement | null>(null)
const remoteVideoRefs = ref<Record<number, HTMLElement | null>>({})
const chatScrollRef = ref<HTMLElement | null>(null)

// Helpers
const statusLabel = (s: string) => ({ live: 'En direct', scheduled: 'Programmée', ended: 'Terminée' }[s] || s)
const statusIcon = (s: string) => ({ live: 'bi-broadcast', scheduled: 'bi-calendar-event', ended: 'bi-check-circle' }[s] || 'bi-circle')
const formatDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
})
const formatTime = (t: string) => new Date(t).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
const formatDuration = (seconds: number) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

// Video grid layout
const totalTiles = computed(() => videoStore.participantList.length + 1)
const gridLayoutClass = computed(() => {
  const n = totalTiles.value
  if (n <= 1) return 'grid-1'
  if (n === 2) return 'grid-2'
  if (n <= 4) return 'grid-4'
  if (n <= 6) return 'grid-6'
  return 'grid-many'
})

// Remote video ref setter
function setRemoteVideoRef(uid: number, el: HTMLElement | null) {
  remoteVideoRefs.value[uid] = el
}

// Watch for local video track to play into DOM
watch(() => videoStore.localVideoTrack, (track) => {
  if (track && localVideoEl.value) {
    track.play(localVideoEl.value)
  }
}, { immediate: true })

// Watch for screen share track to play into local tile
watch(() => videoStore.screenVideoTrack, (track) => {
  if (track && localVideoEl.value) {
    track.play(localVideoEl.value)
  }
})

// Watch for remote participants video tracks
watch(() => videoStore.participantList, (list) => {
  nextTick(() => {
    list.forEach(p => {
      const el = remoteVideoRefs.value[p.uid]
      if (p.videoTrack && el) {
        p.videoTrack.play(el)
      }
    })
  })
}, { deep: true })

// Track unread messages when chat panel is closed
watch(() => videoStore.messages.length, () => {
  if (!showPanel.value || activePanel.value !== 'chat') {
    unreadMessages.value++
  }
  nextTick(() => {
    if (chatScrollRef.value) chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  })
})

// Fix: reload data when route params change (navigation without full page reload)
watch(() => route.params.id, async (newId, oldId) => {
  if (newId !== oldId) {
    inMeeting.value = false
    session.value = null
    await loadData()
  }
})

// Load data
const loadData = async () => {
  pageLoading.value = true
  try {
    try { courses.value = await getInstructorCourses() } catch { courses.value = [] }

    if (!isNewSession.value) {
      const id = parseInt(route.params.id as string)
      session.value = await getLiveSessionById(id)

      // If session is live, start camera preview
      if (session.value?.status === 'live') {
        await initPreview()
      }
    }
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Session introuvable')
    router.push('/live-sessions')
  } finally {
    pageLoading.value = false
  }
}

// Pre-join preview
const initPreview = async () => {
  try {
    await videoStore.createLocalTracks()
    nextTick(() => {
      if (videoStore.localVideoTrack && previewVideoEl.value) {
        videoStore.localVideoTrack.play(previewVideoEl.value)
      }
    })
  } catch { /* ignore preview errors */ }
}

const togglePreviewAudio = () => {
  previewAudioOn.value = !previewAudioOn.value
  if (videoStore.localAudioTrack) videoStore.localAudioTrack.setEnabled(previewAudioOn.value)
}

const togglePreviewVideo = () => {
  previewVideoOn.value = !previewVideoOn.value
  if (videoStore.localVideoTrack) videoStore.localVideoTrack.setEnabled(previewVideoOn.value)
}

// Join meeting
const handleJoinMeeting = async () => {
  if (!session.value || !currentUser.value) return
  joiningMeeting.value = true
  try {
    await videoStore.joinMeeting(session.value.id, currentUser.value.id, currentUser.value.name || 'Utilisateur')
    inMeeting.value = true
    videoStore.isAudioOn = previewAudioOn.value
    videoStore.isVideoOn = previewVideoOn.value

    // Start duration timer
    durationInterval.value = setInterval(() => { sessionDuration.value++ }, 1000)

    // Play local video in meeting view
    nextTick(() => {
      if (videoStore.localVideoTrack && localVideoEl.value) {
        videoStore.localVideoTrack.play(localVideoEl.value)
      }
    })
  } catch {
    // Error is displayed via videoStore.error
  } finally {
    joiningMeeting.value = false
  }
}

// Leave meeting
const handleLeaveMeeting = async () => {
  await videoStore.leaveMeeting()
  inMeeting.value = false
  if (durationInterval.value) { clearInterval(durationInterval.value); durationInterval.value = null }
  sessionDuration.value = 0
  showPanel.value = false
  // Reload session data
  if (session.value) session.value = await getLiveSessionById(session.value.id)
}

// End meeting for all (host only)
const handleEndMeeting = async () => {
  if (!session.value || !confirm('Terminer la session pour tous les participants ?')) return
  try {
    await updateLiveSessionStatus(session.value.id, 'ended')
    await handleLeaveMeeting()
    session.value = await getLiveSessionById(session.value!.id)
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur')
  }
}

// Panel toggle
const togglePanel = (panel: 'participants' | 'chat') => {
  if (showPanel.value && activePanel.value === panel) {
    showPanel.value = false
  } else {
    activePanel.value = panel
    showPanel.value = true
    if (panel === 'chat') unreadMessages.value = 0
  }
}

// Chat
const handleSendChat = () => {
  if (!chatInput.value.trim() || !currentUser.value) return
  videoStore.sendChatMessage(chatInput.value, currentUser.value.id, currentUser.value.name || 'Vous')
  chatInput.value = ''
}

// Session form helpers
const setInstantMeet = () => {
  sessionForm.value.isInstant = true
  if (!sessionForm.value.title.trim()) {
    sessionForm.value.title = `Meet ${new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}`
  }
}

const createSession = async () => {
  if (!sessionForm.value.title.trim()) return
  formLoading.value = true
  try {
    let scheduled_for: string
    if (sessionForm.value.isInstant) {
      scheduled_for = new Date().toISOString()
    } else {
      scheduled_for = `${sessionForm.value.date}T${sessionForm.value.time}:00`
    }
    const payload: any = {
      title: sessionForm.value.title,
      description: sessionForm.value.description || undefined,
      scheduled_for,
      duration_minutes: sessionForm.value.duration_minutes || undefined,
    }
    if (sessionForm.value.course_id) payload.course_id = sessionForm.value.course_id
    const created = await apiCreate(payload)

    if (sessionForm.value.isInstant && created.id) {
      try { await updateLiveSessionStatus(created.id, 'live') } catch { /* user can start manually */ }
    }
    router.push(`/live-session/${created.id}`)
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la création')
  } finally {
    formLoading.value = false
  }
}

const startEditing = () => {
  if (!session.value) return
  const d = new Date(session.value.scheduled_for)
  sessionForm.value = {
    course_id: session.value.course_id ?? null,
    title: session.value.title,
    description: session.value.description || '',
    date: d.toISOString().split('T')[0],
    time: d.toTimeString().slice(0, 5),
    duration_minutes: session.value.duration_minutes || 60,
    isInstant: false,
  }
  isEditing.value = true
}

const saveSession = async () => {
  if (!session.value) return
  formLoading.value = true
  try {
    const scheduled_for = `${sessionForm.value.date}T${sessionForm.value.time}:00`
    const updated = await apiUpdate(session.value.id, {
      title: sessionForm.value.title,
      description: sessionForm.value.description || undefined,
      scheduled_for,
      duration_minutes: sessionForm.value.duration_minutes || undefined,
    })
    session.value = updated
    isEditing.value = false
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la modification')
  } finally {
    formLoading.value = false
  }
}

const changeStatus = async (newStatus: string) => {
  if (!session.value) return
  if (newStatus === 'ended' && !confirm('Terminer la session ?')) return
  actionLoading.value = true
  try {
    const updated = await updateLiveSessionStatus(session.value.id, newStatus)
    session.value = updated
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur')
  } finally {
    actionLoading.value = false
  }
}

const deleteCurrentSession = async () => {
  if (!session.value || !confirm('Supprimer cette session définitivement ?')) return
  try {
    await apiDelete(session.value.id)
    router.push('/live-sessions')
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const copySessionLink = () => {
  if (!session.value) return
  const link = `${window.location.origin}/live-session/${session.value.id}`
  navigator.clipboard.writeText(link).then(() => {
    toastMessage.value = 'Lien copié !'
    setTimeout(() => { toastMessage.value = '' }, 2000)
  })
}

onMounted(loadData)

onUnmounted(async () => {
  if (inMeeting.value) await videoStore.leaveMeeting()
  else videoStore.disposeLocalTracks()
  if (durationInterval.value) clearInterval(durationInterval.value)
})
</script>

<style scoped lang="scss">
/* ============================== MEETING MODE ============================== */
.meeting-container {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: #202124; z-index: 9999;
  display: flex; flex-direction: column;
  color: #e8eaed;
}

.meeting-topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 1.2rem; background: #2d2e31; border-bottom: 1px solid #3c4043;
  min-height: 48px;
}
.meeting-info { display: flex; align-items: center; gap: 0.5rem; }
.meeting-title { font-weight: 600; font-size: 0.9rem; color: #e8eaed; }
.meeting-separator { color: #5f6368; }
.meeting-timer { font-family: monospace; font-size: 0.85rem; color: #9aa0a6; }
.participant-badge {
  background: #3c4043; padding: 0.25rem 0.6rem; border-radius: 16px;
  font-size: 0.8rem; color: #e8eaed; display: inline-flex; align-items: center; gap: 0.4rem;
}

.meeting-body { flex: 1; display: flex; overflow: hidden; }
.meeting-stage { flex: 1; display: flex; align-items: center; justify-content: center; padding: 8px; transition: all 0.3s; }
.meeting-stage.has-panel { margin-right: 0; }

/* Video grid layouts */
.video-grid {
  display: grid; gap: 8px; width: 100%; height: 100%;
  padding: 4px; align-content: center;
}
.grid-1 { grid-template-columns: 1fr; max-width: 960px; margin: 0 auto; }
.grid-2 { grid-template-columns: 1fr 1fr; max-width: 1200px; margin: 0 auto; }
.grid-4 { grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; }
.grid-6 { grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr; }
.grid-many { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }

.video-tile {
  position: relative; border-radius: 12px; overflow: hidden;
  background: #3c4043; min-height: 200px;
}
.video-frame {
  width: 100%; height: 100%; position: absolute; top: 0; left: 0;
  :deep(video) { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
}
.video-off-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; align-items: center; justify-content: center;
  background: #3c4043;
}
.tile-bottom {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 0.4rem 0.8rem; display: flex; align-items: center; gap: 0.4rem;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
}
.tile-name { font-size: 0.8rem; color: #fff; font-weight: 500; }
.tile-mic-icon { color: #ea4335; font-size: 0.75rem; }
.waiting-tile {
  display: flex; align-items: center; justify-content: center;
  background: #2d2e31; grid-column: 1 / -1;
}
.waiting-content { text-align: center; color: #9aa0a6; padding: 2rem; }

/* Avatar circles */
.avatar-circle {
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; flex-shrink: 0;
}
.avatar-lg { width: 80px; height: 80px; font-size: 2rem; background: #5f6368; }
.avatar-xl { width: 100px; height: 100px; font-size: 2.5rem; background: #5f6368; }
.avatar-sm { width: 32px; height: 32px; font-size: 0.85rem; background: #5f6368; }

/* Side panel */
.meeting-panel {
  width: 340px; background: #fff; border-left: 1px solid #e0e0e0;
  display: flex; flex-direction: column; color: #202124;
}
.panel-header {
  display: flex; align-items: center; padding: 0.6rem; border-bottom: 1px solid #e0e0e0;
}
.panel-tabs {
  display: flex; flex: 1; gap: 0;
  button {
    flex: 1; border: none; background: none; padding: 0.5rem; font-size: 0.8rem;
    font-weight: 500; color: #5f6368; cursor: pointer; border-bottom: 2px solid transparent;
    transition: all 0.2s;
    &.active { color: #1a73e8; border-bottom-color: #1a73e8; }
    &:hover { background: #f1f3f4; }
  }
}
.panel-close-btn {
  border: none; background: none; color: #5f6368; padding: 0.4rem;
  border-radius: 50%; cursor: pointer; display: flex; align-items: center;
  &:hover { background: #f1f3f4; }
}
.panel-body { flex: 1; overflow-y: auto; padding: 0.5rem; }
.panel-chat-body { display: flex; flex-direction: column; padding: 0; }

/* Participants list */
.participant-item {
  display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.8rem; border-radius: 8px;
  &:hover { background: #f1f3f4; }
}
.p-name { flex: 1; font-size: 0.85rem; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.p-icons { display: flex; gap: 0.5rem; font-size: 0.85rem; color: #5f6368; }

/* Chat */
.chat-messages-list { flex: 1; overflow-y: auto; padding: 0.8rem; }
.chat-bubble {
  margin-bottom: 0.6rem;
  .chat-meta { display: flex; justify-content: space-between; font-size: 0.7rem; margin-bottom: 0.15rem;
    strong { color: #202124; } small { color: #9aa0a6; }
  }
  .chat-text { font-size: 0.85rem; color: #3c4043; padding: 0.4rem 0.7rem; background: #f1f3f4; border-radius: 8px; }
  &.own .chat-text { background: #e8f0fe; color: #174ea6; }
}
.chat-input-area {
  display: flex; gap: 0.4rem; padding: 0.6rem 0.8rem; border-top: 1px solid #e0e0e0;
}
.chat-input-field {
  flex: 1; border: 1px solid #dadce0; border-radius: 24px; padding: 0.45rem 1rem;
  font-size: 0.85rem; outline: none; background: #f1f3f4;
  &:focus { border-color: #1a73e8; background: #fff; }
}
.chat-send-btn {
  border: none; background: #1a73e8; color: #fff; border-radius: 50%;
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; &:disabled { opacity: 0.5; }
  &:hover:not(:disabled) { background: #1557b0; }
}

/* Control bar */
.meeting-controls {
  padding: 0.8rem 1.5rem; background: #2d2e31; border-top: 1px solid #3c4043;
  display: flex; justify-content: center;
}
.controls-center { display: flex; align-items: center; gap: 0.5rem; }
.ctrl-btn {
  width: 48px; height: 48px; border-radius: 50%; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 1.15rem; transition: all 0.2s;
  background: #3c4043; color: #e8eaed; position: relative;
  &:hover { background: #4a4b4f; }
  &.off { background: #ea4335; color: #fff; }
  &.active { background: #394457; color: #8ab4f8; }
}
.ctrl-leave { background: #ea4335; color: #fff; &:hover { background: #d93025; } }
.ctrl-end { background: #c5221f; color: #fff; &:hover { background: #a31815; } }
.ctrl-divider { width: 1px; height: 32px; background: #5f6368; margin: 0 0.4rem; }
.ctrl-badge {
  position: absolute; top: 2px; right: 2px; min-width: 18px; height: 18px;
  background: #ea4335; color: #fff; font-size: 0.65rem; font-weight: 700;
  border-radius: 9px; display: flex; align-items: center; justify-content: center;
}

/* Panel slide transition */
.panel-slide-enter-active, .panel-slide-leave-active { transition: all 0.25s ease; }
.panel-slide-enter-from, .panel-slide-leave-to { transform: translateX(100%); opacity: 0; }

/* ============================== PRE-JOIN ============================== */
.prejoin-card {
  background: #fff; border: 1px solid #e7edf5; border-radius: 16px;
  overflow: hidden; max-width: 900px; margin: 0 auto;
}
.prejoin-main { display: flex; gap: 2rem; padding: 2rem; align-items: center; }
.prejoin-video-wrapper {
  width: 420px; height: 280px; border-radius: 12px; overflow: hidden;
  background: #202124; position: relative; flex-shrink: 0;
}
.prejoin-video {
  width: 100%; height: 100%;
  :deep(video) { width: 100%; height: 100%; object-fit: cover; }
}
.prejoin-controls {
  position: absolute; bottom: 1rem; left: 50%; transform: translateX(-50%);
  display: flex; gap: 0.5rem;
}
.prejoin-ctrl-btn {
  width: 44px; height: 44px; border-radius: 50%; border: none;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; cursor: pointer; transition: all 0.2s;
  background: rgba(60, 64, 67, 0.8); color: #fff;
  &:hover { background: rgba(60, 64, 67, 1); }
  &.off { background: #ea4335; }
}
.prejoin-info { flex: 1; text-align: left;
  h2 { font-size: 1.5rem; font-weight: 700; color: #1a2332; margin-bottom: 0.5rem; }
}
.prejoin-meta { font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem; }

@media (max-width: 768px) {
  .prejoin-main { flex-direction: column; }
  .prejoin-video-wrapper { width: 100%; height: 220px; }
  .meeting-panel { width: 100%; position: absolute; right: 0; top: 0; bottom: 0; z-index: 10; }
  .video-grid { grid-template-columns: 1fr !important; }
  .ctrl-btn { width: 42px; height: 42px; font-size: 1rem; }
}

/* ============================== MANAGEMENT MODE ============================== */
.live-session-page { max-width: 1100px; margin: 0 auto; }
.back-link { color: #6b7280; text-decoration: none; font-size: 0.875rem; &:hover { color: #2453a7; } }
.page-title { font-size: 1.75rem; font-weight: 700; color: #1a2332; }
.page-subtitle { color: #6b7280; font-size: 0.95rem; }

.btn-primary-custom {
  background: #2453a7; color: #fff; border: none; border-radius: 8px;
  padding: 0.5rem 1.2rem; font-weight: 500; font-size: 0.875rem;
  &:hover { background: #1a3f8a; color: #fff; } &:disabled { opacity: 0.6; }
}
.btn-outline-custom {
  background: transparent; border: 1px solid #e7edf5; color: #4b5563; border-radius: 6px;
  padding: 0.35rem 0.6rem; font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}

.status-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 6px;
  &.badge-live { background: rgba(24,121,78,0.1); color: #18794e; }
  &.badge-scheduled { background: rgba(180,83,9,0.1); color: #b45309; }
  &.badge-ended { background: rgba(107,114,128,0.1); color: #6b7280; }
}

.form-card, .tips-card { background: #fff; border: 1px solid #e7edf5; border-radius: 12px; overflow: hidden; }
.form-card-header, .tips-header { padding: 1rem 1.5rem; font-weight: 600; color: #1a2332; border-bottom: 1px solid #e7edf5; font-size: 0.95rem; }
.form-card-body { padding: 1.5rem; }
.tips-card { background: #fefce8; border-color: #fde68a; }
.tips-header { background: transparent; border-bottom-color: #fde68a; color: #92400e; }
.tips-list { list-style: none; padding: 1rem 1.5rem; margin: 0;
  li { padding: 0.5rem 0; font-size: 0.875rem; color: #4b5563; }
}
.form-label-custom { font-size: 0.85rem; font-weight: 600; color: #374151; margin-bottom: 0.35rem; display: block; }
.form-input-custom, .form-select-custom {
  width: 100%; padding: 0.55rem 0.9rem; border: 1px solid #e7edf5; border-radius: 8px;
  font-size: 0.875rem; color: #1a2332; background: #fafbfd;
  &:focus { outline: none; border-color: #2453a7; box-shadow: 0 0 0 3px rgba(36,83,167,0.08); }
}
.form-select-custom { appearance: auto; }

.detail-card, .action-card { background: #fff; border: 1px solid #e7edf5; border-radius: 12px; overflow: hidden; }
.detail-card-header, .action-card-header {
  padding: 0.9rem 1.3rem; font-weight: 600; color: #1a2332;
  border-bottom: 1px solid #e7edf5; font-size: 0.9rem; display: flex; align-items: center;
}
.detail-card-body { padding: 0; }
.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.8rem 1.3rem; border-bottom: 1px solid #f3f4f6;
  &:last-child { border-bottom: none; }
}
.detail-label { font-size: 0.82rem; color: #6b7280; font-weight: 500; }
.detail-value { font-size: 0.875rem; color: #1a2332; }

.action-card-body { padding: 0.5rem; }
.action-btn {
  display: flex; align-items: center; gap: 0.6rem; width: 100%;
  padding: 0.7rem 1rem; border: none; background: none; border-radius: 8px;
  font-size: 0.85rem; color: #4b5563; cursor: pointer;
  &:hover { background: #f6f8fc; }
  &.action-btn-success { color: #18794e; &:hover { background: rgba(24,121,78,0.08); } }
  &.action-btn-danger { color: #dc2626; &:hover { background: rgba(220,38,38,0.06); } }
}

.alert-info-custom {
  background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af;
  border-radius: 8px; padding: 0.7rem 1rem; font-size: 0.85rem;
}

.copy-toast {
  position: fixed; bottom: 2rem; right: 2rem; background: #1a2332; color: #fff;
  padding: 0.7rem 1.3rem; border-radius: 10px; font-size: 0.875rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15); z-index: 10000;
  animation: fadeInUp 0.3s ease;
}
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>