<template>
  <div class="articles-page">

    <!-- ════════ HERO HEADER ════════ -->
    <section class="page-hero">
      <div class="hero-pattern"></div>
      <div class="hero-inner">
        <span class="hero-badge"><i class="bi bi-journal-richtext"></i> Blog</span>
        <h1 class="hero-title">Nos Articles</h1>
        <p class="hero-sub">Découvrez nos dernières publications, analyses et ressources pédagogiques.</p>

        <!-- Search bar inside hero -->
        <div class="hero-search">
          <i class="bi bi-search search-icon"></i>
          <input
            type="text"
            v-model="filters.search"
            placeholder="Rechercher un article…"
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
            <strong>{{ filteredArticles.length }}</strong> article{{ filteredArticles.length !== 1 ? 's' : '' }}
          </span>
        </div>
        <div class="toolbar-right">
          <div class="filter-group">
            <label class="filter-label">Tag</label>
            <select v-model="filters.tag" class="filter-select">
              <option value="">Tous</option>
              <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
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
        <p>Chargement des articles…</p>
      </div>

      <!-- ════════ ARTICLES GRID ════════ -->
      <div v-else-if="filteredArticles.length" class="articles-grid">
        <RouterLink
          v-for="article in filteredArticles"
          :key="article.id"
          :to="`/articles/${article.id}`"
          class="article-card"
        >
          <div class="card-thumb">
            <img
              :src="article.mediaUrl || 'https://placehold.co/600x340?text=Article'"
              :alt="article.title"
            />
            <span
              v-if="isPremium(article)"
              class="card-premium"
              :title="`Contenu premium · ${article.price} XOF`"
            >
              <i class="bi bi-star-fill"></i> Premium · {{ article.price }} XOF
            </span>
            <span class="card-format" :class="article.format">
              <i :class="article.format === 'video' ? 'bi bi-play-circle-fill' : 'bi bi-file-earmark-text-fill'"></i>
              {{ article.format === 'video' ? 'Vidéo' : 'Texte' }}
            </span>
          </div>
          <div class="card-body">
            <div class="card-meta">
              <span class="meta-date">
                <i class="bi bi-calendar3"></i>
                {{ new Date(article.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }) }}
              </span>
              <span v-if="article.author" class="meta-author">
                <i class="bi bi-person"></i> {{ article.author.name }}
              </span>
            </div>
            <h3 class="card-title">{{ article.title }}</h3>
            <p class="card-desc">{{ article.description }}</p>
            <div class="card-tags" v-if="article.tags?.length">
              <span v-for="tag in article.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <span class="card-link">
              Lire l'article <i class="bi bi-arrow-right"></i>
            </span>
          </div>
        </RouterLink>
      </div>

      <!-- ════════ EMPTY STATE ════════ -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <i class="bi bi-journal-x"></i>
        </div>
        <h3>Aucun article trouvé</h3>
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

const articles = ref<Content[]>([])
const loading = ref(false)
const error = ref('')

// L'API DRF renvoie `is_premium` (snake_case) tandis que le type front utilise `isPremium`
const isPremium = (item: Content): boolean =>
  Boolean(item.isPremium || (item as unknown as Record<string, unknown>).is_premium)

const filters = ref({
  search: '',
  tag: '',
  sort: 'recent'
})

const tags = ['Development', 'Business', 'Marketing', 'Design', 'Technology']

const loadArticles = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await contentStore.getContents('article')
    articles.value = data
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const filteredArticles = computed(() => {
  let filtered = [...articles.value]
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(a =>
      a.title.toLowerCase().includes(search) ||
      a.description.toLowerCase().includes(search)
    )
  }
  if (filters.value.tag) {
    filtered = filtered.filter(a => a.tags.includes(filters.value.tag))
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
  filters.value = { search: '', tag: '', sort: 'recent' }
}

onMounted(() => { loadArticles() })
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

.articles-page {
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
  &:focus { border-color: $secondary; }
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
  border-top-color: $secondary;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ═══════ ARTICLES GRID ═══════ */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}
.article-card {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  transition: transform .25s, box-shadow .25s;
  &:hover {
    transform: translateY(-5px);
    box-shadow: $shadow-lg;
    .card-link i { transform: translateX(4px); }
    .card-thumb img { transform: scale(1.04); }
  }
}
.card-thumb {
  position: relative;
  height: 200px;
  overflow: hidden;
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform .4s;
  }
}
.card-format {
  position: absolute;
  top: 14px;
  right: 14px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
  backdrop-filter: blur(6px);
  color: #fff;
  background: rgba($secondary, .85);
  &.video { background: rgba($primary, .85); }
}
.card-premium {
  position: absolute;
  top: 50px;
  right: 14px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: .72rem;
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
  flex: 1;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
  font-size: .78rem;
  color: $text-light;
  i { font-size: .72rem; margin-right: 4px; }
}
.card-title {
  font-size: 1.08rem;
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
  font-size: .88rem;
  color: $text-light;
  line-height: 1.6;
  margin: 0 0 14px;
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
  margin-bottom: 16px;
}
.tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  background: rgba($secondary, .08);
  color: $secondary;
}
.card-link {
  font-size: .85rem;
  font-weight: 700;
  color: $primary;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  i { transition: transform .25s; font-size: .78rem; }
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
  background: $secondary;
  color: #fff;
  font-weight: 600;
  font-size: .9rem;
  cursor: pointer;
  transition: .2s;
  &:hover { background: color.adjust($secondary, $lightness: -8%); transform: translateY(-1px); }
}

/* ═══════ RESPONSIVE ═══════ */
@media (max-width: 992px) {
  .articles-grid { grid-template-columns: repeat(2, 1fr); gap: 20px; }
}
@media (max-width: 640px) {
  .page-hero { padding: 90px 18px 42px; }
  .hero-title { font-size: 1.8rem; }
  .articles-grid { grid-template-columns: 1fr; gap: 18px; }
  .toolbar { flex-direction: column; align-items: flex-start; }
  .toolbar-right { width: 100%; }
  .filter-group { flex: 1; }
  .filter-select { width: 100%; }
}
</style>