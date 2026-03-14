<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">Mes Contenus</h1>
            <p class="text-muted mb-0">Gérez vos articles et podcasts</p>
          </div>
          <RouterLink to="/content/editor" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Créer un contenu
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
                <i class="bi bi-file-text text-primary fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Total contenus</h6>
                <h3 class="mb-0">{{ userContents.length }}</h3>
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
                <i class="bi bi-check-circle text-success fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Publiés</h6>
                <h3 class="mb-0">{{ publishedCount }}</h3>
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
                <i class="bi bi-pencil text-warning fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Brouillons</h6>
                <h3 class="mb-0">{{ draftCount }}</h3>
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
                <i class="bi bi-star text-info fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Premium</h6>
                <h3 class="mb-0">{{ premiumCount }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
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
        <div class="card border-0 shadow-sm">
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
                    class="btn btn-outline-primary"
                  >
                    <i class="bi bi-pencil me-2"></i>Modifier
                  </RouterLink>
                  <button 
                    v-if="content.status === 'draft'"
                    class="btn btn-outline-success"
                    @click="publishContent(content.id)"
                  >
                    <i class="bi bi-check-circle me-2"></i>Publier
                  </button>
                  <button 
                    class="btn btn-outline-danger"
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
    <div v-if="filteredContents.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-file-earmark-x display-1 text-muted"></i>
      </div>
      <h3>Aucun contenu trouvé</h3>
      <p class="text-muted">Commencez par créer votre premier contenu</p>
      <RouterLink to="/content/editor" class="btn btn-primary">
        Créer un contenu
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

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}
</style>