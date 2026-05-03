<template>
  <div class="live-sessions-page">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h1 class="page-title mb-1">Sessions Live</h1>
          <p class="page-subtitle mb-0">Gérez et planifiez vos sessions en direct</p>
        </div>
        <RouterLink to="/live-session" class="btn btn-primary-custom">
          <i class="bi bi-plus-lg me-2"></i>Nouvelle session
        </RouterLink>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p class="text-muted mt-3">Chargement des sessions...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger d-flex align-items-center">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-auto" @click="fetchSessions">Réessayer</button>
    </div>

    <template v-else>
      <!-- Stats Strip -->
      <div class="stats-strip mb-4">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(36,83,167,0.1);">
            <i class="bi bi-camera-video" style="color: #2453a7;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-label">Total sessions</span>
            <span class="stat-value">{{ sessions.length }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(24,121,78,0.1);">
            <i class="bi bi-broadcast" style="color: #18794e;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-label">En direct</span>
            <span class="stat-value">{{ liveCount }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(180,83,9,0.1);">
            <i class="bi bi-calendar-event" style="color: #b45309;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-label">Programmées</span>
            <span class="stat-value">{{ scheduledCount }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(107,114,128,0.1);">
            <i class="bi bi-check-circle" style="color: #6b7280;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-label">Terminées</span>
            <span class="stat-value">{{ endedCount }}</span>
          </div>
        </div>
      </div>

      <!-- Filter Tabs -->
      <div class="filter-tabs mb-4">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: activeFilter === tab.value }"
          @click="activeFilter = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="filter-count">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Sessions List -->
      <div class="sessions-list" v-if="filteredSessions.length > 0">
        <div v-for="session in filteredSessions" :key="session.id" class="session-card">
          <div class="session-card-left">
            <div class="session-status-indicator" :class="'status-' + session.status"></div>
            <div class="session-info">
              <div class="d-flex align-items-center gap-2 mb-1">
                <h5 class="session-title mb-0">{{ session.title }}</h5>
                <span class="status-badge" :class="'badge-' + session.status">
                  <i class="bi" :class="statusIcon(session.status)"></i>
                  {{ statusLabel(session.status) }}
                </span>
              </div>
              <p class="session-desc mb-2" v-if="session.description">{{ session.description }}</p>
              <div class="session-meta">
                <span class="meta-item">
                  <i class="bi bi-calendar3"></i>
                  {{ formatDate(session.scheduled_for) }}
                </span>
                <span class="meta-item" v-if="session.duration_minutes">
                  <i class="bi bi-clock"></i>
                  {{ session.duration_minutes }} min
                </span>
                <span class="meta-item" v-if="session.host">
                  <i class="bi bi-person"></i>
                  {{ session.host.name }}
                </span>
              </div>
            </div>
          </div>
          <div class="session-card-right">
            <div class="session-actions">
              <button
                v-if="session.status === 'scheduled'"
                class="btn btn-sm btn-success-custom"
                @click="startSession(session.id)"
                :disabled="actionLoading === session.id"
              >
                <i class="bi bi-play-fill me-1"></i>Démarrer
              </button>
              <button
                v-if="session.status === 'live'"
                class="btn btn-sm btn-danger-custom"
                @click="endSession(session.id)"
                :disabled="actionLoading === session.id"
              >
                <i class="bi bi-stop-fill me-1"></i>Terminer
              </button>
              <RouterLink
                v-if="session.status === 'live'"
                :to="`/live-session/${session.id}`"
                class="btn btn-sm btn-primary-custom"
              >
                <i class="bi bi-box-arrow-up-right me-1"></i>Rejoindre
              </RouterLink>
              <button
                v-if="session.status !== 'ended'"
                class="btn btn-sm btn-outline-custom"
                @click="copySessionLink(session.id)"
              >
                <i class="bi bi-link-45deg"></i>
              </button>
              <button
                v-if="session.status === 'ended'"
                class="btn btn-sm btn-outline-custom"
                @click="rescheduleSession(session.id)"
                :disabled="actionLoading === session.id"
              >
                <i class="bi bi-arrow-repeat me-1"></i>Reprogrammer
              </button>
              <RouterLink
                v-if="session.status !== 'ended'"
                :to="`/live-session/${session.id}`"
                class="btn btn-sm btn-outline-custom"
              >
                <i class="bi bi-pencil"></i>
              </RouterLink>
              <RouterLink
                v-if="session.status === 'ended'"
                :to="`/live-session/${session.id}`"
                class="btn btn-sm btn-outline-custom"
              >
                <i class="bi bi-eye me-1"></i>Détails
              </RouterLink>
              <button
                class="btn btn-sm btn-outline-danger-custom"
                @click="deleteSession(session.id)"
                :disabled="actionLoading === session.id"
              >
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="bi bi-camera-video"></i>
        </div>
        <h3>{{ activeFilter === 'all' ? 'Aucune session programmée' : 'Aucune session ' + filterLabel }}</h3>
        <p class="text-muted">
          {{ activeFilter === 'all' ? 'Commencez par créer votre première session live' : 'Aucune session ne correspond à ce filtre' }}
        </p>
        <RouterLink v-if="activeFilter === 'all'" to="/live-session" class="btn btn-primary-custom">
          <i class="bi bi-plus-lg me-2"></i>Créer une session
        </RouterLink>
      </div>
    </template>

    <!-- Toast for copy feedback -->
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
import { ref, computed, onMounted } from 'vue'
import { getAllLiveSessions, updateLiveSessionStatus, deleteLiveSession as apiDeleteSession, rescheduleLiveSession } from '../../../services/api/liveSession'
import type { LiveSession } from '../../../types/api/liveSessionTypes'

const sessions = ref<LiveSession[]>([])
const loading = ref(true)
const error = ref('')
const actionLoading = ref<number | null>(null)
const activeFilter = ref('all')
const toastMessage = ref('')

const liveCount = computed(() => sessions.value.filter(s => s.status === 'live').length)
const scheduledCount = computed(() => sessions.value.filter(s => s.status === 'scheduled').length)
const endedCount = computed(() => sessions.value.filter(s => s.status === 'ended').length)

const filterTabs = computed(() => [
  { label: 'Toutes', value: 'all', count: sessions.value.length },
  { label: 'En direct', value: 'live', count: liveCount.value },
  { label: 'Programmées', value: 'scheduled', count: scheduledCount.value },
  { label: 'Terminées', value: 'ended', count: endedCount.value },
])

const filterLabel = computed(() => {
  const tab = filterTabs.value.find(t => t.value === activeFilter.value)
  return tab ? tab.label.toLowerCase() : ''
})

const filteredSessions = computed(() => {
  if (activeFilter.value === 'all') return sessions.value
  return sessions.value.filter(s => s.status === activeFilter.value)
})

const statusLabel = (status: string) => {
  switch (status) {
    case 'live': return 'En direct'
    case 'scheduled': return 'Programmée'
    case 'ended': return 'Terminée'
    default: return status
  }
}

const statusIcon = (status: string) => {
  switch (status) {
    case 'live': return 'bi-broadcast'
    case 'scheduled': return 'bi-calendar-event'
    case 'ended': return 'bi-check-circle'
    default: return 'bi-circle'
  }
}

const formatDate = (date: string) => {
  const d = new Date(date)
  return d.toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchSessions = async () => {
  loading.value = true
  error.value = ''
  try {
    sessions.value = await getAllLiveSessions()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Impossible de charger les sessions'
  } finally {
    loading.value = false
  }
}

const startSession = async (sessionId: number) => {
  actionLoading.value = sessionId
  try {
    const updated = await updateLiveSessionStatus(sessionId, 'live')
    const idx = sessions.value.findIndex(s => s.id === sessionId)
    if (idx !== -1) sessions.value[idx] = updated
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors du démarrage')
  } finally {
    actionLoading.value = null
  }
}

const endSession = async (sessionId: number) => {
  if (!confirm('Êtes-vous sûr de vouloir terminer cette session ?')) return
  actionLoading.value = sessionId
  try {
    const updated = await updateLiveSessionStatus(sessionId, 'ended')
    const idx = sessions.value.findIndex(s => s.id === sessionId)
    if (idx !== -1) sessions.value[idx] = updated
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la terminaison')
  } finally {
    actionLoading.value = null
  }
}

const deleteSession = async (sessionId: number) => {
  if (!confirm('Supprimer cette session définitivement ?')) return
  actionLoading.value = sessionId
  try {
    await apiDeleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la suppression')
  } finally {
    actionLoading.value = null
  }
}

const copySessionLink = (sessionId: number) => {
  const link = `${window.location.origin}/live-session/${sessionId}`
  navigator.clipboard.writeText(link).then(() => {
    toastMessage.value = 'Lien copié !'
    setTimeout(() => { toastMessage.value = '' }, 2000)
  })
}

const rescheduleSession = async (sessionId: number) => {
  rescheduleTargetId.value = sessionId
  const def = getDefaultDateTime()
  rescheduleForm.value = { date: def.date, time: def.time, duration_minutes: null }
  showRescheduleModal.value = true
}

// Modal state
const showRescheduleModal = ref(false)
const rescheduleTargetId = ref<number | null>(null)
const rescheduleLoading = ref(false)
const rescheduleForm = ref<{ date: string; time: string; duration_minutes: number | null }>({ date: '', time: '', duration_minutes: null })

const getDefaultDateTime = () => {
  const d = new Date(Date.now() + 15 * 60 * 1000)
  const date = d.toISOString().split('T')[0]
  const time = d.toTimeString().slice(0, 5)
  return { date, time }
}

const closeRescheduleModal = () => {
  showRescheduleModal.value = false
  rescheduleTargetId.value = null
}

const confirmReschedule = async () => {
  if (!rescheduleTargetId.value || !rescheduleForm.value.date || !rescheduleForm.value.time) return
  rescheduleLoading.value = true
  try {
    const scheduled_for = `${rescheduleForm.value.date}T${rescheduleForm.value.time}:00`
    const payload: any = { scheduled_for }
    if (rescheduleForm.value.duration_minutes) payload.duration_minutes = rescheduleForm.value.duration_minutes
    const updated = await rescheduleLiveSession(rescheduleTargetId.value, payload)
    const idx = sessions.value.findIndex(s => s.id === rescheduleTargetId.value)
    if (idx !== -1) sessions.value[idx] = updated
    toastMessage.value = 'Session reprogrammée !'
    setTimeout(() => { toastMessage.value = '' }, 2000)
    closeRescheduleModal()
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Erreur lors de la reprogrammation')
  } finally {
    rescheduleLoading.value = false
  }
}

onMounted(fetchSessions)
</script>

<style scoped lang="scss">
.live-sessions-page {
  max-width: 1100px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a2332;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

// Buttons
.btn-primary-custom {
  background: #2453a7;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: background 0.2s;
  &:hover { background: #1a3f8a; color: #fff; }
}

.btn-success-custom {
  background: #18794e;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.9rem;
  font-weight: 500;
  font-size: 0.8rem;
  &:hover { background: #126b42; color: #fff; }
}

.btn-danger-custom {
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.9rem;
  font-weight: 500;
  font-size: 0.8rem;
  &:hover { background: #b91c1c; color: #fff; }
}

.btn-outline-custom {
  background: transparent;
  border: 1px solid #e7edf5;
  color: #4b5563;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}

.btn-outline-danger-custom {
  background: transparent;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.8rem;
  &:hover { background: #fef2f2; }
}

// Stats Strip
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-card {
  background: #fff;
  border: 1px solid #e7edf5;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.78rem;
  color: #6b7280;
  line-height: 1.2;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a2332;
}

// Filter Tabs
.filter-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #e7edf5;
  padding-bottom: 0;
}

.filter-tab {
  background: none;
  border: none;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.4rem;

  &:hover { color: #2453a7; }

  &.active {
    color: #2453a7;
    font-weight: 600;
    border-bottom-color: #2453a7;
  }
}

.filter-count {
  background: #e7edf5;
  color: #4b5563;
  font-size: 0.7rem;
  padding: 0.1rem 0.4rem;
  border-radius: 9px;
  font-weight: 600;

  .active & {
    background: rgba(36,83,167,0.12);
    color: #2453a7;
  }
}

// Session Cards
.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.session-card {
  background: #fff;
  border: 1px solid #e7edf5;
  border-radius: 12px;
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  transition: box-shadow 0.2s, border-color 0.2s;

  &:hover {
    box-shadow: 0 2px 12px rgba(36,83,167,0.08);
    border-color: #d0d9e8;
  }
}

.session-card-left {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.session-status-indicator {
  width: 4px;
  border-radius: 4px;
  min-height: 50px;
  align-self: stretch;
  flex-shrink: 0;

  &.status-live { background: #18794e; }
  &.status-scheduled { background: #b45309; }
  &.status-ended { background: #9ca3af; }
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a2332;
}

.session-desc {
  font-size: 0.85rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  white-space: nowrap;

  &.badge-live {
    background: rgba(24,121,78,0.1);
    color: #18794e;
  }
  &.badge-scheduled {
    background: rgba(180,83,9,0.1);
    color: #b45309;
  }
  &.badge-ended {
    background: rgba(107,114,128,0.1);
    color: #6b7280;
  }
}

.session-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: #6b7280;

  .bi { font-size: 0.85rem; }
}

.session-card-right {
  flex-shrink: 0;
}

.session-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

// Empty State
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(36,83,167,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;

  .bi { font-size: 2rem; color: #2453a7; }
}

.empty-state h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a2332;
  margin-bottom: 0.5rem;
}

// Toast
.copy-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #1a2332;
  color: #fff;
  padding: 0.7rem 1.3rem;
  border-radius: 10px;
  font-size: 0.875rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  z-index: 9999;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

// Responsive
@media (max-width: 768px) {
  .stats-strip { grid-template-columns: repeat(2, 1fr); }
  .session-card { flex-direction: column; align-items: flex-start; }
  .session-card-right { width: 100%; }
  .session-actions { flex-wrap: wrap; }
  .filter-tabs { overflow-x: auto; flex-wrap: nowrap; }
}

// Reschedule Modal
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.2s ease;
}

.modal-dialog-custom {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slideUp 0.25s ease;
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #e7edf5;
}

.modal-title-custom {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a2332;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  line-height: 1;
  &:hover { color: #1a2332; }
}

.modal-body-custom {
  padding: 1.5rem;
}

.modal-footer-custom {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e7edf5;
}

.form-label-custom {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.35rem;
  display: block;
}

.form-input-custom {
  width: 100%;
  padding: 0.55rem 0.9rem;
  border: 1px solid #e7edf5;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #1a2332;
  background: #fafbfd;
  &:focus { outline: none; border-color: #2453a7; box-shadow: 0 0 0 3px rgba(36,83,167,0.08); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>