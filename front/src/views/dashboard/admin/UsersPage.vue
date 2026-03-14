<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">Gestion des Utilisateurs</h1>
            <p class="text-muted mb-0">Gérez les utilisateurs de la plateforme</p>
          </div>
          <RouterLink to="/user-form" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Ajouter un utilisateur
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                <i class="bi bi-people text-primary fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Total utilisateurs</h6>
                <h3 class="mb-0">{{ users.length }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                <i class="bi bi-person-check text-success fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Actifs</h6>
                <h3 class="mb-0">{{ activeUsers }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                <i class="bi bi-person-dash text-warning fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Inactifs</h6>
                <h3 class="mb-0">{{ inactiveUsers }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="rounded-circle bg-info bg-opacity-10 p-3 me-3">
                <i class="bi bi-calendar text-info fs-4"></i>
              </div>
              <div>
                <h6 class="mb-0 text-muted">Nouveaux (30j)</h6>
                <h3 class="mb-0">{{ newUsers }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="input-group">
                  <span class="input-group-text bg-transparent">
                    <i class="bi bi-search"></i>
                  </span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="filters.search"
                    placeholder="Rechercher un utilisateur..."
                  >
                </div>
              </div>
              <div class="col-md-4">
                <select v-model="filters.role" class="form-select">
                  <option value="all">Tous les rôles</option>
                  <option value="student">Étudiants</option>
                  <option value="professor">Professeurs</option>
                  <option value="admin">Administrateurs</option>
                </select>
              </div>
              <div class="col-md-4">
                <select v-model="filters.status" class="form-select">
                  <option value="all">Tous les statuts</option>
                  <option value="active">Actifs</option>
                  <option value="inactive">Inactifs</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Utilisateur</th>
                <th>Email</th>
                <th>Rôle</th>
                <th>Statut</th>
                <th>Inscription</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-light p-2 me-2">
                      <i class="bi bi-person-circle text-primary"></i>
                    </div>
                    <div>
                      <div class="fw-bold">{{ user.name }}</div>
                      <small class="text-muted">{{ user.phone }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span 
                    class="badge"
                    :class="user.role === 'admin' ? 'bg-danger' :
                           user.role === 'professor' ? 'bg-primary' : 'bg-success'"
                  >
                    {{ user.role }}
                  </span>
                </td>
                <td>
                  <span 
                    class="badge"
                    :class="user.status === 'active' ? 'bg-success' : 'bg-danger'"
                  >
                    {{ user.status }}
                  </span>
                </td>
                <td>{{ new Date(user.created_at).toLocaleDateString() }}</td>
                <td>
                  <div class="btn-group">
                    <RouterLink 
                      :to="`/user-form/${user.id}`"
                      class="btn btn-sm btn-outline-primary"
                    >
                      <i class="bi bi-pencil"></i>
                    </RouterLink>
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="toggleUserStatus(user)"
                    >
                      <i :class="['bi', user.status === 'active' ? 'bi-pause-fill' : 'bi-play-fill']"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteUser(user.id)"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredUsers.length === 0" class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-people display-1 text-muted"></i>
      </div>
      <h3>Aucun utilisateur trouvé</h3>
      <p class="text-muted">Ajoutez un nouvel utilisateur ou modifiez vos filtres</p>
      <RouterLink to="/user-form" class="btn btn-primary">
        Ajouter un utilisateur
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getUsers, deleteUser as apiDeleteUser, updateUser as apiUpdateUser } from '../../../services/api/user'

const users = ref<any[]>([])
const isLoading = ref(false)
const error = ref('')

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const data = await getUsers()
    // Map status from is_active
    users.value = data.map((u: any) => ({
        ...u,
        status: u.is_active ? 'active' : 'inactive'
    }))
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement des utilisateurs'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchUsers)

// Filters
const filters = ref({
  search: '',
  role: 'all',
  status: 'all'
})

// Computed properties
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    // Search filter
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      if (!(user.name || '').toLowerCase().includes(search) &&
          !(user.email || '').toLowerCase().includes(search) &&
          !(user.phone || '').includes(search)) {
        return false
      }
    }
    
    // Role filter
    if (filters.value.role !== 'all' && user.role !== filters.value.role) {
      return false
    }
    
    // Status filter
    if (filters.value.status !== 'all' && user.status !== filters.value.status) {
      return false
    }
    
    return true
  })
})

const activeUsers = computed(() => 
  users.value.filter(user => user.status === 'active').length
)

const inactiveUsers = computed(() => 
  users.value.filter(user => user.status === 'inactive').length
)

const newUsers = computed(() => {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  return users.value.filter(user => 
    new Date(user.created_at) >= thirtyDaysAgo
  ).length
})

// Actions
const toggleUserStatus = async (user: any) => {
  try {
    const newStatus = user.status === 'active' ? false : true
    await apiUpdateUser(user.id, { is_active: newStatus })
    user.status = newStatus ? 'active' : 'inactive'
  } catch (err: any) {
    alert(err.message || 'Erreur lors du changement de statut')
  }
}

const deleteUser = async (userId: number) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
    try {
        await apiDeleteUser(userId)
        users.value = users.value.filter(user => user.id !== userId)
    } catch (err: any) {
        alert(err.message || 'Erreur lors de la suppression')
    }
  }
}
</script>

<style scoped>
.rounded-circle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  padding: 0.5rem 1rem;
}
</style>