<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">{{ isEditing ? 'Modifier l\'utilisateur' : 'Ajouter un utilisateur' }}</h1>
            <p class="text-muted mb-0">
              {{ isEditing ? 'Modifiez les informations de l\'utilisateur' : 'Créez un nouvel utilisateur' }}
            </p>
          </div>
          <button class="btn btn-primary" @click="saveUser">
            <i class="bi bi-check-circle me-2"></i>Enregistrer
          </button>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-8">
        <!-- User Form -->
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <form @submit.prevent="saveUser">
              <!-- Basic Information -->
              <h5 class="mb-4">Informations de base</h5>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label">Nom</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="userForm.name"
                    required
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    v-model="userForm.email"
                    required
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Téléphone</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="userForm.phone"
                  >
                </div>

                <div class="col-md-6">
                  <label class="form-label">Pays</label>
                  <select class="form-select" v-model="userForm.country">
                    <option value="" disabled>Sélectionner un pays</option>
                    <option v-for="country in countries" :key="country" :value="country">
                      {{ country }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Date de naissance</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="userForm.birthdate"
                  >
                </div>
              </div>

              <!-- Role and Status -->
              <h5 class="mb-4">Rôle et statut</h5>
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label">Rôle</label>
                  <select class="form-select" v-model="userForm.role" required>
                    <option value="student">Étudiant</option>
                    <option value="professor">Professeur</option>
                    <option value="admin">Administrateur</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Statut</label>
                  <select class="form-select" v-model="userForm.status" required>
                    <option value="active">Actif</option>
                    <option value="inactive">Inactif</option>
                  </select>
                </div>
              </div>

              <!-- Password -->
              <h5 class="mb-4">Sécurité</h5>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Mot de passe</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    v-model="userForm.password"
                    :required="!isEditing"
                  >
                  <div class="form-text">
                    {{ isEditing ? 'Laissez vide pour conserver le mot de passe actuel' : 'Au moins 8 caractères' }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label">Confirmer le mot de passe</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    v-model="userForm.confirm_password"
                    :required="!isEditing"
                  >
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 2rem;">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Aperçu du profil</h5>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="avatar-placeholder rounded-circle mx-auto mb-3">
                <span class="display-4">{{ userForm.name.charAt(0) }}</span>
              </div>
              <h5 class="mb-1">{{ userForm.name || 'Nom de l\'utilisateur' }}</h5>
              <span 
                class="badge"
                :class="userForm.role === 'admin' ? 'bg-danger' :
                       userForm.role === 'professor' ? 'bg-primary' : 'bg-success'"
              >
                {{ userForm.role }}
              </span>
            </div>

            <div class="mb-4">
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-envelope me-2 text-muted"></i>
                <span>{{ userForm.email }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-telephone me-2 text-muted"></i>
                <span>{{ userForm.phone }}</span>
              </div>
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-geo-alt me-2 text-muted"></i>
                <span>{{ userForm.country }}</span>
              </div>
              <div class="d-flex align-items-center">
                <i class="bi bi-calendar me-2 text-muted"></i>
                <span>{{ userForm.birthdate }}</span>
              </div>
            </div>

            <div class="alert" :class="userForm.status === 'active' ? 'alert-success' : 'alert-danger'">
              <i :class="['bi me-2', userForm.status === 'active' ? 'bi-check-circle' : 'bi-x-circle']"></i>
              {{ userForm.status === 'active' ? 'Utilisateur actif' : 'Utilisateur inactif' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isEditing = computed(() => !!route.params.id)

// Form data
const userForm = ref({
  name: '',
  email: '',
  phone: '',
  country: '',
  birthdate: '',
  role: 'student',
  status: 'active',
  password: '',
  confirm_password: ''
})

// Country list
const countries = [
  "France", "Belgique", "Suisse", "Canada", "Maroc", "Algérie", 
  "Tunisie", "Sénégal", "Côte d'Ivoire", "Cameroun", "Mali"
]

// Load user data if editing
onMounted(async () => {
  if (isEditing.value) {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      userForm.value = {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+33 1 23 45 67 89',
        country: 'France',
        birthdate: '1990-01-01',
        role: 'student',
        status: 'active',
        password: '',
        confirm_password: ''
      }
    } catch (error) {
      console.error('Error loading user:', error)
    }
  }
})

// Save user
const saveUser = async () => {
  try {
    // Validate passwords match
    if (userForm.value.password !== userForm.value.confirm_password) {
      alert('Les mots de passe ne correspondent pas')
      return
    }
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    router.push('/manage-users')
  } catch (error) {
    console.error('Error saving user:', error)
  }
}
</script>

<style scoped>
.avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: var(--bs-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sticky-top {
  z-index: 1000;
}

.badge {
  padding: 0.5rem 1rem;
}
</style>