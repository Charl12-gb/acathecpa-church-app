<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { UserRole } from '../../types/api/userTypes'

// Components
const StudentDashboard = defineAsyncComponent(
  () => import('../dashboard/student/StudentDashboard.vue') as any
)
const ProfessorDashboard = defineAsyncComponent(
  () => import('../dashboard/professor/ProfessorDashboard.vue') as any
)
const AdminDashboard = defineAsyncComponent(
  () => import('../dashboard/admin/AdminDashboard.vue') as any
)

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

// Hiérarchie : admin > professor > student
const showAdmin = computed(() => authStore.hasMinRole(UserRole.ADMIN))
const showProfessor = computed(() => authStore.hasMinRole(UserRole.PROFESSOR))
const showStudent = computed(() => authStore.hasMinRole(UserRole.STUDENT))

// Onglet actif par défaut = le rôle le plus élevé de l'utilisateur
const activeTab = computed(() => {
  if (showAdmin.value) return 'admin'
  if (showProfessor.value) return 'professor'
  return 'student'
})
</script>

<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-0">Tableau de bord</h1>
        <p class="text-muted">
          Bienvenue, {{ currentUser?.name }} !
        </p>
      </div>
    </div>

    <!-- Onglets de navigation si l'utilisateur a accès à plusieurs espaces -->
    <ul v-if="showProfessor" class="nav nav-tabs mb-4">
      <li v-if="showAdmin" class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'admin' }" data-bs-toggle="tab" href="#tab-admin" role="tab">
          <i class="bi bi-shield-lock me-1"></i> Administration
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'professor' }" data-bs-toggle="tab" href="#tab-professor" role="tab">
          <i class="bi bi-person-workspace me-1"></i> Professeur
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'student' }" data-bs-toggle="tab" href="#tab-student" role="tab">
          <i class="bi bi-mortarboard me-1"></i> Étudiant
        </a>
      </li>
    </ul>

    <!-- Contenu des onglets -->
    <div v-if="showProfessor" class="tab-content">
      <div v-if="showAdmin" id="tab-admin" class="tab-pane fade" :class="{ 'show active': activeTab === 'admin' }" role="tabpanel">
        <AdminDashboard />
      </div>
      <div id="tab-professor" class="tab-pane fade" :class="{ 'show active': activeTab === 'professor' }" role="tabpanel">
        <ProfessorDashboard />
      </div>
      <div id="tab-student" class="tab-pane fade" :class="{ 'show active': activeTab === 'student' }" role="tabpanel">
        <StudentDashboard />
      </div>
    </div>

    <!-- Student only (pas d'onglets nécessaires) -->
    <StudentDashboard v-if="!showProfessor && showStudent" />
  </div>
</template>