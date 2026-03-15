<template>
  <div class="my-content-page">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h1 class="page-title mb-1">Mes Contenus</h1>
          <p class="page-subtitle mb-0">Gérez vos articles et podcasts</p>
        </div>
        <RouterLink to="/content/editor" class="btn btn-primary-custom">
          <i class="bi bi-plus-lg me-2"></i>Créer un contenu
        </RouterLink>
      </div>
    </div>

    <!-- Stats Strip -->
    <div class="stats-strip mb-4">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(36,83,167,0.1);">
          <i class="bi bi-file-text" style="color: #2453a7;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Total contenus</span>
          <span class="stat-value">{{ userContents.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(24,121,78,0.1);">
          <i class="bi bi-check-circle" style="color: #18794e;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Publiés</span>
          <span class="stat-value">{{ publishedCount }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(180,83,9,0.1);">
          <i class="bi bi-pencil" style="color: #b45309;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Brouillons</span>
          <span class="stat-value">{{ draftCount }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(107,114,128,0.1);">
          <i class="bi bi-star" style="color: #6b7280;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Premium</span>
          <span class="stat-value">{{ premiumCount }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card app-card filter-card">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="input-group">
                  <span class="input-group-text bg-transparent">
                    <i class="bi bi-search"></i>
                  </span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="filters.search"
                    placeholder="Rechercher un contenu..."
                  >
                </div>
              </div>
              <div class="col-md-4">
                <select v-model="filters.type" class="form-select">
                  <option value="all">Tous les types</option>
                  <option value="article">Articles</option>
                  <option value="podcast">Podcasts</option>
                </select>
              </div>
              <div class="col-md-4">
                <select v-model="filters.status" class="form-select">
                  <option value="all">Tous les statuts</option>
                  <option value="published">Publiés</option>
                  <option value="draft">Brouillons</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content List -->
    <div class="row g-4">
      <div v-for="content in filteredContents" :key="content.id" class="col-12">
        <div class="card app-card list-card">
          <div class="card-body">
            <div class="row">
              <div class="col-md-3">
                <img 
                  :src="content.mediaUrl || 'https://placehold.co/400x200?text=Content'" 
                  class="img-fluid rounded mb-3 mb-md-0"
                  :alt="content.title"
                >
              </div>
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-2">
                  <h5 class="mb-0 me-2">{{ content.title }}</h5>
                  <span 
                    class="badge"
                    :class="content.status === 'published' ? 'bg-success' : 'bg-warning text-dark'"
                  >
                    {{ content.status === 'published' ? 'Publié' : 'Brouillon' }}
                  </span>
                </div>

                <p class="text-muted mb-3">{{ content.description }}</p>

                <div class="d-flex flex-wrap gap-3 mb-3">
                  <div class="d-flex align-items-center">
                    <i class="bi bi-calendar me-2 text-muted"></i>
                    <span>{{ new Date(content.created_at).toLocaleDateString() }}</span>
                  </div>
                  <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark me-2 text-muted"></i>
                    <span>{{ content.type }}</span>
                  </div>
                  <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark-text me-2 text-muted"></i>
                    <span>{{ content.format }}</span>
                  </div>
                </div>

                <div class="d-flex flex-wrap gap-2">
                  <span 
                    v-for="tag in content.tags" 
                    :key="tag"
                    class="badge bg-light text-dark"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div class="col-md-3">
                <div class="d-grid gap-2">
                  <RouterLink 
                    :to="`/content/editor/${content.id}`"
                    class="btn btn-outline-custom"
                  >
                    <i class="bi bi-pencil me-2"></i>Modifier
                  </RouterLink>
                  <button 
                    v-if="content.status === 'draft'"
                    class="btn btn-success-custom"
                    @click="publishContent(content.id)"
                  >
                    <i class="bi bi-check-circle me-2"></i>Publier
                  </button>
                  <button 
                    class="btn btn-outline-danger-custom"
                    @click="deleteContent(content.id)"
                  >
                    <i class="bi bi-trash me-2"></i>Supprimer
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredContents.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="bi bi-file-earmark-x"></i>
      </div>
      <h3>Aucun contenu trouvé</h3>
      <p class="text-muted">Commencez par créer votre premier contenu</p>
      <RouterLink to="/content/editor" class="btn btn-primary-custom">
        <i class="bi bi-plus-lg me-2"></i>Créer un contenu
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useContentStore } from '../../../stores/content'
import type { Content } from '../../../stores/content'

const contentStore = useContentStore()

// State
const userContents = ref<Content[]>([])
const loading = ref(false)
const error = ref('')

// Filters
const filters = ref({
  search: '',
  type: 'all',
  status: 'all'
})

// Computed
const filteredContents = computed(() => {
  let filtered = [...userContents.value]
  
  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(content => 
      content.title.toLowerCase().includes(search) ||
      content.description.toLowerCase().includes(search)
    )
  }
  
  // Type filter
  if (filters.value.type !== 'all') {
    filtered = filtered.filter(content => content.type === filters.value.type)
  }
  
  // Status filter
  if (filters.value.status !== 'all') {
    filtered = filtered.filter(content => content.status === filters.value.status)
  }
  
  return filtered
})

const publishedCount = computed(() => 
  userContents.value.filter(content => content.status === 'published').length
)

const draftCount = computed(() => 
  userContents.value.filter(content => content.status === 'draft').length
)

const premiumCount = computed(() => 
  userContents.value.filter(content => content.isPremium).length
)

// Methods
const loadContents = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const data = await contentStore.getUserContents()
    userContents.value = data
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const publishContent = async (contentId: number) => {
  try {
    await contentStore.publishContent(contentId)
    await loadContents()
  } catch (err: any) {
    error.value = err.message
  }
}

const deleteContent = async (contentId: number) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce contenu ?')) {
    try {
      await contentStore.deleteContent(contentId)
      await loadContents()
    } catch (err: any) {
      error.value = err.message
    }
  }
}

// Load contents on mount
onMounted(() => {
  loadContents()
})
</script>

<style scoped lang="scss">
.my-content-page {
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

.btn-primary-custom {
  background: #2453a7;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-weight: 500;
  font-size: 0.875rem;
  &:hover { background: #1a3f8a; color: #fff; }
}

.btn-success-custom {
  background: #18794e;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.45rem 0.8rem;
  font-size: 0.8rem;
  &:hover { background: #126b42; color: #fff; }
}

.btn-outline-custom {
  background: transparent;
  border: 1px solid #e7edf5;
  color: #4b5563;
  border-radius: 6px;
  padding: 0.45rem 0.8rem;
  font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}

.btn-outline-danger-custom {
  background: transparent;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 6px;
  padding: 0.45rem 0.8rem;
  font-size: 0.8rem;
  &:hover { background: #fef2f2; }
}

.app-card {
  border: 1px solid #e7edf5;
  border-radius: 12px;
  box-shadow: none;
  transition: transform 0.2s, border-color 0.2s;
  &:hover {
    transform: translateY(-2px);
    border-color: #d7e3f4;
  }
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

.list-card img {
  border-radius: 10px;
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

.badge {
  padding: 0.4rem 0.75rem;
}

// Responsive
@media (max-width: 768px) {
  .stats-strip { grid-template-columns: repeat(2, 1fr); }
}
</style>