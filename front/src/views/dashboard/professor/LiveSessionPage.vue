<template>
  <!-- ======================== MEETING MODE ======================== -->
  <div v-if="inMeeting" class="meeting-container">
    <div class="meeting-topbar">
      <div class="meeting-info">
        <span class="meeting-title">{{ session?.title }}</span>
        <span class="meeting-separator">|</span>
        <span class="meeting-timer">{{ formatDuration(sessionDuration) }}</span>
      </div>
      <div class="meeting-topbar-right">
        <button class="meeting-topbar-btn" @click="copySessionLink">
          <i class="bi bi-link-45deg"></i>
          Copier le lien
        </button>
        <button class="meeting-topbar-btn meeting-topbar-btn-danger" @click="handleLeaveMeeting">
          <i class="bi bi-telephone-x-fill"></i>
          Quitter
        </button>
        <button
          v-if="session?.host_id === currentUser?.id"
          class="meeting-topbar-btn meeting-topbar-btn-end"
          @click="handleEndMeeting"
        >
          <i class="bi bi-stop-circle-fill"></i>
          Terminer pour tous
        </button>
      </div>
    </div>

    <div class="meeting-body">
      <iframe
        v-if="meetingEmbedUrl"
        :src="meetingEmbedUrl"
        class="meeting-iframe"
        allow="camera; microphone; fullscreen; display-capture; autoplay; clipboard-write"
      ></iframe>
      <div v-else class="meeting-fallback">
        <i class="bi bi-camera-video-off"></i>
        <p>Impossible de charger la salle Jitsi.</p>
        <button class="meeting-topbar-btn" @click="handleLeaveMeeting">Retour</button>
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
                <div class="alert alert-info mt-2 small">
                  La session sera intégrée directement dans cette page via Jitsi.
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
                  <span class="detail-label">Durée prévue</span>
                  <span class="detail-value">{{ session.duration_minutes }} minutes</span>
                </div>
                <div class="detail-row" v-if="session.actual_started_at">
                  <span class="detail-label">Démarrée à</span>
                  <span class="detail-value">{{ formatDate(session.actual_started_at) }}</span>
                </div>
                <div class="detail-row" v-if="session.actual_ended_at">
                  <span class="detail-label">Terminée à</span>
                  <span class="detail-value">{{ formatDate(session.actual_ended_at) }}</span>
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
                <button v-if="session.status !== 'ended'" class="action-btn" @click="copySessionLink">
                  <i class="bi bi-link-45deg"></i><span>Copier le lien</span>
                </button>
                <button v-if="session.status === 'scheduled'" class="action-btn action-btn-success" @click="changeStatus('live')" :disabled="actionLoading">
                  <i class="bi bi-play-fill"></i><span>Démarrer la session</span>
                </button>
                <button v-if="session.status === 'ended'" class="action-btn action-btn-reschedule" @click="handleReschedule">
                  <i class="bi bi-arrow-repeat"></i><span>Reprogrammer</span>
                </button>
                <button class="action-btn action-btn-danger" @click="deleteCurrentSession">
                  <i class="bi bi-trash3"></i><span>Supprimer la session</span>
                </button>
              </div>
            </div>

            <!-- Quick attendance summary in sidebar for ended sessions -->
            <div v-if="session.status === 'ended' && attendance" class="action-card mt-3">
              <div class="action-card-header"><i class="bi bi-people me-2"></i>Résumé présence</div>
              <div class="attendance-summary-mini">
                <div class="att-mini-stat">
                  <span class="att-mini-value">{{ attendance.unique_attendees }}</span>
                  <span class="att-mini-label">Participants</span>
                </div>
                <div class="att-mini-stat">
                  <span class="att-mini-value text-success">{{ attendance.attendance_rate ? Math.round(attendance.attendance_rate) + '%' : '—' }}</span>
                  <span class="att-mini-label">Taux</span>
                </div>
                <div class="att-mini-stat">
                  <span class="att-mini-value">{{ formatDuration(attendance.actual_duration_seconds) }}</span>
                  <span class="att-mini-label">Durée</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Attendance Panel (ended sessions) -->
          <div v-if="session.status === 'ended'" class="col-12 mt-4">
            <div class="detail-card attendance-card">
              <div class="detail-card-header">
                <i class="bi bi-people-fill me-2"></i>Détails de présence
              </div>
              <div class="attendance-card-body">
                <div v-if="attendanceLoading" class="text-center py-4">
                  <div class="spinner-border spinner-border-sm text-primary"></div>
                  <p class="text-muted mt-2 mb-0 small">Chargement des données...</p>
                </div>
                <template v-else-if="attendance">
                  <div v-if="attendance.attendees.length > 0" class="table-responsive">
                    <table class="attendance-table">
                      <thead>
                        <tr>
                          <th>Participant</th>
                          <th>Première connexion</th>
                          <th>Temps de présence</th>
                          <th>Connexions</th>
                          <th>Statut</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="att in attendance.attendees" :key="att.user_id">
                          <td>
                            <div class="att-user">
                              <div class="att-avatar">{{ (att.user_name || att.user_email || '#')[0].toUpperCase() }}</div>
                              <div>
                                <div class="att-user-name">{{ att.user_name || `Utilisateur #${att.user_id}` }}</div>
                                <div class="att-user-email" v-if="att.user_email">{{ att.user_email }}</div>
                              </div>
                            </div>
                          </td>
                          <td>{{ att.first_joined_at ? formatDate(att.first_joined_at) : '—' }}</td>
                          <td><span class="att-duration">{{ formatDuration(att.total_duration_seconds) }}</span></td>
                          <td>{{ att.join_count }}</td>
                          <td>
                            <span class="att-status-badge" :class="att.is_present ? 'att-present' : 'att-left'">
                              <i class="bi" :class="att.is_present ? 'bi-circle-fill' : 'bi-dash-circle'"></i>
                              {{ att.is_present ? 'Connecté' : 'Parti' }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="empty-attendance">
                    <i class="bi bi-person-x"></i>
                    <p>Aucun participant n'a été enregistré pour cette session.</p>
                  </div>
                </template>
                <div v-else class="empty-attendance">
                  <i class="bi bi-exclamation-circle"></i>
                  <p>Données de présence non disponibles.</p>
                </div>
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

    <!-- Reschedule Modal -->
    <Teleport to="body">
      <div v-if="showRescheduleModal" class="modal-overlay" @click.self="closeRescheduleModal">
        <div class="modal-dialog-custom">
          <div class="modal-header-custom">
            <h5 class="modal-title-custom"><i class="bi bi-arrow-repeat me-2"></i>Reprogrammer la session</h5>
            <button class="modal-close-btn" @click="closeRescheduleModal">&times;</button>
          </div>
          <div class="modal-body-custom">
            <div class="form-group mb-3">
              <label class="form-label-custom">Nouvelle date <span class="text-danger">*</span></label>
              <input type="date" class="form-input-custom" v-model="rescheduleForm.date" required>
            </div>
            <div class="form-group mb-3">
              <label class="form-label-custom">Nouvelle heure <span class="text-danger">*</span></label>
              <input type="time" class="form-input-custom" v-model="rescheduleForm.time" required>
            </div>
            <div class="form-group mb-3">
              <label class="form-label-custom">Durée (minutes) <span class="text-muted fw-normal">(optionnel)</span></label>
              <input type="number" class="form-input-custom" v-model.number="rescheduleForm.duration_minutes" min="15" max="480" placeholder="60">
            </div>
          </div>
          <div class="modal-footer-custom">
            <button class="btn btn-outline-custom" @click="closeRescheduleModal">Annuler</button>
            <button class="btn btn-primary-custom" @click="confirmReschedule" :disabled="!rescheduleForm.date || !rescheduleForm.time || rescheduleLoading">
              <span v-if="rescheduleLoading" class="spinner-border spinner-border-sm me-2"></span>
              Reprogrammer
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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
  getLiveSessionAttendance,
  rescheduleLiveSession,
} from '../../../services/api/liveSession'
import type { LiveSessionAttendanceSummary } from '../../../types/api/liveSessionTypes'
import { getInstructorCourses } from '../../../services/api/course'
import type { LiveSession } from '../../../types/api/liveSessionTypes'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const videoStore = useVideoConferenceStore()

const currentUser = computed(() => authStore.user)
const isNewSession = computed(() => !route.params.id)
const meetingEmbedUrl = computed(() => videoStore.activeMeetingUrl)

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

// Helper: default date/time = now + 15 minutes
const getDefaultDateTime = () => {
  const d = new Date(Date.now() + 15 * 60 * 1000)
  const date = d.toISOString().split('T')[0]
  const time = d.toTimeString().slice(0, 5)
  return { date, time }
}

// Initialize form defaults for new session
const initFormDefaults = () => {
  const def = getDefaultDateTime()
  sessionForm.value.date = def.date
  sessionForm.value.time = def.time
}

// Meeting state
const inMeeting = ref(false)
const sessionDuration = ref(0)
const durationInterval = ref<ReturnType<typeof setInterval> | null>(null)
const joiningMeeting = ref(false)

// Attendance state
const attendance = ref<LiveSessionAttendanceSummary | null>(null)
const attendanceLoading = ref(false)

// Pre-join state
const previewVideoEl = ref<HTMLElement | null>(null)
const previewAudioOn = ref(true)
const previewVideoOn = ref(true)

// Helpers
const statusLabel = (s: string) => ({ live: 'En direct', scheduled: 'Programmée', ended: 'Terminée' }[s] || s)
const statusIcon = (s: string) => ({ live: 'bi-broadcast', scheduled: 'bi-calendar-event', ended: 'bi-check-circle' }[s] || 'bi-circle')
const formatDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
})
const formatDuration = (seconds: number) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m}:${s.toString().padStart(2, '0')}`
}

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

      // Load attendance for ended sessions
      if (session.value?.status === 'ended') {
        attendanceLoading.value = true
        try { attendance.value = await getLiveSessionAttendance(id) } catch { /* ignore */ }
        attendanceLoading.value = false
      }

      // Start local preview for all non-ended sessions (scheduled/live)
      if (session.value?.status !== 'ended') {
        await initPreview()
      }
    } else {
      // Default date/time for new session form
      initFormDefaults()
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
    await videoStore.joinMeeting(session.value.id, currentUser.value.name || 'Utilisateur')
    inMeeting.value = true

    // Start duration timer
    durationInterval.value = setInterval(() => { sessionDuration.value++ }, 1000)
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

const handleReschedule = () => {
  if (!session.value) return
  const def = getDefaultDateTime()
  rescheduleForm.value = { date: def.date, time: def.time, duration_minutes: session.value.duration_minutes || null }
  showRescheduleModal.value = true
}

// Reschedule modal state
const showRescheduleModal = ref(false)
const rescheduleLoading = ref(false)
const rescheduleForm = ref<{ date: string; time: string; duration_minutes: number | null }>({ date: '', time: '', duration_minutes: null })

const closeRescheduleModal = () => { showRescheduleModal.value = false }

const confirmReschedule = async () => {
  if (!session.value || !rescheduleForm.value.date || !rescheduleForm.value.time) return
  rescheduleLoading.value = true
  try {
    const scheduled_for = `${rescheduleForm.value.date}T${rescheduleForm.value.time}:00`
    const payload: any = { scheduled_for }
    if (rescheduleForm.value.duration_minutes) payload.duration_minutes = rescheduleForm.value.duration_minutes
    const updated = await rescheduleLiveSession(session.value.id, payload)
    session.value = updated
    toastMessage.value = 'Session reprogrammée !'
    setTimeout(() => { toastMessage.value = '' }, 2000)
    closeRescheduleModal()
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la reprogrammation')
  } finally {
    rescheduleLoading.value = false
  }
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

.meeting-topbar-right { display: flex; align-items: center; gap: 0.6rem; }
.meeting-topbar-btn {
  border: 1px solid #4a4b4f;
  background: #3c4043;
  color: #e8eaed;
  border-radius: 999px;
  padding: 0.45rem 0.85rem;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.meeting-topbar-btn-danger { background: #ea4335; border-color: #ea4335; color: #fff; }
.meeting-topbar-btn-end { background: #c5221f; border-color: #c5221f; color: #fff; }

.meeting-body { flex: 1; display: flex; overflow: hidden; }
.meeting-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #111827;
}
.meeting-fallback {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: #e8eaed;
}
.video-off-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  display: flex; align-items: center; justify-content: center;
  background: #3c4043;
}

/* Avatar circles */
.avatar-circle {
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; flex-shrink: 0;
}
.avatar-lg { width: 80px; height: 80px; font-size: 2rem; background: #5f6368; }
.avatar-xl { width: 100px; height: 100px; font-size: 2.5rem; background: #5f6368; }
.avatar-sm { width: 32px; height: 32px; font-size: 0.85rem; background: #5f6368; }

/* Side panel */
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
  .meeting-topbar { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .meeting-topbar-right { flex-wrap: wrap; }
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

/* Reschedule action btn */
.action-btn-reschedule { color: #2453a7; &:hover { background: rgba(36,83,167,0.08); } }

/* Attendance summary mini (sidebar) */
.attendance-summary-mini {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; padding: 1rem;
}
.att-mini-stat { text-align: center; }
.att-mini-value { display: block; font-size: 1.25rem; font-weight: 700; color: #1a2332; }
.att-mini-label { font-size: 0.72rem; color: #6b7280; }

/* Attendance card */
.attendance-card-body { padding: 1.2rem; }
.attendance-table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  font-size: 0.85rem;
  th { padding: 0.65rem 0.8rem; background: #f8fafc; color: #6b7280; font-weight: 600;
       font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.02em;
       border-bottom: 1px solid #e7edf5; text-align: left; }
  td { padding: 0.7rem 0.8rem; border-bottom: 1px solid #f3f4f6; color: #374151; vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f8fafc; }
}
.att-user { display: flex; align-items: center; gap: 0.6rem; }
.att-avatar {
  width: 32px; height: 32px; border-radius: 50%; background: #e7edf5;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700; color: #2453a7; flex-shrink: 0;
}
.att-user-name { font-weight: 500; color: #1a2332; font-size: 0.85rem; }
.att-user-email { font-size: 0.75rem; color: #9ca3af; }
.att-duration { font-family: monospace; font-size: 0.82rem; color: #374151; }
.att-status-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  font-size: 0.75rem; font-weight: 500; padding: 0.2rem 0.55rem; border-radius: 6px;
  &.att-present { background: rgba(24,121,78,0.1); color: #18794e; }
  &.att-left { background: rgba(107,114,128,0.1); color: #6b7280; }
  .bi { font-size: 0.5rem; }
}
.empty-attendance {
  text-align: center; padding: 2rem 1rem; color: #9ca3af;
  .bi { font-size: 2rem; display: block; margin-bottom: 0.5rem; }
  p { margin: 0; font-size: 0.875rem; }
}

/* Reschedule Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5); display: flex;
  align-items: center; justify-content: center; z-index: 10001;
  animation: fadeIn 0.2s ease;
}
.modal-dialog-custom {
  background: #fff; border-radius: 16px; width: 100%; max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2); overflow: hidden;
  animation: slideUp 0.25s ease;
}
.modal-header-custom {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.2rem 1.5rem; border-bottom: 1px solid #e7edf5;
}
.modal-title-custom { font-size: 1.05rem; font-weight: 700; color: #1a2332; margin: 0; }
.modal-close-btn { background: none; border: none; font-size: 1.5rem; color: #6b7280; cursor: pointer; &:hover { color: #1a2332; } }
.modal-body-custom { padding: 1.5rem; }
.modal-footer-custom { display: flex; gap: 0.75rem; justify-content: flex-end; padding: 1rem 1.5rem; border-top: 1px solid #e7edf5; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>