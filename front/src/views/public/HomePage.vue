<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink } from 'vue-router'
import { getAllCourses } from '../../services/api/course'
import { useAuthStore } from '../../stores/auth'
import type { Course } from '../../types/api'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const featuredCourses = ref<Course[]>([])
const activeVM = ref<'vision' | 'mission'>('vision')
let vmInterval: ReturnType<typeof setInterval> | null = null

const partners = ref([
  { name: 'Université de Paris', logo: 'https://placehold.co/200x100?text=Université+de+Paris' },
  { name: 'Microsoft', logo: 'https://placehold.co/200x100?text=Microsoft' },
  { name: 'IBM', logo: 'https://placehold.co/200x100?text=IBM' },
  { name: 'Orange', logo: 'https://placehold.co/200x100?text=Orange' },
])

const testimonials = ref([
  {
    name: 'Sophie M.',
    position: 'Étudiante diplômée',
    content: 'La formation que j\'ai suivie à ACATHECPA m\'a permis de trouver rapidement un emploi dans mon domaine. Les professeurs sont excellents et le contenu très pratique.',
    avatar: 'https://placehold.co/100x100?text=SM'
  },
  {
    name: 'Thomas D.',
    position: 'Professionnel en reconversion',
    content: 'J\'ai changé de carrière grâce à ACATHECPA. La qualité des cours et le suivi personnalisé m\'ont donné confiance pour me lancer dans ce nouveau domaine.',
    avatar: 'https://placehold.co/100x100?text=TD'
  },
])

const priorities = ref([
  { icon: 'bi-book-fill', title: 'Excellence Pracadémique', text: 'Offrir des programmes de formation de pointe, pertinents au contexte, en Théologie et Missiologie, qui favorisent la rigueur académique et la pensée innovante.' },
  { icon: 'bi-search', title: 'Recherche et Innovation', text: 'Promouvoir la recherche et l\'innovation en Théologie et Missiologie en lien avec les besoins du contexte, pour informer et enrichir nos programmes de formation.' },
  { icon: 'bi-globe', title: 'Contextualisation Critique', text: 'Favoriser une approche contextualisée qui prend en compte les réalités socioculturelles, religieuses et pratiques des communautés.' },
])

const values = ref([
  { icon: 'bi-shield-check', title: 'Éthique', text: 'Agir de manière intègre dans toutes nos activités et promouvoir une culture de la transparence.' },
  { icon: 'bi-check-circle', title: 'Redevabilité', text: 'Assumer la responsabilité de nos décisions et actions avec rigueur.' },
  { icon: 'bi-people', title: 'Inclusion', text: 'Respecter la diversité des personnes, des cultures et des perspectives.' },
  { icon: 'bi-graph-up-arrow', title: 'Croissance', text: 'Favoriser le développement personnel et professionnel de chacun.' },
  { icon: 'bi-heart', title: 'Compassion', text: 'Apporter réconfort et soutien aux personnes et aux communautés.' },
  { icon: 'bi-star', title: 'Foi', text: 'Agir avec une perspective spirituelle pour renforcer notre identité et mission.' },
  { icon: 'bi-houses', title: 'Communauté', text: 'Développer des solutions qui contribuent au développement communautaire.' },
])

onMounted(async () => {
  const TypeIt = (window as any).TypeIt
  if (TypeIt) {
    new TypeIt('#typeit-text', {
      speed: 100,
      loop: true,
      deleteSpeed: 50,
      waitUntilVisible: true,
    })
      .type('Bienvenue à ACATHECPA')
      .pause(3500)
      .delete()
      .type('Welcome to ACATHECPA')
      .pause(3500)
      .delete()
      .type('Bienvenido a ACATHECPA')
      .pause(3500)
      .delete()
      .go()
  }

  try {
    const courses = await getAllCourses({ limit: 3, sortBy: 'created_at', sortOrder: 'desc' })
    featuredCourses.value = courses
  } catch {
    featuredCourses.value = []
  }

  vmInterval = setInterval(() => {
    activeVM.value = activeVM.value === 'vision' ? 'mission' : 'vision'
  }, 6000)
})

onBeforeUnmount(() => {
  if (vmInterval) clearInterval(vmInterval)
})
</script>

<template>
  <div class="home-page">

    <!-- ════════ HERO ════════ -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-overlay"></div>

      <!-- Animated floating icons & branding -->
      <div class="hero-particles" aria-hidden="true">
        <i class="particle p-icon p1 bi bi-mortarboard-fill"></i>
        <i class="particle p-icon p2 bi bi-book-fill"></i>
        <i class="particle p-icon p3 bi bi-building"></i>
        <i class="particle p-icon p4 bi bi-journal-bookmark-fill"></i>
        <i class="particle p-icon p5 bi bi-bank2"></i>
        <i class="particle p-icon p6 bi bi-pen-fill"></i>
        <i class="particle p-icon p7 bi bi-globe-americas"></i>
        <i class="particle p-icon p8 bi bi-building-fill"></i>
        <i class="particle p-icon p9 bi bi-trophy-fill"></i>
        <i class="particle p-icon p10 bi bi-easel-fill"></i>
        <span class="particle p-brand p11">ACATHECPA</span>
        <span class="particle p-brand p12">ACATHECPA</span>
      </div>

      <div class="hero-content">
        <div class="hero-badge">
          <i class="bi bi-mortarboard-fill"></i>
          Formation Théologico-Missionnaire
        </div>
        <h1 class="hero-title">
          <span id="typeit-text"></span>
        </h1>
        <p class="hero-subtitle">
          Académie de Formation Théologico-Missionnaire Innovante — Conjuguant approche
          multidisciplinaire et ancrage contextuel Africain pour une formation pertinente.
        </p>
        <div class="hero-actions">
          <template v-if="isAuthenticated">
            <RouterLink to="/dashboard" class="btn-hero-primary">
              <i class="bi bi-grid-1x2-fill"></i> Tableau de bord
            </RouterLink>
            <RouterLink to="/browse-courses" class="btn-hero-outline">
              <i class="bi bi-play-circle"></i> Voir les formations
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/login" class="btn-hero-primary">
              <i class="bi bi-box-arrow-in-right"></i> Se connecter
            </RouterLink>
            <RouterLink to="/register" class="btn-hero-outline">
              <i class="bi bi-person-plus"></i> S'inscrire
            </RouterLink>
          </template>
        </div>
      </div>
      <!-- Stats flottants -->
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-number">500+</span>
          <span class="stat-label">Étudiants formés</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">50+</span>
          <span class="stat-label">Cours disponibles</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">20+</span>
          <span class="stat-label">Professeurs experts</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">15+</span>
          <span class="stat-label">Pays représentés</span>
        </div>
      </div>

      <!-- Valeurs défilantes -->
      <div class="values-ticker" aria-hidden="true">
        <div class="ticker-track">
          <div v-for="n in 2" :key="n" class="ticker-set">
            <span v-for="(v, i) in values" :key="`${n}-${i}`" class="ticker-item">
              <i :class="'bi ' + v.icon"></i> {{ v.title }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════ À PROPOS ════════ -->
    <section class="section about-section">
      <div class="container">
        <div class="about-grid">
          <div class="about-visual">
            <div class="about-img-wrap">
              <img src="../../assets/logo.png" alt="ACATHECPA" class="about-img" />
            </div>
            <div class="about-accent-dot"></div>

            <!-- Vision / Mission toggle -->
            <div class="vm-toggle">
              <div class="vm-tabs">
                <button
                  class="vm-tab"
                  :class="{ active: activeVM === 'vision' }"
                  @click="activeVM = 'vision'"
                >
                  <i class="bi bi-eye-fill"></i> Vision
                </button>
                <button
                  class="vm-tab"
                  :class="{ active: activeVM === 'mission' }"
                  @click="activeVM = 'mission'"
                >
                  <i class="bi bi-compass-fill"></i> Mission
                </button>
              </div>
              <Transition name="vm-fade" mode="out-in">
                <p v-if="activeVM === 'vision'" key="vision" class="vm-text">
                  Devenir un centre d'excellence en formation et en recherche, intégrant Théologie et
                  Missiologie Intégrée au Contexte pour former des leaders visionnaires, transformatifs
                  et dévoués au service des communautés locales et au développement durable de l'Afrique.
                </p>
                <p v-else key="mission" class="vm-text">
                  Développer et mettre en œuvre des programmes de formations et de recherches pour les
                  vocations ecclésiastiques et les ministères laïcs, afin de les équiper de connaissances
                  approfondies en théologie et missiologie contextualisées, de les habiliter à exercer un
                  leadership transformateur et servant.
                </p>
              </Transition>
            </div>
          </div>
          <div class="about-text">
            <span class="section-badge">À propos</span>
            <h2 class="section-title">Une académie au service de l'Afrique</h2>
            <p class="about-desc">
              ACATHECPA est une Académie de Formation Théologico-Missionnaire Innovante, qui conjugue
              approche multidisciplinaire et ancrage contextuel Africain pour une formation pertinente.
              Notre engagement est de préparer les leaders de demain avec des outils théologiques et
              missiologiques adaptés aux réalités du continent.
            </p>
            <div class="about-highlights">
              <div class="highlight-item">
                <i class="bi bi-check-circle-fill"></i>
                <span>Programmes contextualisés</span>
              </div>
              <div class="highlight-item">
                <i class="bi bi-check-circle-fill"></i>
                <span>Professeurs expérimentés</span>
              </div>
              <div class="highlight-item">
                <i class="bi bi-check-circle-fill"></i>
                <span>Approche multidisciplinaire</span>
              </div>
              <div class="highlight-item">
                <i class="bi bi-check-circle-fill"></i>
                <span>Ancrage africain</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════ PRIORITÉS STRATÉGIQUES ════════ -->
    <section class="section">
      <div class="container">
        <div class="text-center mb-header">
          <span class="section-badge">Nos axes</span>
          <h2 class="section-title">Priorités Stratégiques</h2>
          <p class="section-subtitle">Les piliers qui guident notre démarche de formation et d'innovation</p>
        </div>
        <div class="priorities-grid">
          <div v-for="(p, i) in priorities" :key="i" class="priority-card">
            <div class="priority-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="priority-icon">
              <i :class="'bi ' + p.icon"></i>
            </div>
            <h4 class="priority-title">{{ p.title }}</h4>
            <p class="priority-text">{{ p.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════ FORMATIONS ════════ -->
    <section class="section">
      <div class="container">
        <div class="courses-header">
          <div>
            <span class="section-badge">Catalogue</span>
            <h2 class="section-title">Nos Formations</h2>
            <p class="section-subtitle">Découvrez nos programmes adaptés au contexte africain</p>
          </div>
          <RouterLink to="/browse-courses" class="btn-see-all">
            Voir tous les cours <i class="bi bi-arrow-right"></i>
          </RouterLink>
        </div>
        <div class="courses-list">
          <RouterLink
            v-for="(course, idx) in featuredCourses"
            :key="course.id"
            :to="`/course/${course.id}`"
            class="course-card"
          >
            <span class="course-num">{{ String(idx + 1).padStart(2, '0') }}</span>
            <div class="course-thumb">
              <img :src="course.image_url || 'https://placehold.co/600x400?text=Course'" :alt="course.title" />
            </div>
            <div class="course-body">
              <div class="course-meta-top">
                <span class="course-cat">
                  <i class="bi bi-bookmark-fill"></i> Formation
                </span>
                <span class="course-instructor">
                  <i class="bi bi-person-circle"></i>
                  {{ course.instructor?.name || 'Instructeur' }}
                </span>
              </div>
              <h5 class="course-title">{{ course.title }}</h5>
              <p class="course-desc">
                {{ (course.description && course.description.length > 50) ? course.description.slice(0, 120) + '…' : (course.description || '') }}
              </p>
            </div>
            <div class="course-arrow">
              <i class="bi bi-arrow-right"></i>
            </div>
          </RouterLink>
        </div>
        <div v-if="featuredCourses.length === 0" class="empty-courses">
          <i class="bi bi-journal-bookmark"></i>
          <p>Aucun cours à afficher pour le moment.</p>
        </div>
      </div>
    </section>

    <!-- ════════ TÉMOIGNAGES ════════ -->
    <section class="section section-alt">
      <div class="container">
        <div class="text-center mb-header">
          <span class="section-badge">Témoignages</span>
          <h2 class="section-title">Ce que disent nos étudiants</h2>
        </div>
        <div class="testimonials-grid">
          <div v-for="(t, i) in testimonials" :key="i" class="testimonial-card">
            <div class="testimonial-quote">
              <i class="bi bi-quote"></i>
            </div>
            <p class="testimonial-text">{{ t.content }}</p>
            <div class="testimonial-author">
              <img :src="t.avatar" :alt="t.name" class="testimonial-avatar" />
              <div>
                <strong class="testimonial-name">{{ t.name }}</strong>
                <span class="testimonial-role">{{ t.position }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════ PARTENAIRES ════════ -->
    <section class="partners-section">
      <div class="container">
        <div class="text-center mb-header">
          <span class="section-badge">Réseau</span>
          <h2 class="section-title">Nos Partenaires</h2>
          <p class="section-subtitle">Ils nous font confiance et soutiennent notre mission</p>
        </div>
      </div>
      <div class="partners-ticker">
        <div class="partners-track">
          <div v-for="n in 3" :key="n" class="partners-set">
            <div v-for="(partner, i) in partners" :key="`${n}-${i}`" class="partner-card">
              <img :src="partner.logo" :alt="partner.name" class="partner-logo" />
              <span class="partner-name">{{ partner.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════ CTA ════════ -->
    <section class="cta-section">
      <div class="cta-bg"></div>
      <div class="container cta-inner">
        <div class="cta-content">
          <h2 class="cta-title">Prêt à développer votre vocation ?</h2>
          <p class="cta-subtitle">
            Rejoignez ACATHECPA dès aujourd'hui et commencez votre parcours pour devenir
            un leader transformateur au service de l'Église et de la société.
          </p>
          <div class="cta-actions">
            <RouterLink to="/register" class="btn-cta-primary">
              <i class="bi bi-person-plus"></i> S'inscrire maintenant
            </RouterLink>
            <RouterLink to="/contact" class="btn-cta-outline">
              <i class="bi bi-envelope"></i> Nous contacter
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped lang="scss">
/* ═══════════════════════════════════════════════
   PALETTE (from project CSS variables)
   ═══════════════════════════════════════════════ */
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

.home-page {
  overflow-x: hidden;
}

/* ═══════ SHARED ═══════ */
.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 24px;
}
.text-center { text-align: center; }

.section {
  padding: 60px 0;
}
.section-alt {
  background: $neutral;
}

.mb-header {
  margin-bottom: 36px;
}

.section-badge {
  display: inline-block;
  padding: 5px 16px;
  border-radius: 20px;
  font-size: .78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: $secondary;
  background: rgba($secondary, .1);
  margin-bottom: 12px;
}

.section-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: $dark;
  margin: 0 0 10px;
  line-height: 1.2;
}
.section-subtitle {
  font-size: 1.05rem;
  color: $text-light;
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ═══════ HERO ═══════ */
.hero {
  position: relative;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 24px 60px;
  overflow: hidden;
}
.hero-bg {
  position: absolute;
  inset: 0;
  background: url('https://images.unsplash.com/photo-1589739907626-5bfb198dde73?crop=entropy&cs=tinysrgb&fit=crop&h=800&w=1600') no-repeat center center;
  background-size: cover;
  z-index: 0;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, rgba($secondary, .88) 0%, rgba($dark, .82) 100%);
  z-index: 1;
}

/* ── Floating particles animation ── */
.hero-particles {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: hidden;
  pointer-events: none;
}
.particle {
  position: absolute;
  opacity: 0;
  animation: floatUp linear infinite;
}

/* Icon particles */
.p-icon {
  color: rgba(#fff, .12);
  line-height: 1;
}

/* Brand text particles */
.p-brand {
  font-family: inherit;
  font-weight: 900;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: rgba(#fff, .04);
  white-space: nowrap;
}

/* ── Individual positions & sizes ── */
.p1 {
  font-size: 2.2rem;
  left: 5%; bottom: -40px;
  color: rgba($accent, .18);
  animation-duration: 14s;
  animation-delay: 0s;
}
.p2 {
  font-size: 1.6rem;
  left: 18%; bottom: -40px;
  animation-duration: 11s;
  animation-delay: 2s;
}
.p3 {
  font-size: 3rem;
  left: 32%; bottom: -40px;
  color: rgba($accent, .12);
  animation-duration: 18s;
  animation-delay: 1s;
}
.p4 {
  font-size: 1.4rem;
  left: 48%; bottom: -40px;
  animation-duration: 13s;
  animation-delay: 4s;
}
.p5 {
  font-size: 3.5rem;
  left: 62%; bottom: -40px;
  color: rgba($accent, .14);
  animation-duration: 20s;
  animation-delay: 3s;
}
.p6 {
  font-size: 1.3rem;
  left: 78%; bottom: -40px;
  animation-duration: 12s;
  animation-delay: 6s;
}
.p7 {
  font-size: 2rem;
  left: 88%; bottom: -40px;
  color: rgba($accent, .16);
  animation-duration: 16s;
  animation-delay: 5s;
}
.p8 {
  font-size: 2.8rem;
  left: 25%; bottom: -40px;
  color: rgba($accent, .1);
  animation-duration: 19s;
  animation-delay: 8s;
}
.p9 {
  font-size: 1.8rem;
  left: 72%; bottom: -40px;
  animation-duration: 15s;
  animation-delay: 7s;
}
.p10 {
  font-size: 1.5rem;
  left: 42%; bottom: -40px;
  animation-duration: 14s;
  animation-delay: 9s;
}

/* Brand name - large floating text */
.p11 {
  font-size: 4.5rem;
  left: -2%; bottom: -60px;
  color: rgba(#fff, .03);
  animation-duration: 26s;
  animation-delay: 2s;
}
.p12 {
  font-size: 6rem;
  right: -2%; left: auto;
  bottom: -60px;
  color: rgba(#fff, .025);
  animation-duration: 30s;
  animation-delay: 10s;
}

@keyframes floatUp {
  0% {
    opacity: 0;
    transform: translateY(0) rotate(0deg) scale(.7);
  }
  8% {
    opacity: 1;
  }
  85% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(-750px) rotate(25deg) scale(1.1);
  }
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 720px;
  text-align: center;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 18px;
  border-radius: 24px;
  background: rgba(#fff, .15);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: .82rem;
  font-weight: 600;
  margin-bottom: 24px;
  i { font-size: .9rem; }
}
.hero-title {
  font-size: 3.2rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 20px;
  line-height: 1.15;
  min-height: 1.2em;
}
.hero-subtitle {
  font-size: 1.12rem;
  color: rgba(#fff, .85);
  line-height: 1.7;
  margin: 0 0 36px;
}
.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}
.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  border-radius: 10px;
  background: $accent;
  color: $dark;
  font-weight: 700;
  font-size: .95rem;
  text-decoration: none;
  transition: all .25s;
  box-shadow: 0 4px 16px rgba($accent, .35);
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px rgba($accent, .45);
    background: darken($accent, 5%);
  }
}
.btn-hero-outline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  border-radius: 10px;
  border: 2px solid rgba(#fff, .35);
  background: rgba(#fff, .08);
  color: #fff;
  font-weight: 600;
  font-size: .95rem;
  text-decoration: none;
  transition: all .25s;
  &:hover {
    background: rgba(#fff, .18);
    border-color: rgba(#fff, .55);
  }
}

/* ── Hero Stats ── */
.hero-stats {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 0;
  margin-top: 56px;
  padding: 20px 40px;
  background: rgba(#fff, .12);
  backdrop-filter: blur(10px);
  border-radius: $radius-lg;
  border: 1px solid rgba(#fff, .15);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 28px;
}
.stat-number {
  font-size: 1.6rem;
  font-weight: 800;
  color: $accent;
}
.stat-label {
  font-size: .78rem;
  color: rgba(#fff, .75);
  font-weight: 500;
  margin-top: 2px;
}
.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(#fff, .2);
}

/* ═══════ ABOUT ═══════ */
.about-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 60px;
  align-items: center;
}
.about-visual {
  position: relative;
}
.about-img-wrap {
  background: #fff;
  border-radius: $radius-lg;
  padding: 28px;
  box-shadow: $shadow;
  display: flex;
  align-items: center;
  justify-content: center;
}
.about-img {
  width: 100%;
  max-width: 280px;
  height: auto;
}
.about-accent-dot {
  position: absolute;
  bottom: -16px;
  right: -16px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba($accent, .18);
  z-index: -1;
}
.about-desc {
  font-size: 1.02rem;
  color: $text-light;
  line-height: 1.75;
  margin: 0 0 28px;
}
.about-highlights {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.highlight-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: .9rem;
  font-weight: 600;
  color: $text;
  i {
    color: $success;
    font-size: 1.1rem;
  }
}

/* ═══════ VISION / MISSION TOGGLE (under logo) ═══════ */
.vm-toggle {
  margin-top: 24px;
}
.vm-tabs {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 16px;
}
.vm-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 24px;
  border: 1.5px solid $border;
  background: #fff;
  color: $text-light;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all .25s;
  &.active {
    background: $secondary;
    border-color: $secondary;
    color: #fff;
  }
  &:not(.active):hover {
    border-color: $secondary;
    color: $secondary;
  }
}
.vm-text {
  font-size: .9rem;
  color: $text-light;
  line-height: 1.65;
  margin: 0;
  text-align: center;
}
.vm-fade-enter-active,
.vm-fade-leave-active {
  transition: opacity .35s, transform .35s;
}
.vm-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.vm-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ═══════ PRIORITIES ═══════ */
.priorities-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.priority-card {
  background: #fff;
  border-radius: $radius-lg;
  padding: 32px 28px;
  box-shadow: $shadow-sm;
  border-top: 3px solid $secondary;
  transition: all .3s;
  position: relative;
  &:hover {
    box-shadow: $shadow;
    transform: translateY(-4px);
  }
}
.priority-num {
  position: absolute;
  top: 20px;
  right: 22px;
  font-size: 2.4rem;
  font-weight: 900;
  color: rgba($secondary, .08);
  line-height: 1;
}
.priority-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 1.25rem;
  background: rgba($success, .1);
  color: $success;
  margin-bottom: 20px;
}
.priority-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 10px;
}
.priority-text {
  font-size: .9rem;
  color: $text-light;
  line-height: 1.65;
  margin: 0;
}

/* ═══════ VALUES TICKER ═══════ */
.values-ticker {
  position: relative;
  z-index: 2;
  margin-top: 20px;
  overflow: hidden;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  background: rgba(#fff, .08);
  backdrop-filter: blur(6px);
  border-top: 1px solid rgba(#fff, .1);
  border-bottom: 1px solid rgba(#fff, .1);
  padding: 12px 0;
}
.ticker-track {
  display: flex;
  width: max-content;
  animation: tickerScroll 28s linear infinite;
}
.ticker-set {
  display: flex;
  flex-shrink: 0;
}
.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0 32px;
  font-size: .82rem;
  font-weight: 600;
  color: rgba(#fff, .75);
  white-space: nowrap;
  letter-spacing: .02em;
  i {
    font-size: .88rem;
    color: $accent;
  }
}
@keyframes tickerScroll {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ═══════ COURSES ═══════ */
.courses-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 20px;
  .section-subtitle { margin: 0; text-align: left; }
}
.btn-see-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border-radius: 10px;
  border: 1.5px solid $border;
  color: $text;
  font-size: .88rem;
  font-weight: 600;
  text-decoration: none;
  transition: all .2s;
  white-space: nowrap;
  &:hover {
    border-color: $primary;
    color: $primary;
    background: rgba($primary, .04);
  }
}
.courses-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.course-card {
  display: grid;
  grid-template-columns: auto 110px 1fr auto;
  align-items: center;
  gap: 0;
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: all .3s;
  &:hover {
    box-shadow: $shadow;
    transform: translateY(-3px);
    border-color: rgba($secondary, .25);
    .course-arrow { color: $primary; transform: translateX(3px); }
    .course-thumb img { transform: scale(1.08); }
  }
}
.course-num {
  font-size: 1.5rem;
  font-weight: 900;
  color: rgba($secondary, .12);
  padding: 0 20px 0 24px;
  line-height: 1;
  user-select: none;
}
.course-thumb {
  width: 110px;
  height: 90px;
  overflow: hidden;
  border-radius: 10px;
  margin: 12px 0;
  flex-shrink: 0;
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform .4s;
  }
}
.course-body {
  padding: 16px 24px;
  min-width: 0;
}
.course-meta-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 6px;
}
.course-cat {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: $secondary;
  i { font-size: .68rem; }
}
.course-instructor {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: .78rem;
  color: $text-light;
  i { color: $secondary; font-size: .76rem; }
}
.course-title {
  font-size: 1.02rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 5px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.course-desc {
  font-size: .84rem;
  color: $text-light;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.course-arrow {
  padding: 0 24px;
  font-size: 1.2rem;
  color: $text-light;
  transition: all .25s;
}
.empty-courses {
  text-align: center;
  padding: 48px 0;
  color: $text-light;
  i { font-size: 2.4rem; display: block; margin-bottom: 12px; opacity: .4; }
  p { margin: 0; font-size: .95rem; }
}

/* ═══════ TESTIMONIALS ═══════ */
.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
.testimonial-card {
  background: #fff;
  border-radius: $radius-lg;
  padding: 32px 28px 28px;
  box-shadow: $shadow-sm;
  transition: all .3s;
  position: relative;
  &:hover {
    box-shadow: $shadow;
    transform: translateY(-2px);
  }
}
.testimonial-quote {
  font-size: 2.6rem;
  line-height: 1;
  color: rgba($secondary, .15);
  margin-bottom: 8px;
}
.testimonial-text {
  font-size: .94rem;
  color: $text-light;
  line-height: 1.7;
  margin: 0 0 20px;
  font-style: italic;
}
.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}
.testimonial-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid $border;
}
.testimonial-name {
  display: block;
  font-size: .9rem;
  font-weight: 700;
  color: $dark;
}
.testimonial-role {
  font-size: .78rem;
  color: $text-light;
}

/* ═══════ PARTNERS ═══════ */
.partners-section {
  padding: 60px 0 48px;
  background: $neutral;
  overflow: hidden;
}
.partners-ticker {
  position: relative;
  width: 100%;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
}
.partners-track {
  display: flex;
  width: max-content;
  animation: partnersScroll 22s linear infinite;
  &:hover { animation-play-state: paused; }
}
.partners-set {
  display: flex;
  flex-shrink: 0;
}
.partner-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin: 0 24px;
  padding: 24px 32px;
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  min-width: 200px;
  transition: all .3s;
  cursor: default;
  &:hover {
    box-shadow: $shadow;
    transform: translateY(-3px);
    border-color: rgba($secondary, .2);
  }
}
.partner-logo {
  max-height: 52px;
  width: auto;
  opacity: .65;
  transition: opacity .3s;
  filter: grayscale(.4);
  .partner-card:hover & { opacity: 1; filter: grayscale(0); }
}
.partner-name {
  font-size: .78rem;
  font-weight: 600;
  color: $text-light;
  text-align: center;
  white-space: nowrap;
}
@keyframes partnersScroll {
  0%   { transform: translateX(0); }
  100% { transform: translateX(calc(-100% / 3)); }
}

/* ═══════ CTA ═══════ */
.cta-section {
  position: relative;
  padding: 80px 24px;
  overflow: hidden;
}
.cta-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, $secondary 0%, darken($secondary, 12%) 50%, $success 100%);
  z-index: 0;
}
.cta-inner {
  position: relative;
  z-index: 1;
}
.cta-content {
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
}
.cta-title {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 16px;
}
.cta-subtitle {
  font-size: 1.02rem;
  color: rgba(#fff, .82);
  line-height: 1.7;
  margin: 0 0 32px;
}
.cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}
.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  border-radius: 10px;
  background: $accent;
  color: $dark;
  font-weight: 700;
  font-size: .95rem;
  text-decoration: none;
  transition: all .25s;
  box-shadow: 0 4px 16px rgba($accent, .3);
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px rgba($accent, .4);
  }
}
.btn-cta-outline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  border-radius: 10px;
  border: 2px solid rgba(#fff, .35);
  background: rgba(#fff, .08);
  color: #fff;
  font-weight: 600;
  font-size: .95rem;
  text-decoration: none;
  transition: all .25s;
  &:hover {
    background: rgba(#fff, .18);
    border-color: rgba(#fff, .55);
  }
}

/* ═══════ RESPONSIVE ═══════ */
@media (max-width: 991px) {
  .hero-title { font-size: 2.4rem; }
  .hero-stats { flex-wrap: wrap; padding: 16px 20px; gap: 8px; }
  .stat-item { padding: 8px 16px; }
  .stat-divider { display: none; }
  .about-grid { grid-template-columns: 1fr; gap: 36px; text-align: center; }
  .about-highlights { justify-content: center; }
  .priorities-grid { grid-template-columns: 1fr 1fr; }
  .section-title { font-size: 1.75rem; }
}

@media (max-width: 640px) {
  .section { padding: 44px 0; }
  .hero { min-height: 500px; padding: 80px 18px 48px; }
  .hero-title { font-size: 2rem; }
  .hero-subtitle { font-size: .98rem; }
  .hero-stats { margin-top: 36px; }
  .stat-number { font-size: 1.3rem; }
  .priorities-grid, .testimonials-grid { grid-template-columns: 1fr; }
  .courses-header { flex-direction: column; align-items: flex-start; }
  .course-card { grid-template-columns: 1fr; }
  .course-num { display: none; }
  .course-thumb { width: 100%; height: 160px; border-radius: 0; margin: 0; }
  .course-arrow { display: none; }
  .about-highlights { grid-template-columns: 1fr; }
  .vm-tabs { flex-direction: column; align-items: stretch; }
}
</style>