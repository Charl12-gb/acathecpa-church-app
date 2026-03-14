<template>
    <div class="container py-5">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="mb-1">Sessions Live</h1>
              <p class="text-muted mb-0">Gérez vos sessions en direct</p>
            </div>
            <RouterLink to="/live-session" class="btn btn-primary">
              <i class="bi bi-plus-circle me-2"></i>Nouvelle session
            </RouterLink>
          </div>
        </div>
      </div>
  
      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                  <i class="bi bi-camera-video text-primary fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Total sessions</h6>
                  <h3 class="mb-0">{{ sessions.length }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                  <i class="bi bi-broadcast text-success fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">En direct</h6>
                  <h3 class="mb-0">{{ liveSessions }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                  <i class="bi bi-calendar-event text-warning fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Programmées</h6>
                  <h3 class="mb-0">{{ scheduledSessions }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                  <i class="bi bi-people text-info fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Total participants</h6>
                  <h3 class="mb-0">{{ totalParticipants }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Sessions List -->
      <div class="row g-4">
        <div v-for="session in sessions" :key="session.id" class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-6">
                  <div class="d-flex align-items-center mb-3">
                    <div 
                      class="rounded-circle p-2 me-3"
                      :class="session.status === 'live' ? 'bg-success bg-opacity-10' : 'bg-warning bg-opacity-10'"
                    >
                      <i 
                        class="bi fs-4"
                        :class="[
                          session.status === 'live' ? 'bi-broadcast text-success' : 'bi-calendar-event text-warning'
                        ]"
                      ></i>
                    </div>
                    <div>
                      <h5 class="mb-1">{{ session.title }}</h5>
                      <p class="mb-0 text-muted">{{ session.description }}</p>
                    </div>
                  </div>
  
                  <div class="d-flex flex-wrap gap-3">
                    <div class="d-flex align-items-center">
                      <i class="bi bi-calendar me-2 text-muted"></i>
                      <span>{{ formatDate(session.scheduledFor) }}</span>
                    </div>
                    <div class="d-flex align-items-center">
                      <i class="bi bi-clock me-2 text-muted"></i>
                      <span>{{ session.duration }} minutes</span>
                    </div>
                    <div class="d-flex align-items-center">
                      <i class="bi bi-people me-2 text-muted"></i>
                      <span>{{ session.participants.length }} participants</span>
                    </div>
                  </div>
                </div>
  
                <div class="col-md-6 text-md-end mt-3 mt-md-0">
                  <div 
                    class="badge mb-3"
                    :class="session.status === 'live' ? 'bg-success' : 'bg-warning'"
                  >
                    {{ session.status === 'live' ? 'En direct' : 'Programmée' }}
                  </div>
  
                  <div class="btn-group d-flex">
                    <button 
                      v-if="session.status === 'scheduled'"
                      class="btn btn-primary"
                      @click="startSession(session.id)"
                    >
                      <i class="bi bi-play-circle me-2"></i>Démarrer
                    </button>
                    <button 
                      v-else-if="session.status === 'live'"
                      class="btn btn-danger"
                      @click="endSession(session.id)"
                    >
                      <i class="bi bi-stop-circle me-2"></i>Terminer
                    </button>
                    <button 
                      class="btn btn-outline-primary"
                      @click="copySessionLink(session.id)"
                    >
                      <i class="bi bi-link-45deg me-2"></i>Copier le lien
                    </button>
                    <button 
                      class="btn btn-outline-primary"
                      @click="shareSession(session)"
                    >
                      <i class="bi bi-share me-2"></i>Partager
                    </button>
                    <RouterLink 
                      :to="`/live-session/${session.id}`"
                      class="btn btn-outline-primary"
                    >
                      <i class="bi bi-pencil me-2"></i>Modifier
                    </RouterLink>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Empty State -->
      <div v-if="sessions.length === 0" class="text-center py-5">
        <div class="mb-4">
          <i class="bi bi-camera-video display-1 text-muted"></i>
        </div>
        <h3>Aucune session programmée</h3>
        <p class="text-muted">Commencez par créer votre première session live</p>
        <RouterLink to="/live-session" class="btn btn-primary">
          Créer une session
        </RouterLink>
      </div>
  
      <!-- Share Modal -->
      <div 
        class="modal fade" 
        id="shareModal" 
        tabindex="-1" 
        aria-labelledby="shareModalLabel" 
        aria-hidden="true"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="shareModalLabel">Partager la session</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Lien de la session</label>
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    :value="currentSessionLink" 
                    readonly
                  >
                  <button 
                    class="btn btn-outline-primary"
                    @click="copyToClipboard(currentSessionLink)"
                  >
                    <i class="bi bi-clipboard"></i>
                  </button>
                </div>
              </div>
              <div class="d-flex gap-2">
                <button 
                  class="btn btn-outline-primary w-100"
                  @click="shareViaEmail"
                >
                  <i class="bi bi-envelope me-2"></i>Email
                </button>
                <button 
                  class="btn btn-outline-primary w-100"
                  @click="shareViaWhatsApp"
                >
                  <i class="bi bi-whatsapp me-2"></i>WhatsApp
                </button>
                <button 
                  class="btn btn-outline-primary w-100"
                  @click="shareViaTelegram"
                >
                  <i class="bi bi-telegram me-2"></i>Telegram
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useVideoConferenceStore } from '../../../stores/videoConference'
  import type { LiveSession } from '../../../stores/videoConference'
  
  const videoStore = useVideoConferenceStore()
  
  // Sample data (replace with actual API calls)
  const sessions = ref<LiveSession[]>([
    {
      id: 1,
      courseId: 1,
      title: 'Introduction au Marketing Digital',
      description: 'Session interactive sur les bases du marketing digital',
      scheduledFor: '2024-03-20T14:00:00',
      duration: 60,
      hostId: 1,
      status: 'scheduled',
      participants: [1, 2, 3, 4, 5]
    },
    {
      id: 2,
      courseId: 2,
      title: 'Workshop JavaScript Avancé',
      description: 'Session pratique sur les concepts avancés de JavaScript',
      scheduledFor: '2024-03-21T15:00:00',
      duration: 90,
      hostId: 1,
      status: 'live',
      participants: [1, 2, 3]
    }
  ])
  
  // Computed
  const liveSessions = computed(() => 
    sessions.value.filter(session => session.status === 'live').length
  )
  
  const scheduledSessions = computed(() => 
    sessions.value.filter(session => session.status === 'scheduled').length
  )
  
  const totalParticipants = computed(() => 
    sessions.value.reduce((sum, session) => sum + session.participants.length, 0)
  )
  
  // Current session for sharing
  const currentSessionLink = ref('')
  
  // Methods
  const formatDate = (date: string) => {
    return new Date(date).toLocaleString()
  }
  
  const startSession = async (sessionId: number) => {
    try {
      // Update session status
      const session = sessions.value.find(s => s.id === sessionId)
      if (session) {
        session.status = 'live'
      }
      
      // Navigate to live session
      window.location.href = `/live-session/${sessionId}`
    } catch (error) {
      console.error('Failed to start session:', error)
    }
  }
  
  const endSession = async (sessionId: number) => {
    if (confirm('Êtes-vous sûr de vouloir terminer cette session ?')) {
      try {
        const session = sessions.value.find(s => s.id === sessionId)
        if (session) {
          session.status = 'ended'
        }
      } catch (error) {
        console.error('Failed to end session:', error)
      }
    }
  }
  
  const copySessionLink = (sessionId: number) => {
    const link = `${window.location.origin}/join-session/${sessionId}`
    navigator.clipboard.writeText(link)
      .then(() => alert('Lien copié !'))
      .catch(err => console.error('Failed to copy:', err))
  }
  
  const shareSession = (session: LiveSession) => {
    currentSessionLink.value = `${window.location.origin}/join-session/${session.id}`
    // Open modal (using Bootstrap)
    const modal = new bootstrap.Modal(document.getElementById('shareModal'))
    modal.show()
  }
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => alert('Copié !'))
      .catch(err => console.error('Failed to copy:', err))
  }
  
  const shareViaEmail = () => {
    const subject = encodeURIComponent('Invitation à une session live')
    const body = encodeURIComponent(`Rejoignez-moi pour une session live : ${currentSessionLink.value}`)
    window.open(`mailto:?subject=${subject}&body=${body}`)
  }
  
  const shareViaWhatsApp = () => {
    const text = encodeURIComponent(`Rejoignez-moi pour une session live : ${currentSessionLink.value}`)
    window.open(`https://wa.me/?text=${text}`)
  }
  
  const shareViaTelegram = () => {
    const text = encodeURIComponent(`Rejoignez-moi pour une session live : ${currentSessionLink.value}`)
    window.open(`https://t.me/share/url?url=${currentSessionLink.value}&text=${text}`)
  }
  </script>
  
  <style scoped>
  .rounded-circle {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .badge {
    padding: 0.5rem 1rem;
  }
  
  .btn-group {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .btn-group .btn {
    flex: 1;
  }
  
  @media (max-width: 768px) {
    .btn-group {
      flex-direction: column;
    }
  }
  </style>