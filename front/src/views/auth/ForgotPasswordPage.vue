<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { RouterLink } from 'vue-router'

const authStore = useAuthStore()

const email = ref('')
const message = ref('') // For success or info messages

// Use computed properties for loading and error to automatically react to store changes
const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

const handleSubmit = async () => {
  message.value = '' // Clear previous message
  // It's good practice for the store action to clear its own errors,
  // but component can also ensure it's reset before a new submit
  if (authStore.error) {
    authStore.error = ''
  }

  const result = await authStore.requestPasswordReset(email.value)

  if (result.success) {
    // The backend returns a generic message. We'll use a slightly more user-friendly one here.
    message.value = "If an account with that email exists, a password reset link has been sent. Please check your inbox."
    email.value = '' // Clear the email field on success
  }
  // If result.success is false, the error computed property will display the error from the store.
}
</script>

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="card-title text-center mb-4">Mot de passe oublié</h2>
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="email" class="form-label">Adresse e-mail</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="email"
                  placeholder="Entrez votre e-mail"
                  required
                />
              </div>
              <div v-if="error" class="alert alert-danger py-2" role="alert">
                {{ error }}
              </div>
              <div v-if="message" class="alert alert-success py-2" role="alert">
                {{ message }}
              </div>
              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                <span v-if="loading"> Envoi en cours...</span>
                <span v-else>Envoyer le lien de réinitialisation du mot de passe</span>
              </button>
            </form>
            <div class="text-center mt-3">
              <RouterLink to="/login">Retour à la connexion</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Add any component-specific styles here */
.card {
  border: none;
}
</style>
