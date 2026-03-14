<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getAllCourses, enrollInCourse } from '../../../services/api/course';
import type { Course } from '../../../types/api';
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
    courses.value = await getAllCourses({ status: 'published' });
  } catch (err: any) {
    console.error('Failed to fetch courses:', err);
    error.value = err.message || 'Erreur lors du chargement des cours.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchAllPublishedCourses();
});

// Computed filtered courses
const filteredCourses = computed(() => {
  return courses.value.filter(course => {
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

const enrollCourse = async (courseId: number) => {
  try {
    await enrollInCourse(courseId);
    alert('Inscription réussie! Vous pouvez retrouver ce cours dans "Mes Cours".');
    router.push('/my-courses');
  } catch (err: any) {
    console.error('Failed to enroll in course:', err);
    alert(err.response?.data?.detail || err.message || 'Erreur lors de l\'inscription.');
    router.push('/my-courses');
  }
};
</script>

<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-1">Explorer les Cours</h1>
        <p class="text-muted mb-0">Découvrez notre catalogue de formations professionnelles</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <!-- Search -->
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text bg-transparent">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    v-model="filters.search"
                    placeholder="Rechercher un cours..."
                  >
                </div>
              </div>

              <!-- Category Filter -->
              <div class="col-md-6">
                <select v-model="filters.category" class="form-select">
                  <option v-for="category in categories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
              </div>

              <!-- Level Filter -->
              <div class="col-md-6">
                <select v-model="filters.level" class="form-select">
                  <option value="all">Tous les niveaux</option>
                  <option value="Débutant">Débutant</option>
                  <option value="Intermédiaire">Intermédiaire</option>
                  <option value="Avancé">Avancé</option>
                </select>
              </div>

              <!-- Price Range Filter -->
              <div class="col-md-6">
                <select v-model="filters.priceRange" class="form-select">
                  <option value="all">Tous les prix</option>
                  <option value="free">Gratuit</option>
                  <option value="under-100">Moins de 100XOF</option>
                  <option value="100-200">100XOF - 200XOF</option>
                  <option value="over-200">Plus de 200XOF</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading and Error States -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p>Chargement des cours...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <!-- Course Grid -->
    <div v-else-if="filteredCourses.length > 0" class="row g-4">
      <div v-for="course in filteredCourses" :key="course.id" class="col-md-6 col-lg-4">
        <div class="card h-100 border-0 shadow-sm">
          <img :src="course.image_url || 'https://placehold.co/400x200?text=Image+Indisponible'" class="card-img-top" :alt="course.title" style="height: 200px; object-fit: cover;">
          <div class="card-body d-flex flex-column">
            <div>
              <!-- Category, Rating, Reviews are removed as they are not in Course API type -->
              <!-- <span class="badge bg-primary mb-2">{{ (course as any).category || 'N/A' }}</span> -->
              <h5 class="card-title mb-2">{{ course.title }}</h5>
              <p class="card-text text-muted small mb-2">{{ course.short_description || course.description?.substring(0, 100) + '...' }}</p>
            </div>

            <div class="mt-auto">
              <div class="d-flex align-items-center mb-2">
                <div class="rounded-circle bg-light p-2 me-2">
                  <i class="bi bi-person-circle text-primary"></i>
                </div>
                <span>{{ course.instructor.name }}</span>
              </div>

              <!-- Categorie and objectives (3 and ... if is more)  -->
              <div class="mb-3">
                <div class="d-flex align-items-center">
                  <i class="bi bi-bookmark me-2 text-muted"></i>
                  <span>{{ (course as any).category || 'N/A' }}</span>
                </div><br>
                <div class="d-flex align-items-center">
                   <span class="badge bg-info me-1" v-for="objective in course.objectives.slice(0, 3)" :key="objective">
                    {{ objective }}
                   </span>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center">
                <div class="h5 mb-0">
                  <span v-if="course.is_free" class="badge bg-success">Gratuit</span>
                  <span v-else-if="course.price != null">{{ course.price }} XOF</span>
                  <span v-else class="badge bg-secondary">Prix N/A</span>
                </div>
                <RouterLink :to="`/course/${course.id}`" class="btn btn-outline-primary btn-sm">
                  Voir détails
                </RouterLink>
                <button
                  class="btn btn-primary btn-sm"
                  @click="enrollCourse(course.id)"
                >
                  S'inscrire
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-search display-1 text-muted"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p class="text-muted">Essayez de modifier vos critères de recherche</p>
      <button
        class="btn btn-primary"
        @click="filters = { category: 'Tous', search: '', level: 'all', priceRange: 'all' }"
      >
        Réinitialiser les filtres
      </button>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.badge {
  padding: 0.5rem 1rem;
}

</style>