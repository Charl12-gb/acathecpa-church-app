<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

const form = ref({
  name: '',
  email: '',
  phone: '',
  country: '',
  birthdate: '',
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const formSubmitted = ref(false)
const loading = ref(false)
const error = ref('')
const activeTab = ref<'personal' | 'security' | 'notifications'>('personal')

// Fill form with current user data
onMounted(() => {
  if (currentUser.value) {
    form.value.name = currentUser.value.name || ''
    form.value.email = currentUser.value.email || ''
    form.value.phone = currentUser.value.phone || ''
    form.value.country = currentUser.value.country || ''
    form.value.birthdate = currentUser.value.birthdate || ''
  }
})

// Update profile
const updateProfile = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Update successful
    formSubmitted.value = true
    
    // Reset password fields
    form.value.current_password = ''
    form.value.new_password = ''
    form.value.confirm_password = ''
  } catch (err: any) {
    error.value = err.message || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}

// Update password
const updatePassword = async () => {
  // Validate passwords match
  if (form.value.new_password !== form.value.confirm_password) {
    error.value = 'Les nouveaux mots de passe ne correspondent pas.'
    return
  }
  
  // Add password update logic here
}

// Country list (sample)
const countries = [
  "France", "Belgique", "Suisse", "Canada", "Maroc", "Algérie", 
  "Tunisie", "Sénégal", "Côte d'Ivoire", "Cameroun", "Mali"
]
</script>

<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-0">Mon Profil</h1>
        <p class="text-muted">Gérez vos informations personnelles et vos préférences</p>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-3 mb-4 mb-lg-0">
        <!-- Profile Sidebar -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body text-center">
            <div class="mb-3">
              <div class="avatar-placeholder rounded-circle mx-auto mb-3">
                <span class="display-4">{{ currentUser?.name?.charAt(0).toUpperCase() }}</span>
              </div>
              <h5 class="mb-1">{{ currentUser?.name }}</h5>
              <p class="text-muted mb-0">{{ currentUser?.email }}</p>
            </div>
            <div class="d-grid">
              <button class="btn btn-sm btn-outline-primary">Changer la photo</button>
            </div>
          </div>
        </div>

      </div>

      <div class="col-lg-9">
        <div class="card border-0 shadow-sm mb-4 tabs-shell">
          <div class="card-body py-2 px-2">
            <div class="nav nav-pills profile-tabs" role="tablist" aria-label="Sections profil">
              <button
                type="button"
                class="nav-link"
                :class="{ active: activeTab === 'personal' }"
                @click="activeTab = 'personal'"
              >
                <i class="bi bi-person me-2"></i>Informations personnelles
              </button>
              <button
                type="button"
                class="nav-link"
                :class="{ active: activeTab === 'security' }"
                @click="activeTab = 'security'"
              >
                <i class="bi bi-shield-lock me-2"></i>Sécurité
              </button>
              <button
                type="button"
                class="nav-link"
                :class="{ active: activeTab === 'notifications' }"
                @click="activeTab = 'notifications'"
              >
                <i class="bi bi-bell me-2"></i>Notifications
              </button>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="formSubmitted" class="alert alert-success alert-dismissible fade show" role="alert">
          Votre profil a été mis à jour avec succès.
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" @click="formSubmitted = false"></button>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
          {{ error }}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" @click="error = ''"></button>
        </div>

        <!-- Personal Information -->
        <div v-if="activeTab === 'personal'" class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Informations personnelles</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row g-3">
                <!-- Name -->
                <div class="col-md-6">
                  <label for="name" class="form-label">Nom complet</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="name" 
                    v-model="form.name"
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
                  >
                </div>

                <!-- Country -->
                <div class="col-md-6">
                  <label for="country" class="form-label">Pays</label>
                  <select 
                    class="form-select" 
                    id="country" 
                    v-model="form.country"
                  >
                    <option value="" disabled>Sélectionner votre pays</option>
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
                  >
                </div>

                <div class="col-12 mt-4">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    <span v-if="loading">Mise à jour en cours...</span>
                    <span v-else>Mettre à jour le profil</span>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Security Settings -->
        <div v-if="activeTab === 'security'" class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Sécurité</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updatePassword">
              <div class="row g-3">
                <!-- Current Password -->
                <div class="col-md-6">
                  <label for="current_password" class="form-label">Mot de passe actuel</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="current_password" 
                    v-model="form.current_password"
                    required
                  >
                </div>

                <div class="col-md-6"></div>

                <!-- New Password -->
                <div class="col-md-6">
                  <label for="new_password" class="form-label">Nouveau mot de passe</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="new_password" 
                    v-model="form.new_password"
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
                    required
                  >
                </div>

                <div class="col-12 mt-4">
                  <button type="submit" class="btn btn-primary">
                    Changer le mot de passe
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Notification Settings -->
        <div v-if="activeTab === 'notifications'" class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Préférences de notification</h5>
          </div>
          <div class="card-body">
            <form>
              <div class="mb-3">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="email_notif" checked>
                  <label class="form-check-label" for="email_notif">
                    Notifications par email
                  </label>
                </div>
                <div class="form-text ms-4 ps-1">
                  Recevoir des emails concernant vos cours, commentaires et messages
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="course_update" checked>
                  <label class="form-check-label" for="course_update">
                    Mises à jour des cours
                  </label>
                </div>
                <div class="form-text ms-4 ps-1">
                  Être notifié lorsqu'un cours que vous suivez est mis à jour
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="newsletter">
                  <label class="form-check-label" for="newsletter">
                    Newsletter
                  </label>
                </div>
                <div class="form-text ms-4 ps-1">
                  Recevoir des informations sur les nouveaux cours et offres spéciales
                </div>
              </div>

              <button type="submit" class="btn btn-primary">
                Enregistrer les préférences
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.tabs-shell {
  background: #f8fbff;
  border: 1px solid #e8eef7;
}

.profile-tabs {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.profile-tabs .nav-link {
  border-radius: 10px;
  color: #4f617e;
  font-weight: 600;
  padding: 0.6rem 0.9rem;
}

.profile-tabs .nav-link.active {
  background-color: var(--bs-primary);
  color: #fff;
}

.form-check-input:checked {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}
</style>