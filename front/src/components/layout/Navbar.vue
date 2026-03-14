<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { APP_NAME } from '../../config'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.user)

const handleLogout = () => {
  authStore.logout()
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: '#FFF8EE';">
    <div class="container">
      <RouterLink class="navbar-brand fw-bold text-dark" to="/">{{ APP_NAME }}</RouterLink>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarContent"
        aria-controls="navbarContent" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <RouterLink class="nav-link text-dark" to="/">Accueil</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link text-dark" to="/articles">Articles</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link text-dark" to="/podcasts">Podcasts</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link text-dark" to="/contact">Nous Contacter</RouterLink>
          </li>
        </ul>

        <!-- Not authenticated -->
        <div v-if="!isAuthenticated" class="d-flex">
          <RouterLink to="/login" class="btn btn-outline-light me-2">Connexion</RouterLink>
          <RouterLink to="/register" class="btn btn-light">Inscription</RouterLink>
        </div>

        <!-- Authenticated -->
        <div v-else class="dropdown">
          <button 
            class="btn btn-outline-light dropdown-toggle" 
            type="button" 
            id="userDropdown" 
            data-bs-toggle="dropdown" 
            aria-expanded="false"
          >
            <i class="bi bi-person-circle me-1"></i>
            {{ currentUser?.name }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
            <li><RouterLink class="dropdown-item" to="/dashboard">Tableau de bord</RouterLink></li>
            <li><RouterLink class="dropdown-item" to="/profile">Mon profil</RouterLink></li>
            <li><RouterLink class="dropdown-item" to="/my-content">Mes contenus</RouterLink></li>
            
            <!-- Student specific -->
            <template v-if="currentUser?.role === 'student'">
              <li><RouterLink class="dropdown-item" to="/my-courses">Mes cours</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/certificates">Mes certificats</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/browse-courses">Explorer les cours</RouterLink></li>
            </template>
            
            <!-- Professor specific -->
            <template v-if="currentUser?.role === 'professor'">
              <li><RouterLink class="dropdown-item" to="/manage-courses">Gérer mes cours</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/live-sessions">Sessions en direct</RouterLink></li>
            </template>
            
            <!-- Admin specific -->
            <template v-if="['admin', 'super_admin'].includes(currentUser?.role || '')">
              <li><RouterLink class="dropdown-item" to="/manage-professors">Gérer les professeurs</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/live-sessions">Sessions en direct</RouterLink></li>
            </template>
            
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item text-danger" @click="handleLogout">Déconnexion</button></li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dropdown-item:active {
  background-color: var(--bs-primary);
}
</style>