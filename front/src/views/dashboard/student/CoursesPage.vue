<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { getMyEnrolledCourses, getMyCourseEnrollmentProgress } from '../../../services/api/course';
import type { Course } from '../../../types/api';

// Define an extended type for courses with their specific progress
type CourseWithProgress = Course & { studentProgressPercentage?: number };

const courses = ref<CourseWithProgress[]>([]);
const isLoading = ref(true); // Set to true initially
const error = ref<string | null>(null);
// Optional: const isFetchingProgress = ref(false); // If you want a separate indicator

// Filter options
const filters = ref({
  status: 'all', // all, in-progress, completed
  sort: 'recent', // recent, progress, alphabetical
});

const fetchMyCoursesAndProgress = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const baseCourses = await getMyEnrolledCourses();
    const enrichedCourses: CourseWithProgress[] = [];

    // isFetchingProgress.value = true; // If using a separate loading state for progress part
    for (const course of baseCourses) {
      let progressPercentage = course.progress; // Use existing progress from course object as a fallback
      try {
        const enrollmentProgress = await getMyCourseEnrollmentProgress(course.id);
        if (enrollmentProgress) {
          progressPercentage = enrollmentProgress.progress_percentage;
        }
      } catch (progressError) {
        console.warn(`Failed to fetch progress for course ${course.id}:`, progressError);
        // If fetching progress fails, use course.progress or default to 0
        if (progressPercentage === undefined || progressPercentage === null) progressPercentage = 0;
      }
      enrichedCourses.push({ ...course, studentProgressPercentage: progressPercentage });
    }
    courses.value = enrichedCourses;
    // isFetchingProgress.value = false;

  } catch (err: any) {
    console.error('Failed to fetch enrolled courses or their progress:', err);
    error.value = err.message || 'Erreur lors du chargement de vos cours et de leur progression.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchMyCoursesAndProgress();
});

// Computed courses based on filters
const filteredCourses = computed(() => {
  let filtered = [...courses.value];
  
  // Apply status filter
  if (filters.value.status === 'in-progress') {
    filtered = filtered.filter(course => (course.studentProgressPercentage ?? 0) < 100);
  } else if (filters.value.status === 'completed') {
    filtered = filtered.filter(course => (course.studentProgressPercentage ?? 0) === 100);
  }
  
  // Apply sorting
  switch (filters.value.sort) {
    case 'progress':
      filtered.sort((a, b) => (b.studentProgressPercentage ?? 0) - (a.studentProgressPercentage ?? 0));
      break;
    case 'alphabetical':
      filtered.sort((a, b) => a.title.localeCompare(b.title));
      break;
    default: // recent (using updated_at, assuming it reflects recent activity)
      filtered.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  }
  
  return filtered;
});
</script>

<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">Mes Cours</h1>
            <p class="text-muted mb-0">Gérez et suivez vos cours en cours</p>
          </div>
          <RouterLink to="/browse-courses" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Explorer les cours
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Loading and Error States -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p>Chargement de vos cours...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Statut</label>
                <select v-model="filters.status" class="form-select">
                  <option value="all">Tous les cours</option>
                  <option value="in-progress">En cours</option>
                  <option value="completed">Terminés</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Trier par</label>
                <select v-model="filters.sort" class="form-select">
                  <option value="recent">Plus récents</option>
                  <option value="progress">Progression</option>
                  <option value="alphabetical">Ordre alphabétique</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Course List -->
    <div v-if="filteredCourses.length > 0" class="row g-4">
      <div v-for="course in filteredCourses" :key="course.id" class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <img :src="course.image_url || 'https://placehold.co/400x200?text=Image+Indisponible'" class="card-img-top" :alt="course.title" style="height: 200px; object-fit: cover;">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title mb-0">{{ course.title }}</h5>
              <span
                :class="['badge', course.status === 'published' ? 'bg-success' : 'bg-secondary']"
                style="font-size: 0.75rem;"
              >
                {{ course.status === 'published' ? 'Publié' : 'Brouillon' }}
              </span>
            </div>
            <p class="card-text text-muted small mb-3">{{ course.short_description || course.description?.substring(0,100) + '...' }}</p>
            
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-light p-2 me-2">
                <i class="bi bi-person-circle text-primary"></i>
              </div>
              <span>{{ course.instructor.name }}</span> <!-- Updated to course.instructor.name -->
            </div>
            
            <div class="progress mb-3" style="height: 8px;">
              <div 
                class="progress-bar" 
                role="progressbar" 
                :style="{ width: (course.studentProgressPercentage ?? 0) + '%' }"
                :aria-valuenow="(course.studentProgressPercentage ?? 0)"
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
            
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="text-muted">Progression: {{ course.studentProgressPercentage ?? 0 }}%</span>
              <!-- totalLessons and completedLessons are not available on Course type -->
              <!-- <span class="text-muted">{{ course.completedLessons }}/{{ course.totalLessons }} leçons</span> -->
            </div>
            
            <!-- nextLesson is not available on Course type -->
            <!--
            <div class="mb-3">
              <small class="text-muted d-block">Prochaine leçon:</small>
              <strong>{{ course.nextLesson }}</strong>
            </div>
            -->
            
            <div class="d-flex justify-content-between align-items-center">
              <small class="text-muted">
                <!-- lastActivity is not available, using updated_at -->
                Dernière activité: {{ new Date(course.updated_at).toLocaleDateString() }}
              </small>
              <router-link class="btn btn-primary" :to="{ name: 'course-detail', params: { id: course.id } }">
                Continuer
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-journal-x display-1 text-muted"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p class="text-muted">Ajustez vos filtres ou explorez notre catalogue de cours</p>
      <RouterLink to="/browse-courses" class="btn btn-primary">
        Explorer les cours
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.progress-bar {
  background-color: var(--bs-primary);
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>