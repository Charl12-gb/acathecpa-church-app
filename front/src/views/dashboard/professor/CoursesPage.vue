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
    // The fetchedCourses should already conform to the updated Course type,
    // which includes status, price, is_free, image_url etc.
    // Mocking for UI elements not yet on backend model.
    courses.value = fetchedCourses?.map(course => ({
      ...course, // Spread the actual course data first
      students: (course as any).students || 0, // Keep mocks for now if template uses them
      rating: (course as any).rating || 0,
      revenue: (course as any).revenue || 0,
      lastUpdated: course.updated_at || course.created_at,
      completionRate: course.progress || 0,
      monthlyEnrollments: (course as any).monthlyEnrollments || [0,0,0,0,0,0]
    }));
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
      filtered.sort((a, b) => (b.students || 0) - (a.students || 0)) // Use default if undefined
      break
    case 'rating':
      filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0))
      break
    case 'revenue':
      filtered.sort((a, b) => (b.revenue || 0) - (a.revenue || 0))
      break
    default: // recent (using updated_at or created_at)
      filtered.sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
  }
  
  return filtered
})

// Chart data for enrollments
const getEnrollmentChartData = (course: any) => { // course type should be Course, but monthlyEnrollments is mocked
  return {
    labels: ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin'], // Generic labels
    datasets: [
      {
        label: 'Inscriptions',
        data: course.monthlyEnrollments || [0,0,0,0,0,0], // Use mocked data or remove chart if not available
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

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
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">Mes Cours</h1>
            <p class="text-muted mb-0">Gérez vos cours et leur contenu</p>
          </div>
          <RouterLink to="/course-editor" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Créer un cours
          </RouterLink>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p>Chargement des cours...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-else>
      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                  <i class="bi bi-book text-primary fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Total des cours</h6>
                  <h3 class="mb-0">{{ courses.length }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                  <i class="bi bi-people text-success fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Étudiants</h6>
                  <!-- Note: 'students' might not be available on Course type from API -->
                  <h3 class="mb-0">{{ courses.reduce((sum, course) => sum + (course.students || 0), 0) }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                  <i class="bi bi-star text-warning fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Note moyenne</h6>
                  <!-- Note: 'rating' might not be available -->
                  <h3 class="mb-0">
                    {{
                      (courses.reduce((sum, course) => sum + (course.rating || 0), 0) /
                      (courses.filter(c => (c.rating || 0) > 0).length || 1)).toFixed(1)
                    }}
                  </h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                  <i class="bi bi-currency-euro text-info fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Revenus totaux</h6>
                  <!-- Note: 'revenue' might not be available -->
                  <h3 class="mb-0">{{ courses.reduce((sum, course) => sum + (course.revenue || 0), 0) }}XOF</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                  <i class="bi bi-people text-success fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Étudiants</h6>
                  <h3 class="mb-0">{{ courses.reduce((sum, course) => sum + (course.students || 0), 0) }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                  <i class="bi bi-star text-warning fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Note moyenne</h6>
                  <h3 class="mb-0">
                    {{ 
                      (courses.reduce((sum, course) => sum + (course.rating || 0), 0) /
                      (courses.filter(c => (c.rating || 0) > 0).length || 1)).toFixed(1)
                    }}
                  </h3>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                  <i class="bi bi-currency-euro text-info fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Revenus totaux</h6>
                  <h3 class="mb-0">{{ courses.reduce((sum, course) => sum + (course.revenue || 0), 0) }}XOF</h3>
                </div>
              </div>
            </div>
          </div>
        </div> -->
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <select v-model="filters.status" class="form-select">
                  <option value="all">Tous les statuts</option>
                  <option value="published">Publiés</option>
                  <option value="draft">Brouillons</option>
                </select>
              </div>
              <div class="col-md-6">
                <select v-model="filters.sort" class="form-select">
                  <option value="recent">Plus récents</option>
                  <option value="students">Nombre d'étudiants</option>
                  <option value="rating">Note</option>
                  <option value="revenue">Revenus</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Course List -->
    <div class="row g-4">
      <div v-for="course in filteredCourses" :key="course.id" class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row">
              <div class="col-md-3">
                <img 
                  :src="course.image_url || 'https://placehold.co/400x200?text=Image+Indisponible'"
                  :alt="course.title"
                  class="img-fluid rounded mb-3 mb-md-0"
                  style="width: 100%; height: 150px; object-fit: cover;"
                >
              </div>
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-1">
                  <h5 class="mb-0 me-2">{{ course.title }}</h5>
                  <span 
                    :class="[
                      'badge',
                      course.status === 'published' ? 'bg-success' : 'bg-secondary'
                    ]"
                  >
                    {{ course.status === 'published' ? 'Publié' : 'Brouillon' }}
                  </span>
                </div>
                <p class="text-muted small mb-2">{{ course.short_description || course.description?.substring(0,100) + '...' }}</p>

                <div class="d-flex flex-wrap gap-2 mb-2 small">
                  <span v-if="course.is_free" class="badge bg-info">Gratuit</span>
                  <span v-else-if="course.price != null" class="badge bg-primary">Prix: {{ course.price }}XOF</span>
                  <span class="text-muted">Categorie: {{ course.category }}</span>
                  <span class="text-muted">Mis à jour: {{ new Date(course.updated_at || course.created_at).toLocaleDateString() }}</span>
                </div>

                <div>
                  <label :for="'status-select-' + course.id" class="form-label form-label-sm me-2">Changer statut:</label>
                  <select
                    :id="'status-select-' + course.id"
                    class="form-select form-select-sm d-inline-block"
                    style="width: auto;"
                    :value="course.status"
                    @change="updateCourseStatus(course.id, ($event.target as HTMLSelectElement).value as CourseStatus)"
                    :disabled="isLoading"
                  >
                    <option value="draft">Brouillon</option>
                    <option value="published">Publié</option>
                  </select>
                </div>

              </div>
              <div class="col-md-3 d-flex flex-column align-items-end justify-content-center">
                <RouterLink
                  :to="`/course-editor/${course.id}`"
                  class="btn btn-sm btn-outline-primary mb-2 w-100"
                >
                  <i class="bi bi-pencil me-1"></i>Modifier
                </RouterLink>
                <button
                  class="btn btn-sm btn-outline-danger w-100"
                  @click="deleteCourse(course.id)"
                  :disabled="isLoading"
                >
                  <i class="bi bi-trash me-1"></i>Supprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredCourses.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-journal-x display-1 text-muted"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p class="text-muted">Commencez par créer votre premier cours</p>
      <RouterLink to="/course-editor" class="btn btn-primary">
        Créer un cours
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.rounded-circle {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  padding: 0.5rem 1rem;
}

.progress-bar {
  background-color: var(--bs-primary);
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}
</style>