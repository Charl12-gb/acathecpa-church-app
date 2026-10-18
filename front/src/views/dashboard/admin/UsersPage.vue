<template>
  <div class="users-page">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h1 class="page-title mb-1">Gestion des Utilisateurs</h1>
          <p class="page-subtitle mb-0">Gérez les utilisateurs de la plateforme</p>
        </div>
        <RouterLink to="/user-form" class="btn btn-primary-custom">
          <i class="bi bi-plus-lg me-2"></i>Ajouter un utilisateur
        </RouterLink>
      </div>
    </div>

    <!-- Stats Strip -->
    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button type="button" class="btn-close" aria-label="Fermer" @click="error = ''"></button>
    </div>

    <div class="stats-strip mb-4">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(36,83,167,0.1);">
          <i class="bi bi-people" style="color: #2453a7;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Total utilisateurs</span>
          <span class="stat-value">{{ users.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(24,121,78,0.1);">
          <i class="bi bi-person-check" style="color: #18794e;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Actifs</span>
          <span class="stat-value">{{ activeUsers }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(180,83,9,0.1);">
          <i class="bi bi-person-dash" style="color: #b45309;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Inactifs</span>
          <span class="stat-value">{{ inactiveUsers }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(107,114,128,0.1);">
          <i class="bi bi-calendar" style="color: #6b7280;"></i>
        </div>
        <div class="stat-info">
          <span class="stat-label">Nouveaux (30j)</span>
          <span class="stat-value">{{ newUsers }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card app-card filter-card">
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
                <SearchableSelect
                  v-model="filters.role"
                  :searchable="false"
                  :options="[
                    { value: 'all', label: 'Tous les rôles' },
                    { value: 'student', label: 'Étudiants' },
                    { value: 'professor', label: 'Professeurs' },
                    { value: 'admin', label: 'Administrateurs' },
                  ]"
                />
              </div>
              <div class="col-md-4">
                <SearchableSelect
                  v-model="filters.status"
                  :searchable="false"
                  :options="[
                    { value: 'all', label: 'Tous les statuts' },
                    { value: 'active', label: 'Actifs' },
                    { value: 'inactive', label: 'Inactifs' },
                  ]"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card app-card table-card">
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
                    :class="['admin','super_admin'].includes(user.role) ? 'bg-danger' :
                           user.role === 'professor' ? 'bg-primary' : 'bg-success'"
                  >
                    {{ user.role === 'super_admin' ? 'Super Admin' : user.role === 'admin' ? 'Admin' : user.role === 'professor' ? 'Professeur' : 'Étudiant' }}
                  </span>
                </td>
                <td>
                  <span 
                    class="badge"
                    :class="user.status === 'active' ? 'bg-success' : 'bg-danger'"
                  >
                    {{ user.status === 'active' ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td>{{ new Date(user.created_at).toLocaleDateString() }}</td>
                <td>
                  <span v-if="!canManage(user)" class="text-muted small" title="Réservé aux super administrateurs">
                    <i class="bi bi-shield-lock"></i> Protégé
                  </span>
                  <div v-else class="btn-group">
                    <RouterLink 
                      :to="`/user-form/${user.id}`"
                      class="btn btn-sm btn-outline-custom"
                    >
                      <i class="bi bi-pencil"></i>
                    </RouterLink>
                    <button 
                      class="btn btn-sm btn-outline-custom"
                      @click="toggleUserStatus(user)"
                    >
                      <i :class="['bi', user.status === 'active' ? 'bi-pause-fill' : 'bi-play-fill']"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger-custom"
                      @click="askDelete(user)"
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

    <!-- Deletion dialog -->
    <div v-if="deletion" class="del-backdrop" @click.self="deletion = null">
      <div class="del-dialog" role="dialog" aria-modal="true" aria-labelledby="del-title">
        <h5 id="del-title">Supprimer {{ deletion.user.name || deletion.user.email }}</h5>

        <div v-if="!deletion.impact" class="text-center py-3">
          <div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Chargement</span></div>
        </div>

        <template v-else-if="!deletion.impact.can_delete && deletion.impact.has_history">
          <p>Ce compte a un historique : <strong>{{ historySummary }}</strong>.</p>
          <p class="text-muted">Pour le conserver, désactivez-le : la personne ne pourra plus se connecter.
            Seul un super administrateur peut le supprimer définitivement.</p>
          <div class="del-actions">
            <button type="button" class="btn btn-light" @click="deletion = null">Annuler</button>
            <button v-if="deletion.user.status === 'active'" type="button" class="btn btn-warning" @click="deactivateInstead">
              Désactiver à la place
            </button>
          </div>
        </template>

        <template v-else>
          <template v-if="deletion.impact.has_history">
            <p class="text-danger fw-semibold">Suppression définitive, avec toutes les données du compte :</p>
            <p>{{ historySummary }}.</p>
            <p v-if="deletion.impact.history.course_enrollments" class="text-muted small">
              Les cours de ce formateur seront supprimés, avec les inscriptions, paiements et certificats de leurs étudiants.
            </p>
            <label for="del-confirm" class="form-label small">Tapez <code>{{ deletion.user.email }}</code> pour confirmer</label>
            <input id="del-confirm" v-model.trim="deletion.typed" class="form-control mb-3" autocomplete="off">
          </template>
          <p v-else>Ce compte n'a aucun historique. Il sera supprimé.</p>
          <div v-if="deletion.error" class="alert alert-danger py-2">{{ deletion.error }}</div>
          <div class="del-actions">
            <button type="button" class="btn btn-light" @click="deletion = null">Annuler</button>
            <button type="button" class="btn btn-danger" :disabled="deletion.busy || (deletion.impact.has_history && deletion.typed !== deletion.user.email)"
              @click="confirmDelete">
              {{ deletion.impact.has_history ? 'Supprimer définitivement' : 'Supprimer' }}
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredUsers.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="bi bi-people"></i>
      </div>
      <h3>Aucun utilisateur trouvé</h3>
      <p class="text-muted">Ajoutez un nouvel utilisateur ou modifiez vos filtres</p>
      <RouterLink to="/user-form" class="btn btn-primary-custom">
        <i class="bi bi-plus-lg me-2"></i>Ajouter un utilisateur
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getUsers, deleteUser as apiDeleteUser, updateUser as apiUpdateUser, getUserDeletionImpact, type UserDeletionImpact } from '../../../services/api/user'
import { useAuthStore } from '../../../stores/auth'
import { UserRole } from '../../../types/api/userTypes'
import SearchableSelect from '../../../components/ui/SearchableSelect.vue'

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
        status: u.is_active ? 'active' : 'inactive',
        role: typeof u.role === 'object' && u.role !== null ? u.role.name : u.role
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
    error.value = err.response?.data?.detail || 'Erreur lors du changement de statut'

  }
}

// Super admin accounts can only be managed by a super admin.
const authStore = useAuthStore()
const canManage = (user: any) =>
  authStore.hasRole(UserRole.SUPER_ADMIN) || user.role !== 'super_admin'

const deletion = ref<null | {
  user: any; impact: UserDeletionImpact | null; typed: string; busy: boolean; error: string
}>(null)

const HISTORY_LABELS: Record<string, string> = {
  enrollments: 'inscription(s)', payments: 'paiement(s)', certificates: 'certificat(s)',
  courses: 'cours donné(s)', course_enrollments: 'étudiant(s) inscrit(s) à ses cours',
  contents: 'article(s) ou podcast(s)', live_sessions: 'session(s) en direct',
}
const historySummary = computed(() => {
  const history = deletion.value?.impact?.history ?? {}
  return Object.entries(history).filter(([, n]) => n).map(([k, n]) => `${n} ${HISTORY_LABELS[k] ?? k}`).join(', ')
})

const askDelete = async (user: any) => {
  deletion.value = { user, impact: null, typed: '', busy: false, error: '' }
  try {
    deletion.value.impact = await getUserDeletionImpact(user.id)
  } catch (err: any) {
    deletion.value = null
    error.value = err.response?.data?.detail || 'Impossible de vérifier ce compte.'
  }
}

const confirmDelete = async () => {
  if (!deletion.value) return
  const target = deletion.value
  target.busy = true
  target.error = ''
  try {
    await apiDeleteUser(target.user.id)
    users.value = users.value.filter(u => u.id !== target.user.id)
    deletion.value = null
  } catch (err: any) {
    target.error = err.response?.data?.detail || 'Erreur lors de la suppression.'
  } finally {
    target.busy = false
  }
}

const deactivateInstead = async () => {
  if (!deletion.value) return
  await toggleUserStatus(deletion.value.user)
  deletion.value = null
}
</script>

<style scoped lang="scss">
.del-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, .45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1050;
}

.del-dialog {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, .2);
}

.del-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.users-page {
  max-width: 1100px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a2332;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

.btn-primary-custom {
  background: #2453a7;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-weight: 500;
  font-size: 0.875rem;
  &:hover { background: #1a3f8a; color: #fff; }
}

.btn-outline-custom {
  background: transparent;
  border: 1px solid #e7edf5;
  color: #4b5563;
  border-radius: 6px;
  font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}

.btn-outline-danger-custom {
  background: transparent;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 6px;
  font-size: 0.8rem;
  &:hover { background: #fef2f2; }
}

.app-card {
  border: 1px solid #e7edf5;
  border-radius: 12px;
  box-shadow: none;
  transition: transform 0.2s, border-color 0.2s;
  &:hover {
    transform: translateY(-2px);
    border-color: #d7e3f4;
  }
}

// Stats Strip
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-card {
  background: #fff;
  border: 1px solid #e7edf5;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.78rem;
  color: #6b7280;
  line-height: 1.2;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a2332;
}

.table-card {
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table thead th {
  background: #f8fafc;
  color: #4b5563;
  font-size: 0.8rem;
  font-weight: 600;
  border-bottom: 1px solid #e7edf5;
}

.rounded-circle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

// Empty State
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(36,83,167,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;

  .bi { font-size: 2rem; color: #2453a7; }
}

.empty-state h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a2332;
  margin-bottom: 0.5rem;
}

.badge {
  padding: 0.4rem 0.75rem;
}

// Responsive
@media (max-width: 768px) {
  .stats-strip { grid-template-columns: repeat(2, 1fr); }
}
</style>