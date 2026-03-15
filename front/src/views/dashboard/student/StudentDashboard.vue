<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useStudentDashboardStore } from '../../../stores/studentDashboardStore'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title } from 'chart.js'
import { Doughnut, Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title)

// Store setup
const studentDashboardStore = useStudentDashboardStore();
const {
  stats,
  enrolledCourses,
  overallProgress,
  weeklyActivity,
  recommendedCourses,
  recentCertificates,
  isLoading,
  error
} = storeToRefs(studentDashboardStore);

// Fetch data on component mount
onMounted(() => {
  studentDashboardStore.loadAllStudentDashboardData();
});

// Chart Options
const progressChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  plugins: {
    legend: {
      display: false,
    },
  },
};

const activityChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: Math.max(5, ... (weeklyActivity.value?.map(a => a.study_hours) || [5])) + 1, // Dynamic max based on data or 5
    },
  },
};

// Computed properties for Chart Data
const computedOverallProgressChartData = computed(() => {
  if (!overallProgress.value) {
    return { labels: [], datasets: [{ data: [] }] };
  }
  return {
    labels: ['Complété', 'En cours'],
    datasets: [
      {
        backgroundColor: ['#2ecc71', '#ecf0f1'],
        data: [
          overallProgress.value.completed_percentage,
          overallProgress.value.in_progress_percentage,
        ],
      },
    ],
  };
});

const computedWeeklyActivityChartData = computed(() => {
  if (!weeklyActivity.value || weeklyActivity.value.length === 0) {
    return { labels: [], datasets: [{ data: [] }] };
  }
  // Ensure consistent order of days for the chart
  const dayOrder = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
  const sortedActivity = [...weeklyActivity.value].sort((a, b) => dayOrder.indexOf(a.day_of_week) - dayOrder.indexOf(b.day_of_week));

  return {
    labels: sortedActivity.map(item => item.day_of_week),
    datasets: [
      {
        label: 'Heures d\'études',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderColor: '#3498db',
        borderWidth: 2,
        data: sortedActivity.map(item => item.study_hours),
        tension: 0.4,
        fill: true,
      },
    ],
  };
});

const getRecommendedImage = (course: any): string => {
  return course?.image_url || `https://picsum.photos/seed/reco-${course?.id || 'x'}/640/360`;
};

const getRecommendedCategory = (course: any): string => {
  return course?.category || 'General';
};

const getRecommendedInstructor = (course: any): string => {
  return course?.instructor_name || 'Formateur';
};

const getRecommendedDuration = (course: any): string => {
  const weeks = Number(course?.duration_weeks || 0);
  return weeks > 0 ? `${weeks} semaines` : 'Duree flexible';
};

</script>

<script lang="ts">
export default {
  name: 'StudentDashboard'
}
</script>

<template>
  <div>
    <!-- Loading and Error States -->
    <div v-if="isLoading" class="alert alert-info">Chargement de votre tableau de bord...</div>
    <div v-if="error" class="alert alert-danger">
      Erreur: {{ error }}
    </div>

    <!-- Stats Cards -->
    <div v-if="!isLoading && stats" class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                <i class="bi bi-book text-primary fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Cours</h6>
                <h3 class="mb-0">{{ stats.enrolled_courses_count ?? 'N/A' }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                <i class="bi bi-award text-success fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Certificats</h6>
                <h3 class="mb-0">{{ stats.certificates_count ?? 'N/A' }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                <i class="bi bi-clock-history text-warning fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Heures d'étude</h6>
                <h3 class="mb-0">{{ stats.total_study_hours ?? 'N/A' }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                <i class="bi bi-graph-up-arrow text-info fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Progrès moyen</h6>
                <h3 class="mb-0">{{ stats.average_progress?.toFixed(0) ?? '0' }}%</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <div v-if="!isLoading && !error" class="row g-4">
      <!-- Left Column - Course List -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Mes cours en cours</h5>
              <RouterLink to="/my-courses" class="btn btn-sm btn-outline-primary">
                Voir tous mes cours
              </RouterLink>
            </div>
          </div>
          <div class="card-body">
            <div v-if="enrolledCourses.length === 0" class="text-center py-4">
              <i class="bi bi-book fs-1 text-muted"></i>
              <p class="mt-3">Vous n'êtes inscrit à aucun cours</p>
              <RouterLink to="/browse-courses" class="btn btn-primary">
                Explorer les cours
              </RouterLink>
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="course in enrolledCourses" :key="course.id" class="list-group-item px-0 py-3">
                <div class="d-flex">
                  <img :src="course.image_url || 'https://placehold.co/400x200?text=Cours'" :alt="course.title" class="rounded me-3" style="width: 100px; height: 60px; object-fit: cover;">
                  <div class="flex-grow-1">
                    <h6 class="mb-1">{{ course.title }}</h6>
                    <div class="d-flex align-items-center mb-2">
                      <div class="progress flex-grow-1" style="height: 8px;">
                        <div 
                          class="progress-bar" 
                          role="progressbar" 
                          :style="{ width: course.progress + '%' }" 
                          :aria-valuenow="course.progress" 
                          aria-valuemin="0" 
                          aria-valuemax="100"
                        ></div>
                      </div>
                      <span class="ms-2 small text-muted">{{ course.progress }}%</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">Dernière activité: {{ new Date(course.last_activity_timestamp).toLocaleDateString() }}</small>
                      <router-link class="btn btn-sm btn-primary" :to="`/course/${course.id}`">
                        Continuer
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommended Courses -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Cours recommandés</h5>
              <RouterLink to="/browse-courses" class="btn btn-sm btn-outline-primary">
                Voir plus
              </RouterLink>
            </div>
          </div>
          <div class="card-body">
            <div v-if="recommendedCourses.length === 0" class="text-center py-4">
                <p>Aucune recommandation pour le moment.</p>
            </div>
            <div v-else class="row g-3">
              <div v-for="course in recommendedCourses" :key="course.id" class="col-md-6">
                <div class="card h-100 shadow-sm recommended-card border-0">
                  <img :src="getRecommendedImage(course)" class="card-img-top recommended-image" :alt="course.title">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title mb-0 pe-2">{{ course.title }}</h6>
                      <span class="badge bg-primary-subtle text-primary-emphasis border border-primary-subtle">
                        {{ getRecommendedCategory(course) }}
                      </span>
                    </div>
                    <p class="card-text small text-muted mb-3">
                      <i class="bi bi-person-circle me-1"></i> {{ getRecommendedInstructor(course) }}<br>
                      <i class="bi bi-clock me-1"></i> {{ getRecommendedDuration(course) }}
                    </p>
                    <RouterLink :to="`/course/${course.id}`" class="btn btn-sm btn-outline-primary w-100">
                      Voir le cours
                    </RouterLink>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Stats and Activities -->
      <div class="col-lg-4">
        <!-- Progress Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Progression globale</h5>
          </div>
          <div class="card-body">
            <div v-if="overallProgress" class="position-relative" style="height: 200px;">
              <Doughnut 
                :data="computedOverallProgressChartData"
                :options="progressChartOptions"
              />
              <div class="position-absolute top-50 start-50 translate-middle text-center">
                <h3 class="mb-0">{{ overallProgress.completed_percentage?.toFixed(0) ?? '0' }}%</h3>
                <span class="text-muted small">Complété</span>
              </div>
            </div>
            <div v-else class="text-center text-muted p-3">
                Données de progression non disponibles.
            </div>
          </div>
        </div>

        <!-- Activity Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Activité hebdomadaire</h5>
          </div>
          <div class="card-body">
            <div v-if="weeklyActivity.length > 0" style="height: 200px;">
              <Line 
                :data="computedWeeklyActivityChartData"
                :options="activityChartOptions"
              />
            </div>
            <div v-else class="text-center text-muted p-3">
                Aucune activité enregistrée cette semaine.
            </div>
          </div>
        </div>

        <!-- Recent Certificates -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Certificats récents</h5>
              <RouterLink to="/certificates" class="btn btn-sm btn-outline-primary" v-if="recentCertificates.length">
                Tous mes certificats
              </RouterLink>
            </div>
          </div>
          <div class="card-body">
            <div v-if="recentCertificates.length === 0" class="text-center py-4">
                <p>Aucun certificat obtenu récemment.</p>
            </div>
            <div v-else>
              <div v-for="certificate in recentCertificates" :key="certificate.id" class="d-flex align-items-center p-3 mb-2 border rounded bg-light">
                <div class="flex-shrink-0 me-3">
                  <i class="bi bi-award-fill text-warning fs-1"></i>
                </div>
                <div>
                  <h6 class="mb-1">{{ certificate.course_name }}</h6>
                  <p class="mb-0 small text-muted">Obtenu le {{ new Date(certificate.date_obtained).toLocaleDateString() }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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

.progress {
  background-color: #e9ecef;
}

.progress-bar {
  background-color: #2ecc71;
}

.recommended-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recommended-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.75rem 1.5rem rgba(0, 0, 0, 0.08) !important;
}

.recommended-image {
  height: 150px;
  object-fit: cover;
}
</style>