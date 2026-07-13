<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getAlumni } from '../../services/api/alumni'
import type { Alumnus } from '../../types/api'

const alumni = ref<Alumnus[]>([])
const isLoading = ref(true)
const search = ref('')

const initials = (name: string) =>
  (name || '').split(' ').filter(Boolean).slice(0, 2).map(w => w[0]?.toUpperCase()).join('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return alumni.value
  return alumni.value.filter(a =>
    (a.name || '').toLowerCase().includes(q) ||
    (a.country || '').toLowerCase().includes(q) ||
    a.formations.some(f => f.toLowerCase().includes(q))
  )
})

onMounted(async () => {
  try {
    alumni.value = await getAlumni()
  } catch {
    alumni.value = []
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="alumni-page">
    <!-- Hero -->
    <section class="alumni-hero">
      <div class="container">
        <span class="hero-badge"><i class="bi bi-mortarboard-fill"></i> Communauté</span>
        <h1 class="hero-title">Nos Alumni</h1>
        <p class="hero-subtitle">
          Découvrez les étudiants diplômés et certifiés qui ont suivi leur formation à ACATHECPA.
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <!-- Search -->
        <div class="alumni-search">
          <i class="bi bi-search"></i>
          <input v-model="search" type="text" placeholder="Rechercher par nom, pays ou formation…">
        </div>

        <!-- Loading -->
        <div v-if="isLoading" class="state-msg">
          <div class="spinner-border spinner-border-sm me-2"></div> Chargement…
        </div>

        <!-- Grid -->
        <div v-else-if="filtered.length" class="alumni-grid">
          <div v-for="a in filtered" :key="a.id" class="alumni-card">
            <div class="alumni-avatar">{{ initials(a.name) }}</div>
            <h5 class="alumni-name">{{ a.name }}</h5>
            <p v-if="a.country" class="alumni-country">
              <i class="bi bi-geo-alt-fill"></i> {{ a.country }}
            </p>
            <span class="alumni-badge">
              <i class="bi bi-award-fill"></i>
              {{ a.certificates_count }} certification{{ a.certificates_count > 1 ? 's' : '' }}
            </span>
            <div v-if="a.formations.length" class="alumni-formations">
              <span v-for="(f, i) in a.formations.slice(0, 3)" :key="i" class="formation-tag">{{ f }}</span>
              <span v-if="a.formations.length > 3" class="formation-more">+{{ a.formations.length - 3 }}</span>
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else class="state-msg empty">
          <i class="bi bi-people"></i>
          <p>{{ search ? 'Aucun alumni ne correspond à votre recherche.' : 'Aucun alumni à afficher pour le moment.' }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
$primary: #C14428;
$secondary: #1B7A78;
$accent: #F4A300;
$dark: #1a1a1a;
$text-light: #5a6474;
$border: #e7e0d4;

.container { max-width: 1180px; margin: 0 auto; padding: 0 24px; }
.section { padding: 48px 0 64px; }

.alumni-hero {
  background: linear-gradient(160deg, rgba($secondary, .92) 0%, rgba($dark, .85) 100%);
  color: #fff;
  padding: 64px 0 56px;
  text-align: center;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 16px; border-radius: 24px; background: rgba(#fff, .15);
  font-size: .8rem; font-weight: 600; margin-bottom: 16px;
}
.hero-title { font-size: 2.6rem; font-weight: 800; margin: 0 0 12px; }
.hero-subtitle { font-size: 1.05rem; color: rgba(#fff, .85); max-width: 620px; margin: 0 auto; line-height: 1.6; }

.alumni-search {
  display: flex; align-items: center; gap: 10px;
  max-width: 480px; margin: 0 auto 40px;
  background: #fff; border: 1px solid $border; border-radius: 30px;
  padding: 10px 20px; box-shadow: 0 2px 12px rgba(0,0,0,.05);
  i { color: $text-light; }
  input { flex: 1; border: none; outline: none; font-size: .95rem; background: transparent; }
}

.alumni-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.alumni-card {
  background: #fff; border: 1px solid $border; border-radius: 16px;
  padding: 28px 22px; text-align: center;
  transition: transform .25s, box-shadow .25s, border-color .25s;
  &:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,.08); border-color: rgba($secondary, .3); }
}
.alumni-avatar {
  width: 72px; height: 72px; border-radius: 50%; margin: 0 auto 14px;
  display: grid; place-items: center;
  background: rgba($secondary, .1); color: $secondary;
  font-size: 1.5rem; font-weight: 700;
}
.alumni-name { font-size: 1.05rem; font-weight: 700; color: $dark; margin: 0 0 4px; }
.alumni-country {
  font-size: .82rem; color: $text-light; margin: 0 0 12px;
  i { color: $primary; }
}
.alumni-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: 20px;
  background: rgba($accent, .15); color: darken($accent, 20%);
  font-size: .8rem; font-weight: 700;
}
.alumni-formations {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 14px;
}
.formation-tag {
  font-size: .7rem; padding: 3px 9px; border-radius: 12px;
  background: rgba($secondary, .08); color: $secondary; font-weight: 600;
}
.formation-more { font-size: .7rem; padding: 3px 9px; color: $text-light; }

.state-msg {
  text-align: center; padding: 60px 0; color: $text-light;
  &.empty i { font-size: 2.6rem; display: block; margin-bottom: 12px; opacity: .4; }
  p { margin: 0; }
}

@media (max-width: 640px) {
  .hero-title { font-size: 2rem; }
  .alumni-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
}
</style>
