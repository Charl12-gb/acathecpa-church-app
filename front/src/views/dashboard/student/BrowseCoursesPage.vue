<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getAllCourses, getMyEnrolledCourses, enrollInCourse } from '../../../services/api/course';
import { initiatePayment, confirmPayment } from '../../../services/api/payment';
import type { Course } from '../../../types/api';
import { CourseStatus } from '../../../types/api';
import { useRouter } from 'vue-router';

// Sample categories - these could also come from an API in a real app
const categories = [
  'Tous', // This is a filter option, not a real category from backend typically
  'Développement',
  'Business',
  'Marketing',
  'Design',
  'Finance',
  'Langues',
];

const router = useRouter();

const courses = ref<Course[]>([]);
const enrolledCourseIds = ref<Set<number>>(new Set());
const isLoading = ref(false);
const error = ref<string | null>(null);

// Filters
const filters = ref({
  category: 'Tous', // This will filter client-side based on a non-existent 'category' field on Course type for now
  search: '',
  level: 'all', // 'level' is not on Course type
  priceRange: 'all', // 'price' is not on Course type
});

const fetchAllPublishedCourses = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // Backend returns published courses by default if no status is specified or handled by default in service
    // Explicitly requesting published status as per subtask requirement
    courses.value = await getAllCourses({ status: 'published' as CourseStatus });
  } catch (err: any) {
    console.error('Failed to fetch courses:', err);
    error.value = err.message || 'Erreur lors du chargement des cours.';
  } finally {
    isLoading.value = false;
  }
};

const fetchMyEnrolledCourseIds = async () => {
  try {
    const enrolledCourses = await getMyEnrolledCourses();
    enrolledCourseIds.value = new Set(enrolledCourses.map(course => course.id));
  } catch (err) {
    // Non blocking: if this fails, we still show the public course list.
    console.warn('Failed to fetch enrolled courses for filtering:', err);
  }
};

onMounted(() => {
  Promise.all([fetchAllPublishedCourses(), fetchMyEnrolledCourseIds()]);
});

// Computed filtered courses
const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    // Hide courses where the student is already enrolled.
    if (enrolledCourseIds.value.has(course.id)) {
      return false;
    }

    // Category filter - NOTE: 'category' field doesn't exist on the Course type from API.
    // This filter will not work as intended without backend support or different client-side logic.
    // For now, it will effectively be ignored unless course objects are mapped to include a category.
    if (filters.value.category !== 'Tous' && (course as any).category !== filters.value.category) {
      return false;
    }
    
    // Search filter
    if (filters.value.search && !course.title.toLowerCase().includes(filters.value.search.toLowerCase())) {
      return false;
    }
    
    // Level filter - NOTE: 'level' field doesn't exist on the Course type.
    if (filters.value.level !== 'all' && (course as any).level !== filters.value.level) {
      return false;
    }
    
    // Price filter - Now uses course.price and course.is_free from the updated Course type
    if (filters.value.priceRange !== 'all') {
      if (filters.value.priceRange === 'free') { // Handle 'free' filter option
        if (!course.is_free) return false;
      } else if (course.is_free) {
        // If filtering for a non-'free' price range, free courses should not match
        return false;
      } else if (course.price != null) { // Course is not free, has a price
        if (filters.value.priceRange === 'under-100' && course.price >= 100) {
          return false;
        } else if (filters.value.priceRange === '100-200' && (course.price < 100 || course.price > 200)) {
          return false;
        } else if (filters.value.priceRange === 'over-200' && course.price <= 200) {
          return false;
        }
      } else {
        // Course is not free and has no price, won't match numerical ranges unless 'all'
        return false;
      }
    }

    return true;
  });
});

const enrollingCourseId = ref<number | null>(null);

// Modal state
const showEnrollModal = ref(false);
const selectedCourse = ref<Course | null>(null);
const enrollSuccess = ref(false);
const enrollError = ref<string | null>(null);

const openEnrollModal = (course: Course) => {
  selectedCourse.value = course;
  enrollError.value = null;
  enrollSuccess.value = false;
  showEnrollModal.value = true;
};

const closeEnrollModal = () => {
  showEnrollModal.value = false;
  if (enrollSuccess.value) {
    router.push('/my-courses');
  }
};

const confirmEnroll = async () => {
  if (!selectedCourse.value) return;
  const courseToEnroll = selectedCourse.value;
  enrollingCourseId.value = courseToEnroll.id;
  enrollError.value = null;
  try {
    if (courseToEnroll.is_free || !courseToEnroll.price || courseToEnroll.price <= 0) {
      await enrollInCourse(courseToEnroll.id);
    } else {
      const payment = await initiatePayment({
        course_id: courseToEnroll.id,
        amount: courseToEnroll.price,
        currency: 'XOF',
      });
      await confirmPayment(payment.id);
      await enrollInCourse(courseToEnroll.id);
    }
    enrollSuccess.value = true;
  } catch (err: any) {
    console.error('Failed to enroll in course:', err);
    enrollError.value = err.response?.data?.detail || err.message || "Erreur lors de l'inscription.";
  } finally {
    enrollingCourseId.value = null;
  }
};

const getCourseCategory = (course: Course) => {
  const rawCategory = (course as unknown as { category?: string }).category;
  return rawCategory || 'N/A';
};
</script>

<template>
  <div class="browse-courses-page">
    <!-- Toolbar : Search + Filters unified -->
    <div class="toolbar">
      <div class="toolbar-top">
        <div class="search-wrapper">
          <i class="bi bi-search"></i>
          <input
            type="text"
            v-model="filters.search"
            placeholder="Rechercher un cours…"
          >
          <button v-if="filters.search" class="clear-btn" @click="filters.search = ''">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="toolbar-selects">
          <div class="select-wrap">
            <i class="bi bi-bar-chart-line"></i>
            <select v-model="filters.level">
              <option value="all">Tous niveaux</option>
              <option value="Débutant">Débutant</option>
              <option value="Intermédiaire">Intermédiaire</option>
              <option value="Avancé">Avancé</option>
            </select>
          </div>
          <div class="select-wrap">
            <i class="bi bi-tag"></i>
            <select v-model="filters.priceRange">
              <option value="all">Tous prix</option>
              <option value="free">Gratuit</option>
              <option value="under-100">&lt; 100 XOF</option>
              <option value="100-200">100 – 200 XOF</option>
              <option value="over-200">&gt; 200 XOF</option>
            </select>
          </div>
        </div>
      </div>

      <div class="toolbar-bottom">
        <div class="category-pills">
          <button
            v-for="cat in categories" :key="cat"
            class="pill"
            :class="{ active: filters.category === cat }"
            @click="filters.category = cat"
          >
            {{ cat }}
          </button>
        </div>
        <span class="result-count">
          <strong>{{ filteredCourses.length }}</strong> cours trouvé{{ filteredCourses.length > 1 ? 's' : '' }}
        </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement des cours…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-banner">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <span>{{ error }}</span>
      <button @click="fetchAllPublishedCourses">Réessayer</button>
    </div>

    <!-- Course Grid -->
    <div v-else-if="filteredCourses.length > 0" class="course-list">
      <article v-for="course in filteredCourses" :key="course.id" class="course-card">
        <!-- Thumbnail -->
        <RouterLink :to="`/course/${course.id}`" class="card-thumb">
          <img
            :src="course.image_url || 'https://placehold.co/400x220/e8eef7/2453a7?text=Cours'"
            :alt="course.title"
          >
          <span class="thumb-price" :class="{ free: course.is_free }">
            <template v-if="course.is_free">Gratuit</template>
            <template v-else-if="course.price != null">{{ course.price }}&nbsp;XOF</template>
            <template v-else>—</template>
          </span>
        </RouterLink>

        <!-- Info -->
        <div class="card-body">
          <div class="card-header-row">
            <span class="cat-badge">{{ getCourseCategory(course) }}</span>
            <span v-if="course.objectives && course.objectives.length" class="obj-count">
              <i class="bi bi-bullseye"></i> {{ course.objectives.length }} objectif{{ course.objectives.length > 1 ? 's' : '' }}
            </span>
          </div>

          <RouterLink :to="`/course/${course.id}`" class="card-title">{{ course.title }}</RouterLink>
          <p class="card-desc">{{ course.short_description || course.description?.substring(0, 130) + '…' }}</p>

          <div class="card-meta">
            <span class="meta-instructor">
              <span class="instructor-avatar"><i class="bi bi-person-fill"></i></span>
              {{ course.instructor.name }}
            </span>
            <div v-if="course.objectives && course.objectives.length" class="meta-tags">
              <span class="tag" v-for="obj in course.objectives.slice(0, 2)" :key="obj">{{ obj }}</span>
              <span class="tag-more" v-if="course.objectives.length > 2">+{{ course.objectives.length - 2 }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-side">
          <div class="side-price">
            <span v-if="course.is_free" class="price free">Gratuit</span>
            <span v-else-if="course.price != null" class="price">{{ course.price }}<small> XOF</small></span>
          </div>
          <button
            class="btn-enroll"
            @click="openEnrollModal(course)"
            :disabled="enrollingCourseId === course.id"
          >
            <span v-if="enrollingCourseId === course.id" class="spinner-border spinner-border-sm" role="status"></span>
            <template v-else>
              <i class="bi bi-plus-circle"></i>
              {{ course.is_free || !course.price ? "S'inscrire" : 'Payer' }}
            </template>
          </button>
          <RouterLink :to="`/course/${course.id}`" class="btn-view">
            Voir détails <i class="bi bi-arrow-right"></i>
          </RouterLink>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-illustration">
        <i class="bi bi-binoculars"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p>Aucun résultat ne correspond à vos critères. Essayez d'autres filtres.</p>
      <button
        class="btn-reset"
        @click="filters = { category: 'Tous', search: '', level: 'all', priceRange: 'all' }"
      >
        <i class="bi bi-arrow-counterclockwise me-1"></i> Réinitialiser les filtres
      </button>
    </div>

    <!-- ═══ Enrollment Modal ═══ -->
    <Teleport to="body">
      <div v-if="showEnrollModal && selectedCourse" class="enroll-modal-backdrop" @click.self="closeEnrollModal">
        <div class="enroll-modal">
          <button class="enroll-modal-close" @click="closeEnrollModal"><i class="bi bi-x-lg"></i></button>

          <!-- Success state -->
          <div v-if="enrollSuccess" class="enroll-modal-body enroll-success-state">
            <div class="success-icon"><i class="bi bi-check-circle-fill"></i></div>
            <h3>Inscription réussie !</h3>
            <p>Vous êtes maintenant inscrit à <strong>{{ selectedCourse.title }}</strong>.</p>
            <button class="enroll-modal-btn primary" @click="closeEnrollModal">
              <i class="bi bi-arrow-right"></i> Accéder à mes cours
            </button>
          </div>

          <!-- Confirm state -->
          <template v-else>
            <div class="enroll-modal-header">
              <div class="enroll-modal-icon" :class="{ free: selectedCourse.is_free || !selectedCourse.price }">
                <i :class="selectedCourse.is_free || !selectedCourse.price ? 'bi bi-bookmark-check-fill' : 'bi bi-credit-card-fill'"></i>
              </div>
              <h3>{{ selectedCourse.is_free || !selectedCourse.price ? 'Confirmer l\'inscription' : 'Paiement & inscription' }}</h3>
              <p class="enroll-modal-subtitle">{{ selectedCourse.title }}</p>
            </div>

            <div class="enroll-modal-body">
              <div class="enroll-modal-details">
                <div class="enroll-detail-row">
                  <span class="detail-label"><i class="bi bi-person"></i> Formateur</span>
                  <span class="detail-value">{{ selectedCourse.instructor.name }}</span>
                </div>
                <div v-if="selectedCourse.sections" class="enroll-detail-row">
                  <span class="detail-label"><i class="bi bi-collection"></i> Contenu</span>
                  <span class="detail-value">{{ selectedCourse.sections.length }} sections</span>
                </div>
                <div class="enroll-detail-row highlight">
                  <span class="detail-label"><i class="bi bi-tag-fill"></i> Prix</span>
                  <span class="detail-value price">
                    <template v-if="selectedCourse.is_free || !selectedCourse.price">Gratuit</template>
                    <template v-else>{{ selectedCourse.price }} XOF</template>
                  </span>
                </div>
              </div>

              <div v-if="enrollError" class="enroll-error">
                <i class="bi bi-exclamation-triangle-fill"></i> {{ enrollError }}
              </div>

              <div class="enroll-modal-actions">
                <button class="enroll-modal-btn secondary" @click="closeEnrollModal" :disabled="enrollingCourseId !== null">
                  Annuler
                </button>
                <button class="enroll-modal-btn primary" @click="confirmEnroll" :disabled="enrollingCourseId !== null">
                  <span v-if="enrollingCourseId !== null" class="spinner-border spinner-border-sm"></span>
                  <template v-else>
                    <i :class="selectedCourse.is_free || !selectedCourse.price ? 'bi bi-check-lg' : 'bi bi-lock-fill'"></i>
                    {{ selectedCourse.is_free || !selectedCourse.price ? "Confirmer l'inscription" : 'Payer ' + selectedCourse.price + ' XOF' }}
                  </template>
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped lang="scss">
// ─── Palette ────────────────────────────────────
$primary:     #2453a7;
$primary-dark:#1a3f8a;
$primary-soft:#eaf2ff;
$dark:        #1a2332;
$gray:        #6b7280;
$gray-light:  #f4f7fb;
$border:      #dfe8f6;
$radius:      14px;

.browse-courses-page {
  max-width: 1140px;
  margin: 0 auto;
}

// ─── Toolbar ─────────────────────────────────────
.toolbar {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(16, 24, 40, 0.04);
}

.toolbar-top {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
  margin-bottom: 0.85rem;
}

.search-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;

  > i {
    position: absolute;
    left: 0.85rem;
    color: $gray;
    font-size: 0.9rem;
    pointer-events: none;
  }

  input {
    width: 100%;
    border: 1.5px solid $border;
    border-radius: 10px;
    padding: 0.55rem 2.4rem 0.55rem 2.4rem;
    font-size: 0.88rem;
    color: $dark;
    background: $gray-light;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;

    &::placeholder { color: #9ca3af; }

    &:focus {
      border-color: $primary;
      background: #fff;
      box-shadow: 0 0 0 3px rgba($primary, 0.08);
    }
  }

  .clear-btn {
    position: absolute;
    right: 0.65rem;
    background: none;
    border: none;
    color: $gray;
    cursor: pointer;
    padding: 0.15rem;
    line-height: 1;
    font-size: 0.8rem;
    transition: color 0.15s;
    &:hover { color: $dark; }
  }
}

.toolbar-selects {
  display: flex;
  gap: 0.5rem;
}

.select-wrap {
  position: relative;
  display: flex;
  align-items: center;

  > i {
    position: absolute;
    left: 0.65rem;
    color: $primary;
    font-size: 0.78rem;
    pointer-events: none;
  }

  select {
    border: 1.5px solid $border;
    border-radius: 10px;
    padding: 0.55rem 1.8rem 0.55rem 2rem;
    font-size: 0.82rem;
    color: $dark;
    background: $gray-light;
    appearance: auto;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s;

    &:focus {
      border-color: $primary;
    }
  }
}

.toolbar-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid lighten($border, 3%);
}

// ─── Category pills ─────────────────────────────
.category-pills {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.pill {
  background: transparent;
  border: 1.5px solid $border;
  border-radius: 999px;
  padding: 0.28rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: $gray;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $primary;
    color: $primary;
    background: $primary-soft;
  }

  &.active {
    background: $primary;
    border-color: $primary;
    color: #fff;
    font-weight: 600;
  }
}

.result-count {
  font-size: 0.78rem;
  color: $gray;
  white-space: nowrap;

  strong {
    color: $primary;
    font-weight: 700;
  }
}

// ─── Loading ────────────────────────────────────
.loading-state {
  text-align: center;
  padding: 4rem 1rem;

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $border;
    border-top-color: $primary;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    margin: 0 auto 1rem;
  }

  p {
    color: $gray;
    font-size: 0.9rem;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// ─── Error banner ───────────────────────────────
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1.2rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 0.88rem;

  button {
    margin-left: auto;
    background: none;
    border: 1px solid #dc2626;
    color: #dc2626;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    cursor: pointer;
    &:hover { background: #dc2626; color: #fff; }
  }
}

// ─── Course List ────────────────────────────────
.course-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

// ─── Course Card (horizontal) ───────────────────
.course-card {
  display: flex;
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  overflow: hidden;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;

  &:hover {
    border-color: lighten($primary, 28%);
    box-shadow: 0 8px 30px rgba($primary, 0.1);
  }
}

// ── Thumbnail ───────────────────────────────────
.card-thumb {
  position: relative;
  flex-shrink: 0;
  width: 260px;
  height: 200px;
  overflow: hidden;
  display: block;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
  }

  .course-card:hover & img {
    transform: scale(1.06);
  }
}

.thumb-price {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  background: rgba(#fff, 0.95);
  color: $primary-dark;
  border-radius: 8px;
  padding: 0.2rem 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

  &.free {
    background: #10b981;
    color: #fff;
  }
}

// ── Body (center) ───────────────────────────────
.card-body {
  flex: 1;
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.card-header-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}

.cat-badge {
  background: $primary-soft;
  color: $primary;
  border-radius: 6px;
  padding: 0.15rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.obj-count {
  font-size: 0.72rem;
  color: $gray;
  i { color: $primary; margin-right: 0.2rem; }
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  line-height: 1.35;
  margin-bottom: 0.3rem;
  text-decoration: none;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.15s;

  &:hover { color: $primary; }
}

.card-desc {
  font-size: 0.82rem;
  color: $gray;
  line-height: 1.55;
  margin-bottom: 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.meta-instructor {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: $dark;
}

.instructor-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: $primary-soft;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  i { color: $primary; font-size: 0.75rem; }
}

.meta-tags {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-left: auto;
}

.tag {
  background: $gray-light;
  color: $gray;
  border: 1px solid $border;
  border-radius: 999px;
  padding: 0.12rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 500;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag-more {
  font-size: 0.68rem;
  color: $gray;
  font-weight: 600;
}

// ── Side panel (right) ──────────────────────────
.card-side {
  flex-shrink: 0;
  width: 150px;
  padding: 1rem 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border-left: 1px solid $border;
  background: $gray-light;
}

.side-price {
  text-align: center;
}

.price {
  font-size: 1.15rem;
  font-weight: 800;
  color: $dark;

  small {
    font-size: 0.65rem;
    font-weight: 500;
    color: $gray;
  }

  &.free {
    color: #10b981;
    font-size: 0.95rem;
  }
}

.btn-enroll {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem 0.6rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;

  &:hover:not(:disabled) {
    background: $primary-dark;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-view {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: $primary;
  text-decoration: none;
  transition: gap 0.2s;

  &:hover {
    gap: 0.5rem;
    text-decoration: underline;
  }
}

// ─── Empty state ────────────────────────────────
.empty-state {
  text-align: center;
  padding: 4.5rem 2rem;
}

.empty-illustration {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: $primary-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;

  i {
    font-size: 2.2rem;
    color: $primary;
  }
}

.empty-state h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: $dark;
  margin-bottom: 0.4rem;
}

.empty-state p {
  color: $gray;
  font-size: 0.88rem;
  max-width: 340px;
  margin: 0 auto 1.3rem;
}

.btn-reset {
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.3rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;

  &:hover { background: $primary-dark; }
}

// ─── Responsive ─────────────────────────────────
@media (max-width: 767.98px) {
  .toolbar-top {
    flex-direction: column;
  }

  .toolbar-selects {
    flex-direction: column;
    width: 100%;

    .select-wrap {
      width: 100%;
      select { width: 100%; }
    }
  }

  .toolbar-bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  // Cards become vertical on mobile
  .course-card {
    flex-direction: column;
  }

  .card-thumb {
    width: 100%;
    height: 210px;
  }

  .card-side {
    width: 100%;
    border-left: none;
    border-top: 1px solid $border;
    flex-direction: row;
    padding: 0.75rem 1rem;
    justify-content: space-between;
  }

  .side-price {
    text-align: left;
  }

  .meta-tags {
    margin-left: 0;
  }
}

@media (max-width: 400px) {
  .category-pills {
    gap: 0.3rem;
  }

  .pill {
    padding: 0.25rem 0.65rem;
    font-size: 0.72rem;
  }
}

// ═══════════════════════════════════════════════
// ENROLLMENT MODAL
// ═══════════════════════════════════════════════
.enroll-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: modalFadeIn 0.2s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.enroll-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  animation: modalSlideUp 0.25s ease;
}

@keyframes modalSlideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.enroll-modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: $gray;
  font-size: 1rem;
  cursor: pointer;
  z-index: 1;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  &:hover { background: $gray-light; color: $dark; }
}

.enroll-modal-header {
  padding: 1.5rem 1.5rem 0.75rem;
  text-align: center;

  h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 0.25rem;
  }
}

.enroll-modal-subtitle {
  font-size: 0.85rem;
  color: $gray;
  margin: 0;
}

.enroll-modal-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: $primary-soft;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;

  i { font-size: 1.4rem; color: $primary; }

  &.free {
    background: rgba(#10b981, 0.1);
    i { color: #10b981; }
  }
}

.enroll-modal-body {
  padding: 0.75rem 1.5rem 1.5rem;
}

.enroll-modal-details {
  background: $gray-light;
  border: 1px solid $border;
  border-radius: 12px;
  padding: 0.15rem 0;
  margin-bottom: 1rem;
}

.enroll-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;

  &:not(:last-child) { border-bottom: 1px solid $border; }
  &.highlight { background: rgba($primary, 0.03); }
}

.detail-label {
  color: $gray;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  i { color: $primary; font-size: 0.85rem; }
}

.detail-value {
  font-weight: 600;
  color: $dark;
  &.price { font-size: 1.05rem; font-weight: 800; color: $primary; }
}

.enroll-error {
  padding: 0.6rem 0.85rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-size: 0.82rem;
  margin-bottom: 1rem;
  i { margin-right: 0.3rem; }
}

.enroll-modal-actions {
  display: flex;
  gap: 0.6rem;
}

.enroll-modal-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.65rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;

  &.primary {
    background: $primary;
    color: #fff;
    &:hover:not(:disabled) { background: $primary-dark; }
  }

  &.secondary {
    background: $gray-light;
    color: $gray;
    border: 1px solid $border;
    &:hover:not(:disabled) { color: $dark; border-color: darken($border, 8%); }
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.enroll-success-state {
  text-align: center;
  padding: 2rem 1.5rem !important;

  h3 { font-size: 1.15rem; font-weight: 700; color: $dark; margin: 0 0 0.4rem; }
  p { font-size: 0.88rem; color: $gray; margin: 0 0 1.2rem; }
  .enroll-modal-btn { max-width: 250px; margin: 0 auto; }
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(#10b981, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  i { font-size: 2rem; color: #10b981; }
}
</style>