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

        <template v-else-if="podcast">
            <!-- Podcast Header -->
            <div class="row mb-4">
                <div class="col-lg-8 mx-auto">
                    <nav aria-label="breadcrumb" class="mb-4">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <RouterLink to="/podcasts">Podcasts</RouterLink>
                            </li>
                            <li class="breadcrumb-item active" aria-current="page">
                                {{ podcast.title }}
                            </li>
                        </ol>
                    </nav>

                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-4 mb-md-0">
                                    <img :src="podcast.mediaUrl || 'https://placehold.co/400x400?text=Podcast'"
                                        class="img-fluid rounded" :alt="podcast.title">
                                </div>
                                <div class="col-md-8">
                                    <h1 class="mb-3">{{ podcast.title }}</h1>

                                    <div class="d-flex flex-wrap gap-3 mb-3">
                                        <span class="badge"
                                            :class="podcast.format === 'audio' ? 'bg-success' : 'bg-danger'">
                                            {{ podcast.format }}
                                        </span>
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-calendar me-2"></i>
                                            <span>{{ new Date(podcast.created_at).toLocaleDateString() }}</span>
                                        </div>
                                    </div>

                                    <div class="d-flex align-items-center mb-4">
                                        <div class="rounded-circle bg-light p-2 me-2">
                                            <i class="bi bi-person-circle text-primary"></i>
                                        </div>
                                        <span>{{ podcast.author.name }}</span>
                                    </div>

                                    <p class="lead mb-4">{{ podcast.description }}</p>

                                    <div class="d-flex flex-wrap gap-2 mb-4">
                                        <span v-for="tag in podcast.tags" :key="tag" class="badge bg-light text-dark">
                                            {{ tag }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Podcast Content -->
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card border-0 shadow-sm mb-4">
                        <div class="card-body">
                            <!-- Audio Player -->
                            <div v-if="podcast.format === 'audio'" class="audio-player mb-4">
                                <audio controls class="w-100">
                                    <source :src="podcast.mediaUrl" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                            </div>

                            <!-- Video Player -->
                            <div v-else-if="podcast.format === 'video'" class="ratio ratio-16x9 mb-4">
                                <iframe :src="podcast.mediaUrl" allowfullscreen
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
                            </div>

                            <!-- Text Content -->
                            <div v-if="podcast.content" class="podcast-content" v-html="podcast.content"></div>
                        </div>
                    </div>

                    <!-- Premium Content Notice -->
                    <div v-if="podcast.isPremium" class="alert alert-warning">
                        <i class="bi bi-star-fill me-2"></i>
                        Contenu premium
                        <strong class="ms-2">{{ podcast.price }}XOF</strong>
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

const podcast = ref<Content | null>(null)
const loading = ref(true)
const error = ref('')

const loadPodcast = async () => {
    loading.value = true
    error.value = ''

    try {
        const podcastId = parseInt(route.params.id as string)
        //   const data = await contentStore.getContent(podcastId)
        //   podcast.value = data
        podcast.value = {
            "id": 1,
            "title": "Titre du podcast",
            "description": "Description du podcast",
            "created_at": "2025-04-26T10:00:00Z",
            "format": "audio",
            "mediaUrl": "https://example.com/media/podcast.mp3",
            "author": {
                "id": 1,
                "name": "Auteur du podcast"
            },
            "tags": ["théologie", "mission", "éducation"],
            "content": "<p>Contenu HTML riche du podcast...</p>",
            "isPremium": true,
            "price": 9.99
        }
    } catch (err: any) {
        error.value = err.message || 'Failed to load podcast'
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadPodcast()
})
</script>

<style scoped>
.badge {
    padding: 0.5rem 1rem;
}

.audio-player {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
}

.podcast-content {
    font-size: 1.1rem;
    line-height: 1.8;
}

.podcast-content :deep(h2),
.podcast-content :deep(h3) {
    margin: 2rem 0 1rem;
}

.podcast-content :deep(p) {
    margin-bottom: 1.5rem;
}
</style>