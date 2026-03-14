<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRoute, useRouter, RouterLink } from 'vue-router'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter() // useRouter is imported but not used in the provided snippet, will be used by store action

const token = ref('')
const password = ref('')
const confirmPassword = ref('')

const message = ref('') // For success messages
const customError = ref('') // For client-side validation errors like password mismatch

// Use computed properties for loading and error to automatically react to store changes
const loading = computed(() => authStore.loading)
const storeError = computed(() => authStore.error) // Renamed to avoid conflict with a local 'error' ref if any

onMounted(() => {
  const queryToken = route.query.token
  if (queryToken && typeof queryToken === 'string') {
    token.value = queryToken
  } else {
    customError.value = "Invalid or missing password reset token. Please request a new link."
    // Optionally, redirect if token is absolutely necessary and missing
    // router.push('/forgot-password')
  }
  // Clear any previous store errors when component mounts
  if (authStore.error) {
    authStore.error = ''
  }
})

const handleSubmit = async () => {
  message.value = ''
  customError.value = ''
  if (authStore.error) {
    authStore.error = ''
  }

  if (!token.value) {
    customError.value = "Invalid or missing reset token. Please try the reset link again or request a new one."
    return
  }

  if (password.value !== confirmPassword.value) {
    customError.value = "Passwords do not match."
    return
  }

  if (password.value.length < 8) { // Basic password length validation
    customError.value = "Password must be at least 8 characters long."
    return
  }

  const result = await authStore.resetPassword(token.value, password.value)

  if (result.success) {
    // The store action already redirects to /login.
    // We can set a message that might be displayed briefly or passed via query/store to login page.
    // For now, the redirect is the primary confirmation.
    // A more robust solution might involve a global notification system.
    // message.value = result.message || "Password has been reset successfully! Redirecting to login..."
    // setTimeout(() => router.push('/login'), 2000); // Manual redirect if store didn't do it.
  }
  // If result.success is false, the storeError computed property will display the error from the store.
}
</script>

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h2 class="card-title text-center mb-4">Réinitialiser le mot de passe</h2>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="password" class="form-label">Nouveau mot de passe</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="password"
                  placeholder="Entrez le nouveau mot de passe"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirmer le nouveau mot de passe</label>
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="confirmPassword"
                  placeholder="Confirmez le nouveau mot de passe"
                  required
                />
              </div>

              <div v-if="storeError" class="alert alert-danger py-2" role="alert">
                {{ storeError }}
              </div>

              <div v-if="customError" class="alert alert-danger py-2" role="alert">
                {{ customError }}
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
                <span v-if="loading"> Réinitialisation en cours...</span>
                <span v-else>Réinitialiser le mot de passe</span>
              </button>
            </form>

            <div class="text-center mt-3" v-if="!message"> <RouterLink to="/login">Retour à la connexion</RouterLink>
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
