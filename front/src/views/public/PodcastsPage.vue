<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-1">Podcasts</h1>
        <p class="text-muted mb-0">Découvrez nos podcasts éducatifs</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text bg-transparent">
                    <i class="bi bi-search"></i>
                  </span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="filters.search"
                    placeholder="Rechercher un podcast..."
                  >
                </div>
              </div>
              <div class="col-md-3">
                <select v-model="filters.format" class="form-select">
                  <option value="">Tous les formats</option>
                  <option value="audio">Audio</option>
                  <option value="video">Vidéo</option>
                </select>
              </div>
              <div class="col-md-3">
                <select v-model="filters.sort" class="form-select">
                  <option value="recent">Plus récents</option>
                  <option value="popular">Plus populaires</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Podcasts Grid -->
    <div class="row g-4">
      <div v-for="podcast in filteredPodcasts" :key="podcast.id" class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <div class="row g-0">
            <div class="col-md-4">
              <img 
                :src="podcast.mediaUrl || 'https://placehold.co/200x200?text=Podcast'" 
                class="img-fluid rounded-start h-100"
                style="object-fit: cover;"
                :alt="podcast.title"
              >
            </div>
            <div class="col-md-8">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span 
                    class="badge"
                    :class="podcast.format === 'audio' ? 'bg-success' : 'bg-danger'"
                  >
                    {{ podcast.format }}
                  </span>
                  <small class="text-muted">
                    {{ new Date(podcast.created_at).toLocaleDateString() }}
                  </small>
                </div>

                <h5 class="card-title mb-2">{{ podcast.title }}</h5>
                <p class="card-text text-muted">{{ podcast.description }}</p>

                <div class="d-flex align-items-center mb-3">
                  <div class="rounded-circle bg-light p-2 me-2">
                    <i class="bi bi-person-circle text-primary"></i>
                  </div>
                  <span>{{ podcast.author.name }}</span>
                </div>

                <div class="d-flex flex-wrap gap-2 mb-3">
                  <span 
                    v-for="tag in podcast.tags" 
                    :key="tag"
                    class="badge bg-light text-dark"
                  >
                    {{ tag }}
                  </span>
                </div>

                <RouterLink 
                  :to="`/podcasts/${podcast.id}`"
                  class="btn btn-primary w-100"
                >
                  Écouter le podcast
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredPodcasts.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-mic display-1 text-muted"></i>
      </div>
      <h3>Aucun podcast trouvé</h3>
      <p class="text-muted">Essayez de modifier vos critères de recherche</p>
      <button 
        class="btn btn-primary"
        @click="resetFilters"
      >
        Réinitialiser les filtres
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useContentStore } from '../../stores/content'
import type { Content } from '../../stores/content'

const contentStore = useContentStore()

// State
const podcasts = ref<Content[]>([])
const loading = ref(false)
const error = ref('')

// Filters
const filters = ref({
  search: '',
  format: '',
  sort: 'recent'
})

// Load podcasts
const loadPodcasts = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // const data = await contentStore.getContents('podcast')
    // podcasts.value = data
    podcasts.value = [
    {
      "id": "1",
      "title": "Comment améliorer votre référencement SEO en 2025",
      "description": "Découvrez les techniques les plus efficaces pour optimiser votre visibilité sur les moteurs de recherche cette année.",
      "format": "text",
      "mediaUrl": "https://example.com/images/seo-article.jpg",
      "created_at": "2025-04-15T14:30:00Z",
      "author": {
        "id": "a1",
        "name": "Marie Dubois",
        "avatarUrl": "https://example.com/avatars/marie.jpg"
      },
      "tags": ["SEO", "Marketing Digital", "Web"]
    },
    {
      "id": "2",
      "title": "Tutoriel: Créer une application Vue.js en 30 minutes",
      "description": "Un guide pas à pas pour développer rapidement votre première application avec le framework Vue.js.",
      "format": "video",
      "mediaUrl": "https://example.com/images/vuejs-tutorial.jpg",
      "created_at": "2025-04-10T09:15:00Z",
      "author": {
        "id": "a2",
        "name": "Thomas Martin",
        "avatarUrl": "https://example.com/avatars/thomas.jpg"
      },
      "tags": ["Vue.js", "JavaScript", "Frontend", "Tutoriel"]
    },
    {
      "id": "3",
      "title": "L'importance de l'accessibilité web pour votre site",
      "description": "Pourquoi et comment rendre votre site web accessible à tous les utilisateurs, y compris ceux ayant des handicaps.",
      "format": "podcast",
      "mediaUrl": "https://example.com/images/accessibility.jpg",
      "created_at": "2025-04-05T16:45:00Z",
      "author": {
        "id": "a3",
        "name": "Sophie Leroy",
        "avatarUrl": "https://example.com/avatars/sophie.jpg"
      },
      "tags": ["Accessibilité", "UX", "Inclusivité"]
    }
  ]
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Computed filtered podcasts
const filteredPodcasts = computed(() => {
  let filtered = [...podcasts.value]
  
  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(podcast => 
      podcast.title.toLowerCase().includes(search) ||
      podcast.description.toLowerCase().includes(search)
    )
  }
  
  // Format filter
  if (filters.value.format) {
    filtered = filtered.filter(podcast => podcast.format === filters.value.format)
  }
  
  // Sorting
  if (filters.value.sort === 'popular') {
    // Add your popularity sorting logic here
    filtered.sort((a, b) => b.id - a.id)
  } else {
    filtered.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }
  
  return filtered
})

// Reset filters
const resetFilters = () => {
  filters.value = {
    search: '',
    format: '',
    sort: 'recent'
  }
}

// Load podcasts on mount
onMounted(() => {
  loadPodcasts()
})
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.badge {
  padding: 0.5rem 1rem;
}
</style>