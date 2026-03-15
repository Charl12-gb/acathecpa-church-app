<template>
  <div class="container-fluid">
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
          <button class="btn btn-primary" @click="saveUser" :disabled="isSaving">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-check-circle me-2"></i>
            {{ isSaving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-8">
        <!-- Error message -->
        <div v-if="errorMsg" class="alert alert-danger mb-3">{{ errorMsg }}</div>
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
import { getUserById, updateUser } from '../../../services/api/user'
import { register } from '../../../services/api/auth'
import { UserRole } from '../../../types/api/userTypes'

const route = useRoute()
const router = useRouter()

const isEditing = computed(() => !!route.params.id)
const isSaving = ref(false)
const errorMsg = ref('')

const userForm = ref({
  name: '',
  email: '',
  phone: '',
  country: '',
  birthdate: '',
  role: 'student' as string,
  status: 'active',
  password: '',
  confirm_password: ''
})

const countries = [
  "France", "Belgique", "Suisse", "Canada", "Maroc", "Algérie",
  "Tunisie", "Sénégal", "Côte d'Ivoire", "Cameroun", "Mali"
]

onMounted(async () => {
  if (isEditing.value) {
    try {
      const userId = Number(route.params.id)
      const user = await getUserById(userId) as any
      const roleName = typeof user.role === 'object' && user.role !== null
        ? (user.role as any).name
        : user.role as string
      userForm.value = {
        name: user.name || '',
        email: user.email,
        phone: user.phone || '',
        country: user.country || '',
        birthdate: user.birthdate || '',
        role: roleName,
        status: user.is_active ? 'active' : 'inactive',
        password: '',
        confirm_password: ''
      }
    } catch (err: any) {
      errorMsg.value = err.message || 'Erreur lors du chargement de l\'utilisateur'
    }
  }
})

const saveUser = async () => {
  errorMsg.value = ''
  if (userForm.value.password && userForm.value.password !== userForm.value.confirm_password) {
    errorMsg.value = 'Les mots de passe ne correspondent pas'
    return
  }

  isSaving.value = true
  try {
    if (isEditing.value) {
      const userId = Number(route.params.id)
      const payload: any = {
        name: userForm.value.name,
        email: userForm.value.email,
        phone: userForm.value.phone || null,
        country: userForm.value.country || null,
        birthdate: userForm.value.birthdate || null,
        role: { name: userForm.value.role },
        is_active: userForm.value.status === 'active',
      }
      if (userForm.value.password) {
        payload.password = userForm.value.password
      }
      await updateUser(userId, payload)
    } else {
      await register({
        name: userForm.value.name,
        email: userForm.value.email,
        password: userForm.value.password,
        phone: userForm.value.phone || undefined,
        country: userForm.value.country || undefined,
        birthdate: userForm.value.birthdate || undefined,
        role: userForm.value.role as UserRole,
      })
    }
    router.push('/manage-users')
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || 'Erreur lors de l\'enregistrement'
  } finally {
    isSaving.value = false
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