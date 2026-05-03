<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { APP_NAME } from '../../config'

onMounted(() => {
  console.log(
    '%c📋 Identifiants de test par profil',
    'font-weight:bold; font-size:14px; color:#2453a7;'
  )
  console.table([
    { Profil: 'Super Admin', Email: 'admin@example.com', 'Mot de passe': 'admin123' },
    { Profil: 'Professeur 1', Email: 'prof1@example.com', 'Mot de passe': 'password123' },
    { Profil: 'Professeur 2', Email: 'prof2@example.com', 'Mot de passe': 'password123' },
    { Profil: 'Professeur 3', Email: 'prof3@example.com', 'Mot de passe': 'password123' },
    { Profil: 'Étudiant', Email: 'student@example.com', 'Mot de passe': 'password123' },
  ])
})

const authStore = useAuthStore()
const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

const form = ref({
  identifier: '',
  password: '',
  remember: false
})

const loginWithIdentifier = async () => {
  await authStore.login(form.value.identifier, form.value.password)
}
</script>

<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <img 
                src="../../assets/logo.png" 
                alt="Logo" 
                class="mb-2"
                style="width: 150px;"
              >
              <h2 class="fw-bold mb-1">Connexion</h2>
              <p class="text-muted">Accédez à votre compte {{ APP_NAME }}</p>
            </div>

            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>

            <form @submit.prevent="loginWithIdentifier">
              <div class="mb-3">
                <label for="identifier" class="form-label">Email ou téléphone</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-person"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="identifier" 
                    v-model="form.identifier"
                    placeholder="Entrez votre email ou téléphone"
                    required
                  >
                </div>
              </div>

              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <label for="password" class="form-label">Mot de passe</label>
                  <a href="/forgot-password" class="text-decoration-none small">Mot de passe oublié?</a>
                </div>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock"></i></span>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    v-model="form.password"
                    placeholder="Entrez votre mot de passe"
                    required
                  >
                </div>
              </div>

              <div class="mb-4 form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="remember" 
                  v-model="form.remember"
                >
                <label class="form-check-label" for="remember">Rester connecté</label>
              </div>

              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <span v-if="loading">Connexion en cours...</span>
                  <span v-else>Se connecter</span>
                </button>
              </div>
            </form>

            <div class="mt-4 text-center">
              <p class="mb-0">Vous n'avez pas de compte? <RouterLink to="/register" class="text-decoration-none">S'inscrire</RouterLink></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-group-text {
  background-color: transparent;
}
</style>