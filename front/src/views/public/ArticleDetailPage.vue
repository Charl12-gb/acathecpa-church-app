<template>
    <div class="container py-5">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
  
      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
  
      <template v-else-if="article">
        <!-- Article Header -->
        <div class="row mb-4">
          <div class="col-lg-8 mx-auto">
            <nav aria-label="breadcrumb" class="mb-4">
              <ol class="breadcrumb">
                <li class="breadcrumb-item">
                  <RouterLink to="/articles">Articles</RouterLink>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                  {{ article.title }}
                </li>
              </ol>
            </nav>
  
            <h1 class="mb-3">{{ article.title }}</h1>
            
            <div class="d-flex flex-wrap gap-3 mb-4">
              <span class="badge bg-primary">{{ article.format }}</span>
              <div class="d-flex align-items-center">
                <i class="bi bi-calendar me-2"></i>
                <span>{{ new Date(article.created_at).toLocaleDateString() }}</span>
              </div>
              <div class="d-flex align-items-center" v-if="article.author">
                <i class="bi bi-person-circle me-2"></i>
                <span>{{ article.author.name }}</span>
              </div>
            </div>
  
            <div class="mb-4">
              <img 
                v-if="article.mediaUrl || (article as any).media_url"
                :src="article.mediaUrl || (article as any).media_url"
                :alt="article.title"
                class="img-fluid rounded"
              >
            </div>
          </div>
        </div>
  
        <!-- Article Content -->
        <div class="row">
          <div class="col-lg-8 mx-auto">
            <div class="card border-0 shadow-sm mb-4">
              <div class="card-body">
                <!-- Text Content -->
                <div v-if="article.format === 'text'" v-html="article.content || (article as any).content_body" class="article-content"></div>
  
                <!-- PDF Viewer -->
                <div v-else-if="article.format === 'pdf'" class="ratio ratio-16x9">
                  <iframe :src="article.mediaUrl || (article as any).media_url" allowfullscreen></iframe>
                </div>
  
                <!-- Video Player -->
                <div v-else-if="article.format === 'video'" class="ratio ratio-16x9">
                  <iframe 
                    :src="article.mediaUrl || (article as any).media_url"
                    allowfullscreen
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  ></iframe>
                </div>
  
                <!-- Audio Player -->
                <div v-else-if="article.format === 'audio'" class="audio-player">
                  <audio controls class="w-100">
                    <source :src="article.mediaUrl || (article as any).media_url" type="audio/mpeg">
                    Your browser does not support the audio element.
                  </audio>
                </div>
              </div>
            </div>
  
            <!-- Tags -->
            <div class="mb-4">
              <h5 class="mb-3">Tags</h5>
              <div class="d-flex flex-wrap gap-2">
                <span 
                  v-for="tag in article.tags" 
                  :key="tag"
                  class="badge bg-light text-dark"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
  
            <!-- Premium Content Notice -->
            <div v-if="article.isPremium || (article as any).is_premium" class="alert alert-warning">
              <i class="bi bi-star-fill me-2"></i>
              Contenu premium
              <strong class="ms-2">{{ article.price }}XOF</strong>
            </div>
          </div>
        </div>
      </template>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { useContentStore } from '../../stores/content'
  import type { Content } from '../../stores/content'
  
  const route = useRoute()
  const contentStore = useContentStore()
  
  const article = ref<Content | null>(null)
  const loading = ref(true)
  const error = ref('')
  
  const loadArticle = async () => {
    loading.value = true
    error.value = ''
    
    try {
      const articleId = parseInt(route.params.id as string)
      const data = await contentStore.getContent(articleId)
      article.value = data
    } catch (err: any) {
      error.value = err.message || 'Failed to load article'
    } finally {
      loading.value = false
    }
  }
  
  onMounted(() => {
    loadArticle()
  })
  </script>
  
  <style scoped>
  .article-content {
    font-size: 1.1rem;
    line-height: 1.8;
  }
  
  .article-content :deep(img) {
    max-width: 100%;
    height: auto;
    margin: 1rem 0;
  }
  
  .article-content :deep(h2),
  .article-content :deep(h3) {
    margin: 2rem 0 1rem;
  }
  
  .article-content :deep(blockquote) {
    border-left: 4px solid var(--bs-primary);
    padding-left: 1rem;
    margin: 1.5rem 0;
    font-style: italic;
  }
  
  .badge {
    padding: 0.5rem 1rem;
  }
  
  .audio-player {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
  }
  </style>