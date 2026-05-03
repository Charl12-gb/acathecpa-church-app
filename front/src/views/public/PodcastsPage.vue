<template>
  <div class="podcasts-page">

    <!-- ════════ HERO HEADER ════════ -->
    <section class="page-hero">
      <div class="hero-pattern"></div>
      <div class="hero-inner">
        <span class="hero-badge"><i class="bi bi-mic-fill"></i> Audio & Vidéo</span>
        <h1 class="hero-title">Nos Podcasts</h1>
        <p class="hero-sub">Écoutez nos podcasts éducatifs, discussions et enseignements théologiques.</p>

        <div class="hero-search">
          <i class="bi bi-search search-icon"></i>
          <input
            type="text"
            v-model="filters.search"
            placeholder="Rechercher un podcast…"
            class="search-input"
          />
          <span v-if="filters.search" class="search-clear" @click="filters.search = ''">
            <i class="bi bi-x-lg"></i>
          </span>
        </div>
      </div>
    </section>

    <!-- ════════ TOOLBAR ════════ -->
    <div class="container">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="result-count">
            <strong>{{ filteredPodcasts.length }}</strong> podcast{{ filteredPodcasts.length !== 1 ? 's' : '' }}
          </span>
        </div>
        <div class="toolbar-right">
          <div class="filter-group">
            <label class="filter-label">Format</label>
            <select v-model="filters.format" class="filter-select">
              <option value="">Tous</option>
              <option value="audio">Audio</option>
              <option value="video">Vidéo</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Trier par</label>
            <select v-model="filters.sort" class="filter-select">
              <option value="recent">Plus récents</option>
              <option value="popular">Plus populaires</option>
            </select>
          </div>
        </div>
      </div>

      <!-- ════════ LOADING ════════ -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Chargement des podcasts…</p>
      </div>

      <!-- ════════ PODCASTS GRID ════════ -->
      <div v-else-if="filteredPodcasts.length" class="podcasts-grid">
        <RouterLink
          v-for="podcast in filteredPodcasts"
          :key="podcast.id"
          :to="`/podcasts/${podcast.id}`"
          class="podcast-card"
        >
          <!-- Thumbnail -->
          <div class="card-thumb">
            <img
              :src="podcast.mediaUrl || 'https://placehold.co/400x400?text=Podcast'"
              :alt="podcast.title"
            />
            <div class="play-overlay">
              <i class="bi" :class="podcast.format === 'video' ? 'bi-play-circle-fill' : 'bi-headphones'"></i>
            </div>
            <span
              v-if="isPremium(podcast)"
              class="card-premium"
              :title="`Contenu premium · ${podcast.price} XOF`"
            >
              <i class="bi bi-star-fill"></i> Premium · {{ podcast.price }} XOF
            </span>
            <span class="card-format" :class="podcast.format">
              <i :class="podcast.format === 'audio' ? 'bi bi-soundwave' : 'bi bi-camera-video-fill'"></i>
              {{ podcast.format === 'audio' ? 'Audio' : 'Vidéo' }}
            </span>
          </div>
          <!-- Body -->
          <div class="card-body">
            <div class="card-meta">
              <span class="meta-date">
                <i class="bi bi-calendar3"></i>
                {{ new Date(podcast.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }) }}
              </span>
              <span v-if="podcast.author" class="meta-author">
                <i class="bi bi-person"></i> {{ podcast.author.name }}
              </span>
            </div>
            <h3 class="card-title">{{ podcast.title }}</h3>
            <p class="card-desc">{{ podcast.description }}</p>
            <div class="card-tags" v-if="podcast.tags?.length">
              <span v-for="tag in podcast.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <span class="card-link">
              <i class="bi bi-play-fill"></i> Écouter maintenant
            </span>
          </div>
        </RouterLink>
      </div>

      <!-- ════════ EMPTY STATE ════════ -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="bi bi-mic-mute"></i>
        </div>
        <h3>Aucun podcast trouvé</h3>
        <p>Essayez de modifier vos critères de recherche</p>
        <button class="btn-reset" @click="resetFilters">
          <i class="bi bi-arrow-counterclockwise"></i> Réinitialiser les filtres
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useContentStore } from '../../stores/content'
import type { Content } from '../../stores/content'

const contentStore = useContentStore()

const podcasts = ref<Content[]>([])
const loading = ref(false)
const error = ref('')

// L'API DRF renvoie `is_premium` (snake_case) tandis que le type front utilise `isPremium`
const isPremium = (item: Content): boolean =>
  Boolean(item.isPremium || (item as unknown as Record<string, unknown>).is_premium)

const filters = ref({
  search: '',
  format: '',
  sort: 'recent'
})

const loadPodcasts = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await contentStore.getContents('podcast')
    podcasts.value = data
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const filteredPodcasts = computed(() => {
  let filtered = [...podcasts.value]
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(p =>
      p.title.toLowerCase().includes(search) ||
      p.description.toLowerCase().includes(search)
    )
  }
  if (filters.value.format) {
    filtered = filtered.filter(p => p.format === filters.value.format)
  }
  if (filters.value.sort === 'popular') {
    filtered.sort((a, b) => b.id - a.id)
  } else {
    filtered.sort((a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }
  return filtered
})

const resetFilters = () => {
  filters.value = { search: '', format: '', sort: 'recent' }
}

onMounted(() => { loadPodcasts() })
</script>

<style scoped lang="scss">
@use "sass:color";

$primary:    #C14428;
$secondary:  #1B7A78;
$accent:     #F4A300;
$success:    #27664B;
$neutral:    #FFF8EE;
$dark:       #1a1a1a;
$text:       #2C2C2C;
$text-light: #5a6474;
$border:     #e7e0d4;
$radius:     12px;
$radius-lg:  18px;
$shadow-sm:  0 2px 8px rgba(0,0,0,.05);
$shadow:     0 4px 20px rgba(0,0,0,.07);
$shadow-lg:  0 8px 40px rgba(0,0,0,.10);

.podcasts-page {
  min-height: 100vh;
  background: $neutral;
}

/* ═══════ HERO ═══════ */
.page-hero {
  position: relative;
  background: linear-gradient(160deg, $success 0%, color.adjust($secondary, $lightness: -10%) 100%);
  padding: 110px 24px 60px;
  text-align: center;
  overflow: hidden;
}
.hero-pattern {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E");
  z-index: 0;
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(#fff, .14);
  color: #fff;
  font-size: .78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: 18px;
  backdrop-filter: blur(4px);
}
.hero-title {
  font-size: 2.6rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px;
  line-height: 1.15;
}
.hero-sub {
  font-size: 1.05rem;
  color: rgba(#fff, .82);
  margin: 0 0 32px;
  line-height: 1.6;
}
.hero-search {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
}
.search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: $text-light;
  font-size: 1rem;
}
.search-input {
  width: 100%;
  padding: 14px 48px 14px 48px;
  border-radius: 50px;
  border: none;
  background: #fff;
  font-size: .95rem;
  color: $text;
  box-shadow: $shadow-lg;
  outline: none;
  transition: box-shadow .2s;
  &::placeholder { color: #b0a898; }
  &:focus { box-shadow: 0 8px 40px rgba(0,0,0,.15), 0 0 0 3px rgba($accent, .25); }
}
.search-clear {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  cursor: pointer;
  color: $text-light;
  transition: .2s;
  &:hover { background: rgba(0,0,0,.06); color: $dark; }
}

/* ═══════ TOOLBAR ═══════ */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 60px;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  padding: 20px 0 24px;
  border-bottom: 1px solid $border;
  margin-bottom: 32px;
}
.result-count {
  font-size: .92rem;
  color: $text-light;
  strong { color: $dark; font-weight: 700; }
}
.toolbar-right {
  display: flex;
  gap: 12px;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-label {
  font-size: .78rem;
  font-weight: 600;
  color: $text-light;
  white-space: nowrap;
}
.filter-select {
  padding: 8px 32px 8px 12px;
  border-radius: 8px;
  border: 1px solid $border;
  background: #fff;
  font-size: .85rem;
  color: $text;
  cursor: pointer;
  outline: none;
  appearance: auto;
  transition: border-color .2s;
  &:focus { border-color: $primary; }
}

/* ═══════ LOADING ═══════ */
.loading-state {
  text-align: center;
  padding: 80px 0;
  color: $text-light;
  p { margin-top: 16px; font-size: .95rem; }
}
.spinner {
  width: 36px; height: 36px;
  border: 3px solid $border;
  border-top-color: $primary;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ═══════ PODCASTS GRID ═══════ */
.podcasts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px;
}
.podcast-card {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  display: grid;
  grid-template-columns: 200px 1fr;
  transition: transform .25s, box-shadow .25s;
  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
    .play-overlay { opacity: 1; }
    .card-link i { transform: translateX(3px); }
    .card-thumb img { transform: scale(1.06); }
  }
}
.card-thumb {
  position: relative;
  overflow: hidden;
  min-height: 220px;
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform .4s;
  }
}
.play-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba($dark, .35);
  opacity: 0;
  transition: opacity .3s;
  i {
    font-size: 2.8rem;
    color: #fff;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,.3));
  }
}
.card-format {
  position: absolute;
  top: 12px;
  right: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  border-radius: 20px;
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
  backdrop-filter: blur(6px);
  color: #fff;
  &.audio { background: rgba($success, .85); }
  &.video { background: rgba($primary, .85); }
}
.card-premium {
  position: absolute;
  top: 46px;
  right: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  border-radius: 20px;
  font-size: .7rem;
  font-weight: 800;
  letter-spacing: .03em;
  color: $dark;
  background: linear-gradient(135deg, #FFD86B 0%, $accent 100%);
  box-shadow: 0 4px 14px rgba($accent, .5);
  i { color: $primary; }
}
.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
  font-size: .76rem;
  color: $text-light;
  i { font-size: .7rem; margin-right: 3px; }
}
.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 8px;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-desc {
  font-size: .86rem;
  color: $text-light;
  line-height: 1.6;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}
.tag {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: .7rem;
  font-weight: 600;
  background: rgba($primary, .08);
  color: $primary;
}
.card-link {
  font-size: .84rem;
  font-weight: 700;
  color: $accent;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  i { transition: transform .25s; font-size: 1rem; }
}

/* ═══════ EMPTY STATE ═══════ */
.empty-state {
  text-align: center;
  padding: 80px 24px;
}
.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba($primary, .08);
  display: grid;
  place-items: center;
  margin: 0 auto 20px;
  i { font-size: 2rem; color: $primary; }
}
.empty-state h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 8px;
}
.empty-state p {
  font-size: .95rem;
  color: $text-light;
  margin: 0 0 24px;
}
.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 10px;
  border: none;
  background: $primary;
  color: #fff;
  font-weight: 600;
  font-size: .9rem;
  cursor: pointer;
  transition: .2s;
  &:hover { background: color.adjust($primary, $lightness: -8%); transform: translateY(-1px); }
}

/* ═══════ RESPONSIVE ═══════ */
@media (max-width: 992px) {
  .podcasts-grid { grid-template-columns: 1fr; gap: 20px; }
  .podcast-card { grid-template-columns: 180px 1fr; }
}
@media (max-width: 640px) {
  .page-hero { padding: 90px 18px 42px; }
  .hero-title { font-size: 1.8rem; }
  .podcast-card { grid-template-columns: 1fr; }
  .card-thumb { min-height: 180px; }
  .toolbar { flex-direction: column; align-items: flex-start; }
  .toolbar-right { width: 100%; }
  .filter-group { flex: 1; }
  .filter-select { width: 100%; }
}
</style>