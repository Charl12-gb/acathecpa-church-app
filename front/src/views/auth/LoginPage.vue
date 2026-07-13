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
  <div class="auth-page-container min-vh-100 d-flex">
    <div class="row g-0 w-100 min-vh-100">
      <!-- Left side: Illustration (Visible only on large devices) -->
      <div class="col-lg-6 d-none d-lg-flex flex-column justify-content-between p-5 text-white position-relative auth-sidebar">
        <!-- Background Image overlay -->
        <div class="auth-sidebar-bg" style="background-image: url('/auth_login_illustration_1783456492135.png');"></div>
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
          <h1 class="display-5 fw-bold mb-3 animate__animated animate__fadeInUp">Élevez vos compétences</h1>
          <p class="fs-5 text-white-80 animate__animated animate__fadeInUp animate__delay-1s">
            Accédez à une plateforme d'apprentissage de haut niveau conçue pour révéler votre plein potentiel et accélérer votre carrière.
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
            <h2 class="fw-bold mb-2 text-dark-blue">Connexion</h2>
            <p class="text-muted">Ravi de vous revoir ! Connectez-vous à votre espace étudiant.</p>
          </div>

          <div v-if="error" class="alert alert-danger custom-alert animate__animated animate__shakeX" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error }}
          </div>

          <form @submit.prevent="loginWithIdentifier" class="needs-validation">
            <div class="mb-3">
              <label for="identifier" class="form-label fw-semibold">Email ou Téléphone</label>
              <div class="input-group custom-input-group">
                <span class="input-group-text"><i class="bi bi-person"></i></span>
                <input 
                  type="text" 
                  class="form-control" 
                  id="identifier" 
                  v-model="form.identifier"
                  placeholder="exemple@domaine.com ou +225..."
                  required
                >
              </div>
            </div>

            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label for="password" class="form-label fw-semibold mb-0">Mot de passe</label>
                <a href="/forgot-password" class="forgot-password-link text-decoration-none">Mot de passe oublié ?</a>
              </div>
              <div class="input-group custom-input-group">
                <span class="input-group-text"><i class="bi bi-lock"></i></span>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="form.password"
                  placeholder="Votre mot de passe"
                  required
                >
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-4">
              <div class="form-check custom-checkbox">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="remember" 
                  v-model="form.remember"
                >
                <label class="form-check-label text-muted" for="remember">Se souvenir de moi</label>
              </div>
            </div>

            <div class="d-grid mb-4">
              <button 
                type="submit" 
                class="btn btn-primary btn-lg custom-btn"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                <span v-if="loading">Connexion en cours...</span>
                <span v-else>Se connecter <i class="bi bi-arrow-right ms-1"></i></span>
              </button>
            </div>
          </form>

          <div class="text-center">
            <p class="text-muted mb-0">
              Nouveau sur la plateforme ? 
              <RouterLink to="/register" class="signup-link fw-bold text-decoration-none">Créer un compte</RouterLink>
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
  max-width: 480px;
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

.custom-input-group .form-control {
  border: none;
  padding: 0.75rem 1rem 0.75rem 0.2rem;
  font-size: 1rem;
  box-shadow: none;
}

.custom-input-group .form-control:focus {
  outline: none;
}

.forgot-password-link {
  font-size: 0.9rem;
  color: var(--color-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-password-link:hover {
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

.signup-link {
  color: var(--color-primary);
  transition: color 0.2s ease;
}

.signup-link:hover {
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