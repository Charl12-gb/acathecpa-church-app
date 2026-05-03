<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
// Chart.js components are registered but not actively used in the provided course list part.
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title } from 'chart.js'
// import { Line } from 'vue-chartjs'
import {
  getInstructorCourses,
  deleteCourse as apiDeleteCourse,
  publishCourse, // Added
  updateCourse   // Added
} from '../../../services/api/course'
import type { Course, CourseStatus } from '../../../types/api' // Added CourseStatus

// ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title)

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title)

const courses = ref<Course[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

// Filters
const filters = ref({
  status: 'all', // all, published, draft
  sort: 'recent' // recent, students, rating, revenue (Note: students, rating, revenue might not be available on Course type)
})

const fetchCourses = async () => {
  isLoading.value = true
  error.value = null
  try {
    // Assuming getInstructorCourses returns courses structured similarly to the old sample data for now.
    // Adjustments might be needed based on the actual API response structure.
    const fetchedCourses = await getInstructorCourses()
    courses.value = fetchedCourses || [];
  } catch (err: any) {
    console.error('Failed to fetch courses:', err)
    error.value = err.message || 'Erreur lors du chargement des cours.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchCourses()
})

// Computed filtered courses
const filteredCourses = computed(() => {
  let filtered = [...courses.value]
  
  // Status filter
  if (filters.value.status !== 'all') {
    // Ensure course.status matches the enum values if it's an enum
    filtered = filtered.filter(course => course.status === filters.value.status)
  }
  
  // Sorting - Adjust based on available fields in Course type
  switch (filters.value.sort) {
    case 'students':
      filtered.sort((a, b) => ((b as any).students || 0) - ((a as any).students || 0))
      break
    case 'rating':
      filtered.sort((a, b) => ((b as any).rating || 0) - ((a as any).rating || 0))
      break
    case 'revenue':
      filtered.sort((a, b) => ((b as any).revenue || 0) - ((a as any).revenue || 0))
      break
    default: // recent (using updated_at or created_at)
      filtered.sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
  }
  
  return filtered
})

const getCourseMetric = (course: Course, key: 'students' | 'rating' | 'revenue') => {
  const raw = course as unknown as { students?: number; rating?: number; revenue?: number };
  return raw[key] || 0;
}

const totalStudents = computed(() =>
  courses.value.reduce((sum, course) => sum + getCourseMetric(course, 'students'), 0)
)

const averageRating = computed(() => {
  const ratings = courses.value.map((course) => getCourseMetric(course, 'rating')).filter((value) => value > 0)
  if (ratings.length === 0) return '0.0'
  const avg = ratings.reduce((sum, value) => sum + value, 0) / ratings.length
  return avg.toFixed(1)
})

const totalRevenue = computed(() =>
  courses.value.reduce((sum, course) => sum + getCourseMetric(course, 'revenue'), 0)
)

const onCourseStatusChange = (courseId: number, event: Event) => {
  const target = event.target as HTMLSelectElement | null
  if (!target) return
  updateCourseStatus(courseId, target.value as CourseStatus)
}

// Chart data for enrollments
// const getEnrollmentChartData = (course: any) => {
//   return {
//     labels: ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin'],
//     datasets: [
//       {
//         label: 'Inscriptions',
//         data: course.monthlyEnrollments || [0,0,0,0,0,0],
//         borderColor: '#3498db',
//         backgroundColor: 'rgba(52, 152, 219, 0.1)',
//         tension: 0.4,
//         fill: true
//       }
//     ]
//   }
// }

// const chartOptions = {
//   responsive: true,
//   maintainAspectRatio: false,
//   plugins: {
//     legend: {
//       display: false
//     }
//   },
//   scales: {
//     y: {
//       beginAtZero: true
//     }
//   }
// }

const updateCourseStatus = async (courseId: number, newStatus: CourseStatus) => {
  // Simple loading state for now, could be per-course
  isLoading.value = true;
  try {
    if (newStatus === 'published') { // Assuming CourseStatus.PUBLISHED is 'published'
      await publishCourse(courseId);
    } else if (newStatus === 'draft') { // Assuming CourseStatus.DRAFT is 'draft'
      await updateCourse(courseId, { status: newStatus });
    }
    // Update local data to reflect the change immediately
    const course = courses.value.find(c => c.id === courseId);
    if (course) {
      course.status = newStatus;
    }
    // Or re-fetch: await fetchCourses();
  } catch (err: any) {
    console.error('Failed to update course status:', err);
    error.value = `Erreur lors de la mise à jour du statut: ${err.message || ' inconnue'}`;
    // Optionally, revert local change or show specific error to user
  } finally {
    isLoading.value = false;
  }
};

const deleteCourse = async (courseId: number) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce cours ?')) {
    try {
      await apiDeleteCourse(courseId) // Using aliased import
      courses.value = courses.value.filter(course => course.id !== courseId)
      // Optionally, show a success notification
    } catch (err: any) {
      console.error('Failed to delete course:', err)
      // Optionally, show an error notification
      alert(err.message || 'Erreur lors de la suppression du cours.')
    }
  }
}
</script>

<template>
  <div class="professor-courses-page">
    <!-- Toolbar : Header + Filters unified -->
    <div class="toolbar">
      <div class="toolbar-top">
        <div class="toolbar-title">
          <h1>Mes Cours</h1>
          <span class="result-count">
            <strong>{{ filteredCourses.length }}</strong> cours{{ filteredCourses.length > 1 ? 's' : '' }}
          </span>
        </div>
        <RouterLink to="/course-editor" class="btn-create">
          <i class="bi bi-plus-lg"></i> Créer un cours
        </RouterLink>
      </div>

      <!-- Stats Strip -->
      <div class="stats-strip">
        <div class="stat-chip">
          <i class="bi bi-book" style="color: #2453a7;"></i>
          <span><strong>{{ courses.length }}</strong> cours</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-people" style="color: #18794e;"></i>
          <span><strong>{{ totalStudents }}</strong> étudiants</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-star" style="color: #b45309;"></i>
          <span><strong>{{ averageRating }}</strong> note</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-currency-euro" style="color: #6b7280;"></i>
          <span><strong>{{ totalRevenue }}</strong> XOF</span>
        </div>
      </div>

      <div class="toolbar-bottom">
        <div class="toolbar-selects">
          <div class="select-wrap">
            <i class="bi bi-funnel"></i>
            <select v-model="filters.status">
              <option value="all">Tous les statuts</option>
              <option value="published">Publiés</option>
              <option value="draft">Brouillons</option>
            </select>
          </div>
          <div class="select-wrap">
            <i class="bi bi-sort-down"></i>
            <select v-model="filters.sort">
              <option value="recent">Plus récents</option>
              <option value="students">Nombre d'étudiants</option>
              <option value="rating">Note</option>
              <option value="revenue">Revenus</option>
            </select>
          </div>
        </div>
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
      <button @click="fetchCourses">Réessayer</button>
    </div>

    <!-- Course List -->
    <div v-else-if="filteredCourses.length > 0" class="course-list">
      <article v-for="course in filteredCourses" :key="course.id" class="course-card">
        <!-- Thumbnail -->
        <div class="card-thumb">
          <img
            :src="course.image_url || 'https://placehold.co/400x220/e8eef7/2453a7?text=Cours'"
            :alt="course.title"
          >
          <span
            class="thumb-badge"
            :class="course.status === 'published' ? 'published' : 'draft'"
          >
            {{ course.status === 'published' ? 'Publié' : 'Brouillon' }}
          </span>
        </div>

        <!-- Body -->
        <div class="card-body">
          <div class="card-header-row">
            <span v-if="course.is_free" class="price-badge free">Gratuit</span>
            <span v-else-if="course.price != null" class="price-badge">{{ course.price }} XOF</span>
            <span class="card-date">
              <i class="bi bi-clock"></i> {{ new Date(course.updated_at || course.created_at).toLocaleDateString('fr-FR') }}
            </span>
          </div>

          <h3 class="card-title">{{ course.title }}</h3>
          <p class="card-desc">{{ course.short_description || course.description?.substring(0, 130) + '…' }}</p>

          <div class="card-info-row">
            <span v-if="course.category" class="info-tag">
              <i class="bi bi-tag"></i> {{ course.category }}
            </span>
          </div>

          <div class="card-status-row">
            <label :for="'status-select-' + course.id" class="status-label">Statut :</label>
            <select
              :id="'status-select-' + course.id"
              class="status-select"
              :value="course.status"
              @change="onCourseStatusChange(course.id, $event)"
              :disabled="isLoading"
            >
              <option value="draft">Brouillon</option>
              <option value="published">Publié</option>
            </select>
          </div>
        </div>

        <!-- Side panel -->
        <div class="card-side">
          <RouterLink :to="`/course-editor/${course.id}`" class="btn-action primary">
            <i class="bi bi-pencil"></i> Modifier
          </RouterLink>
          <button
            class="btn-action danger"
            @click="deleteCourse(course.id)"
            :disabled="isLoading"
          >
            <i class="bi bi-trash"></i> Supprimer
          </button>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div v-if="!isLoading && !error && filteredCourses.length === 0" class="empty-state">
      <div class="empty-illustration">
        <i class="bi bi-journal-x"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p>Commencez par créer votre premier cours</p>
      <RouterLink to="/course-editor" class="btn-reset">
        <i class="bi bi-plus-lg"></i> Créer un cours
      </RouterLink>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use "sass:color";

// ─── Palette ────────────────────────────────────
$primary:     #2453a7;
$primary-dark:#1a3f8a;
$primary-soft:#eaf2ff;
$dark:        #1a2332;
$gray:        #6b7280;
$gray-light:  #f4f7fb;
$border:      #dfe8f6;
$radius:      14px;

.professor-courses-page {
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
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.toolbar-title {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;

  h1 {
    font-size: 1.45rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}

.result-count {
  font-size: 0.78rem;
  color: $gray;
  white-space: nowrap;
  strong { color: $primary; font-weight: 700; }
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.1rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s;
  &:hover { background: $primary-dark; color: #fff; }
}

// ─── Stats Strip (compact chips) ────────────────
.stats-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid color.adjust($border, $lightness: 3%);
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.8rem;
  background: $gray-light;
  border: 1px solid $border;
  border-radius: 999px;
  font-size: 0.78rem;
  color: $gray;

  i { font-size: 0.85rem; }
  strong { color: $dark; font-weight: 700; }
}

.toolbar-bottom {
  padding-top: 0.75rem;
  border-top: 1px solid color.adjust($border, $lightness: 3%);
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
    &:focus { border-color: $primary; }
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

  p { color: $gray; font-size: 0.9rem; }
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
    border-color: color.adjust($primary, $lightness: 28%);
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

.thumb-badge {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  border-radius: 8px;
  padding: 0.2rem 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

  &.published { background: #10b981; color: #fff; }
  &.draft     { background: rgba(#fff, 0.95); color: $gray; }
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

.price-badge {
  background: $primary-soft;
  color: $primary;
  border-radius: 6px;
  padding: 0.15rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;

  &.free { background: #dcfce7; color: #15803d; }
}

.card-date {
  font-size: 0.72rem;
  color: $gray;
  i { margin-right: 0.2rem; }
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  line-height: 1.35;
  margin: 0 0 0.3rem;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 0.82rem;
  color: $gray;
  line-height: 1.55;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.info-tag {
  background: $gray-light;
  color: $gray;
  border: 1px solid $border;
  border-radius: 999px;
  padding: 0.12rem 0.55rem;
  font-size: 0.7rem;
  font-weight: 500;
  i { color: $primary; margin-right: 0.2rem; }
}

.card-status-row {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: $dark;
  margin: 0;
}

.status-select {
  border: 1.5px solid $border;
  border-radius: 8px;
  padding: 0.3rem 0.6rem;
  font-size: 0.78rem;
  color: $dark;
  background: $gray-light;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
  &:focus { border-color: $primary; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
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

.btn-action {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem 0.6rem;
  border: none;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s, transform 0.15s;

  &.primary {
    background: $primary;
    color: #fff;
    &:hover { background: $primary-dark; transform: translateY(-1px); color: #fff; }
  }

  &.danger {
    background: #fff;
    color: #dc2626;
    border: 1.5px solid #fecaca;
    &:hover { background: #fef2f2; border-color: #dc2626; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
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
  i { font-size: 2.2rem; color: $primary; }
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
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.3rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s;
  &:hover { background: $primary-dark; color: #fff; }
}

// ─── Responsive ─────────────────────────────────
@media (max-width: 767.98px) {
  .toolbar-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-strip {
    gap: 0.4rem;
  }

  .stat-chip {
    font-size: 0.72rem;
    padding: 0.3rem 0.6rem;
  }

  .toolbar-selects {
    flex-direction: column;
    width: 100%;
    .select-wrap {
      width: 100%;
      select { width: 100%; }
    }
  }

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
    justify-content: center;
  }

  .btn-action { width: auto; flex: 1; min-width: 100px; }
}
</style>