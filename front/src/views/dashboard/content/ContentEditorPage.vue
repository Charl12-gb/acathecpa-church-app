<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">{{ isEditing ? 'Modifier le contenu' : 'Créer un contenu' }}</h1>
            <p class="text-muted mb-0">
              {{ isEditing ? 'Modifiez votre contenu' : 'Créez un nouvel article ou podcast' }}
            </p>
          </div>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-primary"
              @click="previewContent"
            >
              <i class="bi bi-eye me-2"></i>Aperçu
            </button>
            <button 
              class="btn btn-primary"
              @click="saveContent"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-check-circle me-2"></i>
              {{ contentForm.status === 'draft' ? 'Enregistrer' : 'Publier' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-8">
        <!-- Content Form -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Titre</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="contentForm.title"
                placeholder="Entrez le titre"
                required
              >
            </div>

            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea 
                class="form-control" 
                v-model="contentForm.description"
                rows="3"
                placeholder="Brève description du contenu"
                required
              ></textarea>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Type</label>
                <select class="form-select" v-model="contentForm.type" required>
                  <option value="article">Article</option>
                  <option value="podcast">Podcast</option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">Format</label>
                <select class="form-select" v-model="contentForm.format" required>
                  <option value="text">Texte</option>
                  <option value="audio">Audio</option>
                  <option value="video">Vidéo</option>
                  <option value="pdf">PDF</option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">Statut</label>
                <select class="form-select" v-model="contentForm.status">
                  <option value="draft">Brouillon</option>
                  <option value="published">Publié</option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">Tags</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="tagsInput"
                  placeholder="Séparez les tags par des virgules"
                  @keyup.enter="addTag"
                >
              </div>
            </div>

            <div v-if="contentForm.tags.length > 0" class="mb-3">
              <div class="d-flex flex-wrap gap-2">
                <span 
                  v-for="tag in contentForm.tags" 
                  :key="tag"
                  class="badge bg-primary"
                  style="cursor: pointer;"
                  @click="removeTag(tag)"
                >
                  {{ tag }}
                  <i class="bi bi-x ms-1"></i>
                </span>
              </div>
            </div>

            <div v-if="contentForm.format === 'text'" class="mb-3">
              <label class="form-label">Contenu</label>
              <ContentEditor v-model="contentForm.content" />
            </div>

            <div v-else-if="['audio', 'video', 'pdf'].includes(contentForm.format)" class="mb-3">
              <label class="form-label">URL du média</label>
              <input 
                type="url" 
                class="form-control" 
                v-model="contentForm.mediaUrl"
                placeholder="Entrez l'URL du média"
              >
            </div>

            <div class="form-check mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isPremium"
                v-model="contentForm.isPremium"
              >
              <label class="form-check-label" for="isPremium">
                Contenu premium
              </label>
            </div>

            <div v-if="contentForm.isPremium" class="mb-3">
              <label class="form-label">Prix (XOF)</label>
              <input 
                type="number" 
                class="form-control" 
                v-model="contentForm.price"
                min="0"
                step="0.01"
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 2rem;">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Aperçu</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <span 
                class="badge"
                :class="contentForm.type === 'article' ? 'bg-primary' : 'bg-success'"
              >
                {{ contentForm.type }}
              </span>
              <span 
                class="badge ms-2"
                :class="contentForm.status === 'published' ? 'bg-success' : 'bg-warning text-dark'"
              >
                {{ contentForm.status }}
              </span>
            </div>

            <h5 class="mb-3">{{ contentForm.title || 'Titre du contenu' }}</h5>
            <p class="text-muted">{{ contentForm.description || 'Description du contenu' }}</p>

            <div class="mb-3">
              <div class="d-flex gap-2 flex-wrap">
                <span 
                  v-for="tag in contentForm.tags" 
                  :key="tag"
                  class="badge bg-light text-dark"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <div v-if="contentForm.isPremium" class="alert alert-warning">
              <i class="bi bi-star-fill me-2"></i>
              Contenu premium
              <strong class="ms-2">{{ contentForm.price }}XOF</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useContentStore } from '../../../stores/content'
import ContentEditor from '../../../components/content/ContentEditor.vue'

const route = useRoute()
const router = useRouter()
const contentStore = useContentStore()

const isEditing = computed(() => !!route.params.id)
const loading = computed(() => contentStore.loading)

// Form data
const contentForm = ref({
  title: '',
  description: '',
  content: '',
  type: 'article',
  format: 'text',
  mediaUrl: '',
  isPremium: false,
  price: 0,
  status: 'draft',
  tags: [] as string[]
})

const tagsInput = ref('')

// Add tag
const addTag = () => {
  const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag)
  contentForm.value.tags = [...new Set([...contentForm.value.tags, ...tags])]
  tagsInput.value = ''
}

// Remove tag
const removeTag = (tag: string) => {
  contentForm.value.tags = contentForm.value.tags.filter(t => t !== tag)
}

// Load content if editing
onMounted(async () => {
  if (isEditing.value) {
    try {
      const content = await contentStore.getContent(parseInt(route.params.id as string))
      contentForm.value = {
        ...content,
        tags: content.tags || []
      }
    } catch (error) {
      console.error('Error loading content:', error)
    }
  }
})

// Preview content
const previewContent = () => {
  // Add preview logic here
  console.log('Preview content:', contentForm.value)
}

// Save content
const saveContent = async () => {
  try {
    const payload: any = {
        ...contentForm.value,
        content_body: contentForm.value.content
    };
    await contentStore.saveContent(payload)
    router.push('/my-content')
  } catch (error) {
    console.error('Error saving content:', error)
  }
}
</script>

<style scoped>
.badge {
  padding: 0.5rem 1rem;
}
</style>