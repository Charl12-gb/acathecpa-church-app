<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia' 
import { useAdminDashboardStore } from '../../../stores/adminDashboardStore'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title } from 'chart.js'
import { Doughnut, Line } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title)

// Store setup
const adminDashboardStore = useAdminDashboardStore();
const {
  stats,
  professors,
  recentActivities,
  userDistribution,
  monthlyRegistrations,
  isLoading,
  error
} = storeToRefs(adminDashboardStore);

onMounted(() => {
  adminDashboardStore.loadAllAdminDashboardData();
});

const computedUserDistributionChartData = computed(() => {
  if (!userDistribution.value) {
    return { labels: [], datasets: [{ data: [] }] };
  }
  return {
    labels: ['Étudiants', 'Professeurs', 'Admins'],
    datasets: [
      {
        backgroundColor: ['#3498db', '#2ecc71', '#e74c3c'],
        data: [
          userDistribution.value.students_count,
          userDistribution.value.professors_count,
          userDistribution.value.admins_count,
        ],
      },
    ],
  };
});

const userDistributionOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
    },
  },
};

const computedRegistrationChartData = computed(() => {
  if (!monthlyRegistrations.value || monthlyRegistrations.value.length === 0) {
    return { labels: [], datasets: [{ data: [] }] }; 
  }
  return {
    labels: monthlyRegistrations.value.map(item => item.month),
    datasets: [
      {
        label: 'Nouvelles inscriptions',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderColor: '#3498db',
        borderWidth: 2,
        data: monthlyRegistrations.value.map(item => item.count),
        tension: 0.4,
        fill: true,
      },
    ],
  };
});

const registrationOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const, // Added 'as const' for type safety
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

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
                <i class="bi bi-people text-primary fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Utilisateurs</h6>
                <h3 class="mb-0">{{ stats.total_users ?? 'N/A' }}</h3>
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
                <i class="bi bi-person-workspace text-success fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Professeurs</h6>
                <h3 class="mb-0">{{ stats.total_professors ?? 'N/A' }}</h3>
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
                <i class="bi bi-book text-warning fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Cours total</h6>
                <h3 class="mb-0">{{ stats.total_courses ?? 'N/A' }}</h3>
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
                <h6 class="mb-0 text-muted">Nouv. inscriptions</h6>
                <h3 class="mb-0">{{ stats.new_enrollments_last_month ?? 'N/A' }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <div v.if="!isLoading && !error" class="row g-4">
      <!-- Left Column -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Professeurs</h5>
              <div>
                <RouterLink to="/manage-professors" class="btn btn-sm btn-outline-primary me-2">
                  Gérer les professeurs
                </RouterLink>
                <RouterLink to="/professor-form" class="btn btn-sm btn-primary">
                  <i class="bi bi-plus"></i> Ajouter
                </RouterLink>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="professors.length === 0" class="text-center text-muted p-3">
              Aucun professeur à afficher.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th scope="col">Nom</th>
                    <th scope="col">Email</th>
                    <th scope="col">Cours</th>
                    <th scope="col">Étudiants</th>
                    <th scope="col">Évaluation</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="professor in professors" :key="professor.id">
                    <td>{{ professor.name }}</td>
                    <td>{{ professor.email }}</td>
                    <td>{{ professor.courses_count }}</td>
                    <td>{{ professor.students_count }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <span class="me-2">{{ professor.average_rating.toFixed(1) }}</span>
                        <div class="text-warning">
                          <i class="bi bi-star-fill"></i>
                        </div>
                      </div>
                    </td>
                    <td>
                      <RouterLink :to="`/professor-form/${professor.id}`" class="btn btn-sm btn-outline-primary me-1">
                        <i class="bi bi-pencil"></i>
                      </RouterLink>
                      <button class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Recent Activities -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Activités récentes</h5>
          </div>
          <div class="card-body">
            <div v-if="recentActivities.length === 0" class="text-center text-muted p-3">
              Aucune activité récente.
            </div>
            <div v-else class="list-group list-group-flush">
              <div v-for="activity in recentActivities" :key="activity.id" class="list-group-item px-0 py-3">
                <div class="d-flex align-items-center">
                  <div class="flex-shrink-0 me-3">
                    <div class="rounded-circle bg-light p-3">
                      <i class="bi bi-activity text-primary"></i>
                    </div>
                  </div>
                  <div>
                    <h6 class="mb-1">{{ activity.user_name }}</h6>
                    <p class="mb-0 text-muted">
                      {{ activity.action }} <strong>{{ activity.resource_name }}</strong>
                    </p>
                    <small class="text-muted">{{ new Date(activity.timestamp).toLocaleString() }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="col-lg-4">
        <!-- User Distribution Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Répartition des utilisateurs</h5>
          </div>
          <div class="card-body">
            <div v-if="userDistribution" style="height: 250px;">
              <Doughnut 
                :data="computedUserDistributionChartData"
                :options="userDistributionOptions"
              />
            </div>
            <div v-else class="text-center text-muted p-3">
              Données de répartition non disponibles.
            </div>
          </div>
        </div>

        <!-- Registration Chart -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Nouvelles inscriptions</h5>
          </div>
          <div class="card-body">
            <div v-if="monthlyRegistrations.length > 0" style="height: 250px;">
              <Line 
                :data="computedRegistrationChartData"
                :options="registrationOptions"
              />
            </div>
             <div v-else class="text-center text-muted p-3">
              Données d'inscription non disponibles.
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
              <RouterLink to="/professor-form" class="btn btn-primary">
                <i class="bi bi-person-plus me-2"></i> Ajouter un professeur
              </RouterLink>
              <button class="btn btn-outline-primary">
                <i class="bi bi-gear me-2"></i> Paramètres du système
              </button>
              <button class="btn btn-outline-primary">
                <i class="bi bi-file-earmark-text me-2"></i> Générer des rapports
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