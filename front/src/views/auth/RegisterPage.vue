<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { APP_NAME } from '../../config'
import { countries } from '../../services/utils'
import SearchableSelect from '../../components/ui/SearchableSelect.vue'

const authStore = useAuthStore()
const route = useRoute()
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
  }, route.query.redirect)
}

</script>

<template>
  <div class="auth-page-container min-vh-100 d-flex">
    <div class="row g-0 w-100 min-vh-100">
      <!-- Left side: Illustration (Visible only on large devices) -->
      <div class="col-lg-6 d-none d-lg-flex flex-column justify-content-between p-5 text-white position-relative auth-sidebar">
        <!-- Background Image overlay -->
        <div class="auth-sidebar-bg" style="background-image: url('/auth_register_illustration_1783456506134.png');"></div>
        <div class="auth-sidebar-overlay"></div>
        
        <!-- Top branding logo/name -->
        <div class="position-relative z-index-2">
          <RouterLink to="/" class="d-flex align-items-center gap-2 text-white text-decoration-none">
            <img src="../../assets/logo.png" alt="Logo" class="logo-sidebar">
            <span class="fs-4 fw-bold letter-spacing-1">{{ APP_NAME }}</span>
          </RouterLink>
        </div>
        
        <!-- Centered Inspiring Text -->
        <div class="position-relative z-index-2 my-auto max-width-sidebar-text">
          <h1 class="display-5 fw-bold mb-3 animate__animated animate__fadeInUp">Commencez votre voyage académique</h1>
          <p class="fs-5 text-white-80 animate__animated animate__fadeInUp animate__delay-1s">
            Rejoignez notre communauté d'étudiants et de professionnels. Développez de nouvelles compétences avec nos programmes de formation certifiés.
          </p>
        </div>
        
        <!-- Bottom copyright info -->
        <div class="position-relative z-index-2 text-white-50 small">
          &copy; {{ new Date().getFullYear() }} {{ APP_NAME }}. Tous droits réservés.
        </div>
      </div>
      
      <!-- Right side: Form (Takes full width on smaller screens, half on large) -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center py-5 px-4 px-sm-5 bg-auth-form">
        <div class="auth-form-card w-100">
          <!-- Logo shown on mobile only -->
          <div class="text-center d-lg-none mb-4">
            <img src="../../assets/logo.png" alt="Logo" class="logo-mobile mb-2">
            <h3 class="fw-bold mb-1">{{ APP_NAME }}</h3>
          </div>

          <div class="mb-4">
            <h2 class="fw-bold mb-2 text-dark-blue">Inscription</h2>
            <p class="text-muted">Créez votre compte étudiant pour commencer vos cours.</p>
          </div>

          <div v-if="error || customError" class="alert alert-danger custom-alert animate__animated animate__shakeX" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error || customError }}
          </div>

          <form @submit.prevent="register" class="needs-validation">
            <div class="row g-3">
              <!-- Name -->
              <div class="col-12">
                <label for="name" class="form-label fw-semibold">Nom & Prénoms</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-person"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="name" 
                    v-model="form.name"
                    placeholder="Votre nom et prénoms complets"
                    required
                  >
                </div>
              </div>

              <!-- Email -->
              <div class="col-md-6">
                <label for="email" class="form-label fw-semibold">Email</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="form.email"
                    placeholder="votre@email.com"
                    required
                  >
                </div>
              </div>

              <!-- Phone -->
              <div class="col-md-6">
                <label for="phone" class="form-label fw-semibold">Téléphone</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-telephone"></i></span>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone" 
                    v-model="form.phone"
                    placeholder="+225..."
                    required
                  >
                </div>
              </div>

              <!-- Country -->
              <div class="col-md-6">
                <label for="country" class="form-label fw-semibold">Pays</label>
                <SearchableSelect
                  id="country"
                  v-model="form.country"
                  :options="countries"
                  placeholder="Votre pays..."
                />
              </div>

              <!-- Birthdate -->
              <div class="col-md-6">
                <label for="birthdate" class="form-label fw-semibold">Date de naissance</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-calendar"></i></span>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="birthdate" 
                    v-model="form.birthdate"
                    required
                  >
                </div>
              </div>

              <!-- Password -->
              <div class="col-md-6">
                <label for="password" class="form-label fw-semibold">Mot de passe</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-lock"></i></span>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    v-model="form.password"
                    placeholder="Au moins 8 car."
                    required
                  >
                </div>
              </div>

              <!-- Confirm Password -->
              <div class="col-md-6">
                <label for="confirm_password" class="form-label fw-semibold">Confirmer le mot de passe</label>
                <div class="input-group custom-input-group">
                  <span class="input-group-text"><i class="bi bi-shield-check"></i></span>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="confirm_password" 
                    v-model="form.confirm_password"
                    placeholder="Répétez le mot de passe"
                    required
                  >
                </div>
              </div>

              <!-- Terms -->
              <div class="col-12 mt-3">
                <div class="form-check custom-checkbox">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="terms" 
                    v-model="form.terms"
                    required
                  >
                  <label class="form-check-label text-muted small" for="terms">
                    J'accepte les <RouterLink to="/conditions-utilisation" target="_blank" class="terms-link text-decoration-none">conditions d'utilisation</RouterLink> et la <RouterLink to="/confidentialite" target="_blank" class="terms-link text-decoration-none">politique de confidentialité</RouterLink>
                  </label>
                </div>
              </div>

              <div class="col-12 mt-4">
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg w-100 custom-btn"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <span v-if="loading">Inscription en cours...</span>
                  <span v-else>S'inscrire <i class="bi bi-arrow-right ms-1"></i></span>
                </button>
              </div>
            </div>
          </form>

          <div class="text-center mt-4">
            <p class="text-muted mb-0">
              Déjà un compte ? 
              <RouterLink to="/login" class="login-link fw-bold text-decoration-none">Se connecter</RouterLink>
            </p>
          </div>

          <div class="mt-4 text-center">
            <RouterLink to="/" class="back-home-btn">
              <i class="bi bi-arrow-left"></i>
              <span>Retour à l'accueil</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page-container {
  background-color: var(--background-default);
  overflow-x: hidden;
}

.auth-sidebar {
  overflow: hidden;
  background-color: var(--color-secondary);
}

.auth-sidebar-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  transition: transform 10s ease;
  z-index: 1;
}

.auth-sidebar:hover .auth-sidebar-bg {
  transform: scale(1.05);
}

.auth-sidebar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(27, 122, 120, 0.85) 0%, rgba(193, 68, 40, 0.7) 100%);
  z-index: 1;
}

.logo-sidebar {
  width: 45px;
  height: 45px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.9);
  padding: 5px;
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.z-index-2 {
  z-index: 2;
}

.max-width-sidebar-text {
  max-width: 500px;
}

.bg-auth-form {
  background-color: var(--background-default);
}

.auth-form-card {
  max-width: 600px;
  background: var(--background-secondary);
  border: 1px solid rgba(27, 122, 120, 0.15);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
}

.logo-mobile {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.text-dark-blue {
  color: #2c3e50;
}

.custom-alert {
  border-radius: 12px;
  border: none;
  font-size: 0.95rem;
}

/* Custom form inputs */
.custom-input-group {
  border: 1px solid rgba(108, 117, 125, 0.25);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  background-color: #fff;
}

.custom-input-group:focus-within {
  border-color: var(--color-secondary);
  box-shadow: 0 0 0 4px rgba(27, 122, 120, 0.15);
}

.custom-input-group .input-group-text {
  background-color: transparent;
  border: none;
  color: #6c757d;
  padding-left: 1.2rem;
  padding-right: 0.8rem;
  font-size: 1.1rem;
}

.custom-input-group .form-control,
.custom-input-group .custom-select {
  border: none;
  padding: 0.75rem 1rem 0.75rem 0.2rem;
  font-size: 1rem;
  box-shadow: none;
}

.custom-input-group .custom-select {
  padding-left: 0.2rem;
  background-position: right 0.75rem center;
}

.custom-input-group .form-control:focus,
.custom-input-group .custom-select:focus {
  outline: none;
}

.terms-link {
  color: var(--color-primary);
  font-weight: 500;
}

.terms-link:hover {
  color: var(--color-secondary);
}

/* Checkbox styling */
.custom-checkbox .form-check-input {
  border-color: rgba(27, 122, 120, 0.3);
}

.custom-checkbox .form-check-input:checked {
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
}

/* Primary Button */
.custom-btn {
  background-color: var(--color-primary);
  border: none;
  border-radius: 12px;
  padding: 0.8rem 1.5rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(193, 68, 40, 0.2);
  transition: all 0.3s ease;
}

.custom-btn:hover {
  background-color: var(--color-secondary);
  box-shadow: 0 6px 18px rgba(27, 122, 120, 0.3);
  transform: translateY(-2px);
}

.custom-btn:active {
  transform: translateY(0);
}

.custom-btn:disabled {
  background-color: #a5a5a5;
  box-shadow: none;
}

.login-link {
  color: var(--color-primary);
  transition: color 0.2s ease;
}

.login-link:hover {
  color: var(--color-secondary);
}

.back-home-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.2s ease;
  text-decoration: none;
}

.back-home-btn:hover {
  color: var(--color-secondary);
  transform: translateX(-3px);
}

/* Animations */
.animate__animated {
  animation-duration: 0.8s;
}

@media (max-width: 991.98px) {
  .bg-auth-form {
    background-color: var(--background-default);
  }
  .auth-form-card {
    padding: 2.5rem 1.5rem;
    box-shadow: none;
    background: transparent;
    border: none;
  }
}
</style>