<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-1">Articles</h1>
        <p class="text-muted mb-0">Découvrez nos derniers articles et ressources</p>
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
                    placeholder="Rechercher un article..."
                  >
                </div>
              </div>
              <div class="col-md-3">
                <select v-model="filters.tag" class="form-select">
                  <option value="">Tous les tags</option>
                  <option v-for="tag in tags" :key="tag" :value="tag">
                    {{ tag }}
                  </option>
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

    <!-- Articles Grid -->
    <div class="row g-4">
      <div v-for="article in filteredArticles" :key="article.id" class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <img 
            v-if="article.mediaUrl" 
            :src="article.mediaUrl" 
            class="card-img-top" 
            :alt="article.title"
            style="height: 200px; object-fit: cover;"
          >
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span 
                class="badge"
                :class="article.format === 'text' ? 'bg-primary' : 
                       article.format === 'video' ? 'bg-danger' : 'bg-success'"
              >
                {{ article.format }}
              </span>
              <small class="text-muted">
                {{ new Date(article.created_at).toLocaleDateString() }}
              </small>
            </div>
            
            <h5 class="card-title mb-3">{{ article.title }}</h5>
            <p class="card-text text-muted">{{ article.description }}</p>
            
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-light p-2 me-2">
                <i class="bi bi-person-circle text-primary"></i>
              </div>
              <span>{{ article.author.name }}</span>
            </div>
            
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span 
                v-for="tag in article.tags" 
                :key="tag"
                class="badge bg-light text-dark"
              >
                {{ tag }}
              </span>
            </div>
            
            <RouterLink 
              :to="`/articles/${article.id}`"
              class="btn btn-primary w-100"
            >
              Lire l'article
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredArticles.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-journal-x display-1 text-muted"></i>
      </div>
      <h3>Aucun article trouvé</h3>
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
const articles = ref<Content[]>([])
const loading = ref(false)
const error = ref('')

// Filters
const filters = ref({
  search: '',
  tag: '',
  sort: 'recent'
})

// Sample tags (replace with actual tags from your backend)
const tags = ['Development', 'Business', 'Marketing', 'Design', 'Technology']

// Load articles
const loadArticles = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // const data = await contentStore.getContents('article')
    // articles.value = data
    articles.value =[
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

// Computed filtered articles
const filteredArticles = computed(() => {
  let filtered = [...articles.value]
  
  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(article => 
      article.title.toLowerCase().includes(search) ||
      article.description.toLowerCase().includes(search)
    )
  }
  
  // Tag filter
  if (filters.value.tag) {
    filtered = filtered.filter(article => 
      article.tags.includes(filters.value.tag)
    )
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
    tag: '',
    sort: 'recent'
  }
}

// Load articles on mount
onMounted(() => {
  loadArticles()
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