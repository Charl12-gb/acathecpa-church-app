<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useAuthStore } from '../../stores/auth'

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
const userRole = computed(() => currentUser.value?.role || '')

// Show appropriate dashboard based on user role
const showDashboard = computed(() => {
  if (userRole.value === 'admin' || userRole.value === 'super_admin') {
    return 'admin'
  } else if (userRole.value === 'professor') {
    return 'professor'
  } else {
    return 'student'
  }
})
</script>

<template>
  <div class="container py-5">
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-0">Tableau de bord</h1>
        <p class="text-muted">
          Bienvenue, {{ currentUser?.name }} !
        </p>
      </div>
    </div>

    <!-- Student Dashboard -->
    <StudentDashboard v-if="showDashboard === 'student'" />
    
    <!-- Professor Dashboard -->
    <ProfessorDashboard v-else-if="showDashboard === 'professor'" />
    
    <!-- Admin Dashboard -->
    <AdminDashboard v-else-if="showDashboard === 'admin'" />
  </div>
</template>