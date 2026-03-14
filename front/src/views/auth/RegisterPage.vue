<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { APP_NAME } from '../../config'
import { countries } from '../../services/utils'

const authStore = useAuthStore()
const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

const form = ref({
  name: '',
  email: '',
  phone: '',
  country: '',
  birthdate: '',
  password: '',
  confirm_password: '',
  terms: false
})

const customError = ref('')

const register = async () => {
  // Reset error
  customError.value = ''
  
  // Validate passwords match
  if (form.value.password !== form.value.confirm_password) {
    customError.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  
  // Validate terms
  if (!form.value.terms) {
    customError.value = 'Vous devez accepter les conditions d\'utilisation.'
    return
  }
  
  // Register
  await authStore.register({
    name: form.value.name,
    email: form.value.email,
    phone: form.value.phone,
    country: form.value.country,
    birthdate: form.value.birthdate,
    password: form.value.password
  })
}

</script>

<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-7">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <img 
                src="../../assets/logo.png" 
                alt="Logo" 
                class="mb-2"
                style="width: 150px;"
              >
              <h2 class="fw-bold mb-1">Inscription</h2>
              <p class="text-muted">Créez votre compte étudiant sur {{ APP_NAME }}</p>
            </div>

            <div v-if="error || customError" class="alert alert-danger" role="alert">
              {{ error || customError }}
            </div>

            <form @submit.prevent="register">
              <div class="row g-3">
                <!-- Name -->
                <div class="col-md-12">
                  <label for="name" class="form-label">Nom & Prénoms</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="name" 
                    v-model="form.name"
                    placeholder="Votre nom et prénoms"
                    required
                  >
                </div>

                <!-- Email -->
                <div class="col-md-6">
                  <label for="email" class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="form.email"
                    placeholder="votre.email@exemple.com"
                    required
                  >
                </div>

                <!-- Phone -->
                <div class="col-md-6">
                  <label for="phone" class="form-label">Téléphone</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone" 
                    v-model="form.phone"
                    placeholder="+33 123456789"
                    required
                  >
                </div>

                <!-- Country -->
                <div class="col-md-6">
                  <label for="country" class="form-label">Pays</label>
                  <select 
                    class="form-select" 
                    id="country" 
                    v-model="form.country"
                    required
                  >
                    <option value="" disabled selected>Sélectionner votre pays</option>
                    <option v-for="country in countries" :key="country" :value="country">
                      {{ country }}
                    </option>
                  </select>
                </div>

                <!-- Birthdate -->
                <div class="col-md-6">
                  <label for="birthdate" class="form-label">Date de naissance</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="birthdate" 
                    v-model="form.birthdate"
                    required
                  >
                </div>

                <!-- Password -->
                <div class="col-md-6">
                  <label for="password" class="form-label">Mot de passe</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    v-model="form.password"
                    placeholder="Créer un mot de passe"
                    required
                  >
                  <div class="form-text">
                    Au moins 8 caractères, incluant lettres et chiffres
                  </div>
                </div>

                <!-- Confirm Password -->
                <div class="col-md-6">
                  <label for="confirm_password" class="form-label">Confirmer le mot de passe</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="confirm_password" 
                    v-model="form.confirm_password"
                    placeholder="Confirmer votre mot de passe"
                    required
                  >
                </div>

                <!-- Terms -->
                <div class="col-12 mt-3">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="terms" 
                      v-model="form.terms"
                      required
                    >
                    <label class="form-check-label" for="terms">
                      J'accepte les <a href="#" class="text-decoration-none">conditions d'utilisation</a> et la <a href="#" class="text-decoration-none">politique de confidentialité</a>
                    </label>
                  </div>
                </div>

                <div class="col-12 mt-4">
                  <button 
                    type="submit" 
                    class="btn btn-primary w-100"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    <span v-if="loading">Inscription en cours...</span>
                    <span v-else>S'inscrire</span>
                  </button>
                </div>
              </div>
            </form>

            <div class="mt-4 text-center">
              <p class="mb-0">Vous avez déjà un compte? <RouterLink to="/login" class="text-decoration-none">Se connecter</RouterLink></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-control:focus,
.form-select:focus {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}
</style>