<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useProfessorDashboardStore } from '../../../stores/professorDashboardStore'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title } from 'chart.js'
import { Doughnut, Bar } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title)

// Store setup
const professorDashboardStore = useProfessorDashboardStore();
const {
  stats,
  publishedCourses,
  studentEngagement,
  studentDistribution,
  recentActivities,
  isLoading,
  error
} = storeToRefs(professorDashboardStore);

// Fetch data on component mount
onMounted(() => {
  professorDashboardStore.loadAllProfessorDashboardData();
});

// Chart options (can remain mostly static or be made dynamic if needed)
const studentDistributionOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
    },
  },
};

const engagementChartOptions = {
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
    },
  },
};

// Computed property for Student Distribution Chart
const computedStudentDistributionChartData = computed(() => {
  if (!studentDistribution.value) {
    return { labels: [], datasets: [{ data: [] }] };
  }
  return {
    labels: ['Actifs', 'Inactifs', 'Terminés'],
    datasets: [
      {
        backgroundColor: ['#2ecc71', '#f39c12', '#3498db'],
        data: [
          studentDistribution.value.active_students_count,
          studentDistribution.value.inactive_students_count,
          studentDistribution.value.completed_students_count,
        ],
      },
    ],
  };
});

// Computed property for Engagement Chart (Bar chart)
const computedEngagementChartData = computed(() => {
  if (!studentEngagement.value || studentEngagement.value.length === 0) {
    return { labels: [], datasets: [{ data: [] }] };
  }
  return {
    labels: studentEngagement.value.map(item => item.course_name),
    datasets: [
      {
        label: 'Heures moyennes par étudiant',
        backgroundColor: ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c'], // Add more colors if more courses
        data: studentEngagement.value.map(item => item.average_hours_spent),
      },
    ],
  };
});

</script>

<template>
  <div>
    <!-- Loading and Error States -->
    <div v-if="isLoading" class="alert alert-info">Chargement des données du tableau de bord...</div>
    <div v-if="error" class="alert alert-danger">
      Erreur lors du chargement des données: {{ error }}
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
                <h6 class="mb-0 text-muted">Cours publiés</h6>
                <h3 class="mb-0">{{ stats.published_courses_count ?? 'N/A' }}</h3>
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
                <i class="bi bi-people text-success fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Étudiants</h6>
                <h3 class="mb-0">{{ stats.total_students_count ?? 'N/A' }}</h3>
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
                <i class="bi bi-star text-warning fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Note moyenne</h6>
                <h3 class="mb-0">{{ stats.average_rating?.toFixed(1) ?? 'N/A' }}</h3>
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
                <i class="bi bi-chat-dots text-info fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Questions</h6>
                <h3 class="mb-0">{{ stats.total_questions_count ?? 'N/A' }}</h3>
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
              <h5 class="mb-0">Mes cours publiés</h5>
              <div>
                <RouterLink to="/manage-courses" class="btn btn-sm btn-outline-primary me-2">
                  Gérer mes cours
                </RouterLink>
                <RouterLink to="/course-editor" class="btn btn-sm btn-primary">
                  <i class="bi bi-plus"></i> Ajouter un cours
                </RouterLink>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="publishedCourses.length === 0" class="text-center py-4">
              <i class="bi bi-book fs-1 text-muted"></i>
              <p class="mt-3">Vous n'avez pas encore publié de cours</p>
              <RouterLink to="/course-editor" class="btn btn-primary">
                Créer un cours
              </RouterLink>
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="course in publishedCourses" :key="course.id" class="list-group-item px-0 py-3">
                <div class="d-flex">
                  <!-- Assuming course.image_url exists from CoursePerformance type -->
                  <img :src="(course as any).image_url || 'https://placehold.co/400x200?text=Cours'" alt="Course Image" class="rounded me-3" style="width: 100px; height: 60px; object-fit: cover;">
                  <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start">
                      <h6 class="mb-1">{{ course.title }}</h6>
                      <span class="badge bg-success d-flex align-items-center">
                        <i class="bi bi-star-fill me-1"></i>
                        {{ course.rating.toFixed(1) }}
                      </span>
                    </div>
                    <div class="d-flex flex-wrap mb-2">
                      <span class="me-3 small text-muted">
                        <i class="bi bi-people me-1"></i> {{ course.students_count }} étudiants
                      </span>
                      <span class="small text-muted">
                        <i class="bi bi-calendar me-1"></i> Mis à jour le {{ new Date(course.last_updated).toLocaleDateString() }}
                      </span>
                    </div>
                    <div class="d-flex">
                      <RouterLink :to="`/course-editor/${course.id}`" class="btn btn-sm btn-outline-primary me-2">
                        Modifier
                      </RouterLink>
                      <button class="btn btn-sm btn-outline-secondary">
                        Statistiques
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activities -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Activités récentes</h5>
          </div>
          <div class="card-body">
             <div v-if="recentActivities.length === 0" class="text-center py-4">
              <p class="mt-3">Aucune activité récente à afficher.</p>
            </div>
            <div v-else class="list-group list-group-flush">
              <div v-for="activity in recentActivities" :key="activity.id" class="list-group-item px-0 py-3">
                <div class="d-flex">
                  <div class="flex-shrink-0 me-3">
                    <div v-if="activity.activity_type === 'question'" class="rounded-circle bg-warning bg-opacity-10 p-3">
                      <i class="bi bi-question-circle text-warning"></i>
                    </div>
                    <div v-else class="rounded-circle bg-info bg-opacity-10 p-3">
                      <i class="bi bi-chat-dots text-info"></i>
                    </div>
                  </div>
                  <div>
                    <h6 class="mb-1">{{ activity.student_name }}</h6>
                    <p class="mb-1">
                      <span v-if="activity.activity_type === 'question'" class="badge bg-warning text-dark me-2">Question</span>
                      <span v-else class="badge bg-info text-dark me-2">Commentaire</span>
                      {{ activity.content }}
                    </p>
                    <div class="d-flex align-items-center text-muted small">
                      <span class="me-3">{{ activity.course_name }}</span>
                      <span>{{ new Date(activity.timestamp).toLocaleString() }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Stats and Charts -->
      <div class="col-lg-4">
        <!-- Student Distribution Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Répartition des étudiants</h5>
          </div>
          <div class="card-body">
            <div v-if="studentDistribution" style="height: 200px;">
              <Doughnut 
                :data="computedStudentDistributionChartData"
                :options="studentDistributionOptions"
              />
            </div>
            <div v-else class="text-center text-muted p-3">
              Données de répartition non disponibles.
            </div>
          </div>
        </div>

        <!-- Engagement Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Engagement par cours</h5>
          </div>
          <div class="card-body">
            <div v-if="studentEngagement.length > 0" style="height: 250px;">
              <Bar 
                :data="computedEngagementChartData"
                :options="engagementChartOptions"
              />
            </div>
            <div v-else class="text-center text-muted p-3">
              Données d'engagement non disponibles.
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Actions rapides</h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <RouterLink to="/course-editor" class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i> Créer un nouveau cours
              </RouterLink>
              <button class="btn btn-outline-primary">
                <i class="bi bi-chat-dots me-2"></i> Répondre aux questions
              </button>
              <button class="btn btn-outline-primary">
                <i class="bi bi-graph-up me-2"></i> Voir les statistiques complètes
              </button>
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
</style>