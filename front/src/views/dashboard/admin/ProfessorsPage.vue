<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useProfessorStore } from '../../../stores/professor';
import { storeToRefs } from 'pinia';
import { Professor } from '../../../types/api/professorTypes';

const professorStore = useProfessorStore();

const {
  professors: professorList, // Using 'professors' from store, can alias if needed e.g. professors: storeProfessors
  isLoadingList,
  errorList
} = storeToRefs(professorStore);

const {
  fetchProfessors,
  deleteProfessor: storeDeleteProfessor,      // Aliased to avoid naming conflict
  toggleProfessorStatus: storeToggleProfessorStatus // Aliased
} = professorStore;

// Filters (local to component)
const filters = ref({
  status: 'all', // 'all', 'active', 'inactive'
  search: '',
  sort: 'name' // name, specialization
});

onMounted(() => {
  fetchProfessors();
});

const filteredProfessors = computed(() => {
  // Use professorList from storeToRefs directly
  let filtered = [...professorList.value];

  // Status filter
  if (filters.value.status !== 'all') {
    const isActive = filters.value.status === 'active';
    filtered = filtered.filter(prof => prof.is_active === isActive);
  }

  // Search filter
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    filtered = filtered.filter(prof =>
      (prof.name && prof.name.toLowerCase().includes(search)) ||
      prof.email.toLowerCase().includes(search) ||
      (prof.professor_profile?.specialization && prof.professor_profile.specialization.toLowerCase().includes(search))
    );
  }

  // Sorting
  switch (filters.value.sort) {
    case 'specialization':
      filtered.sort((a, b) =>
        (a.professor_profile?.specialization || '').localeCompare(b.professor_profile?.specialization || '')
      );
      break;
    case 'name':
    default:
      filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  }
  return filtered;
});

// Delete professor action
const handleDeleteProfessor = async (userId: number) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur professeur ? Cette action est irréversible.')) {
    try {
      await storeDeleteProfessor(userId);
      alert('Professeur supprimé avec succès.');
      // The store action already removes the professor from the list,
      // so no need to manually filter professorList.value here.
    } catch (err: any) {
      // Error is already set in store's errorList/errorItem, can use that in template
      // Or display a local alert/notification
      console.error('Error deleting professor from component:', err);
      alert(err.message || 'Erreur lors de la suppression du professeur.');
    }
  }
};

// Toggle professor status action
const handleToggleStatus = async (professor: Professor) => {
  const newStatus = !professor.is_active;
  const alertMessage = `Êtes-vous sûr de vouloir ${newStatus ? 'activer' : 'désactiver'} ce professeur ?`;

  if (confirm(alertMessage)) {
    try {
      await storeToggleProfessorStatus(professor.id, professor.is_active);
      alert(`Statut du professeur mis à jour.`);
      // Store action updates the professor in the list.
    } catch (err: any) {
      console.error('Error toggling professor status from component:', err);
      alert(err.message || 'Erreur lors du changement de statut.');
    }
  }
};


// Computed Stats
const totalProfessors = computed(() => professorList.value.length); // Uses store-managed list
const totalCoursesPublished = computed(() => 0); // Placeholder - data not in store/model
const totalStudents = computed(() => 0); // Placeholder
const averageRating = computed(() => "N/A"); // Placeholder

</script>

<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">Gestion des Professeurs</h1>
            <p class="text-muted mb-0">Gérez les professeurs et leurs accès</p>
          </div>
          <RouterLink :to="{ name: 'professor-form' }" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Ajouter un professeur
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoadingList" class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Chargement des professeurs...</p>
    </div>

    <!-- Error State -->
    <div v-if="errorList" class="alert alert-danger" role="alert">
      <strong>Erreur :</strong> {{ errorList }}
    </div>

    <!-- Content when not loading and no error -->
    <template v-if="!isLoadingList && !errorList">
      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                  <i class="bi bi-person-workspace text-primary fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Total professeurs</h6>
                  <h3 class="mb-0">{{ totalProfessors }}</h3>
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
                  <i class="bi bi-book text-success fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Cours publiés (fictif)</h6>
                  <h3 class="mb-0">{{ totalCoursesPublished }}</h3>
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
                  <i class="bi bi-people text-warning fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Total étudiants (fictif)</h6>
                  <h3 class="mb-0">{{ totalStudents }}</h3>
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
                  <i class="bi bi-star text-info fs-4"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-muted">Note moyenne</h6>
                  <h3 class="mb-0">{{ averageRating }}</h3>
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
                    <span class="input-group-text bg-transparent border-end-0">
                      <i class="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control border-start-0"
                      v-model="filters.search"
                      placeholder="Rechercher (nom, email, spécialisation)..."
                    >
                  </div>
                </div>
                <div class="col-md-4">
                  <select v-model="filters.status" class="form-select">
                    <option value="all">Tous les statuts</option>
                    <option value="active">Actifs</option>
                    <option value="inactive">Inactifs</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <select v-model="filters.sort" class="form-select">
                    <option value="name">Trier par Nom</option>
                    <option value="specialization">Trier par Spécialisation</option>
                    <!-- Add other sort options if data becomes available -->
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Professors List -->
      <div class="row g-4">
        <div v-for="professor in filteredProfessors" :key="professor.id" class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body p-4">
              <div class="row align-items-center">
                <div class="col-md-3">
                  <div class="d-flex align-items-center mb-3 mb-md-0">
                    <div class="avatar-placeholder rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3">
                      <span class="fs-5 fw-bold">{{ professor.name ? professor.name.charAt(0).toUpperCase() : 'P' }}</span>
                    </div>
                    <div>
                      <h5 class="mb-0 fs-6 fw-semibold">{{ professor.name || 'N/A' }}</h5>
                      <p class="mb-0 text-muted small">{{ professor.professor_profile?.specialization || 'Non spécifiée' }}</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-1 small">
                    <i class="bi bi-envelope me-2 text-muted"></i>
                    {{ professor.email }}
                  </div>
                  <div class="small">
                    <i class="bi bi-telephone me-2 text-muted"></i>
                    {{ professor.phone || 'N/A' }}
                  </div>
                </div>
                <div class="col-md-2 text-center">
                   <!-- Placeholder for stats like Courses/Students if data were available -->
                   <div class="py-2 rounded bg-light">
                     <small class="text-muted d-block">Profil</small>
                     <RouterLink :to="{ name: 'professor-form', params: { id: professor.id } }" class="fw-semibold">
                        Voir/Modifier
                     </RouterLink>
                   </div>
                </div>
                <div class="col-md-1 text-center">
                   <span
                    :class="[
                      'badge fs-xs',
                      professor.is_active ? 'bg-success-subtle text-success-emphasis' : 'bg-danger-subtle text-danger-emphasis'
                    ]"
                  >
                    {{ professor.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </div>
                <div class="col-md-3">
                  <div class="d-flex justify-content-end align-items-center gap-2">
                    <RouterLink
                      :to="{ name: 'professor-form', params: { id: professor.id } }"
                      class="btn btn-sm btn-outline-secondary"
                      title="Modifier"
                    >
                      <i class="bi bi-pencil"></i>
                    </RouterLink>
                    <button
                      class="btn btn-sm btn-outline-secondary"
                      @click="handleToggleStatus(professor)"
                      :title="professor.is_active ? 'Désactiver' : 'Activer'"
                    >
                      <i :class="['bi', professor.is_active ? 'bi-toggle-on' : 'bi-toggle-off']"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="handleDeleteProfessor(professor.id)"
                      title="Supprimer"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State for filtered list -->
      <div v-if="!isLoadingList && filteredProfessors.length === 0 && !errorList" class="text-center py-5 mt-4">
        <div class="mb-3">
          <i class="bi bi-people display-4 text-muted"></i>
        </div>
        <h4>Aucun professeur ne correspond à vos critères</h4>
        <p class="text-muted">Essayez d'ajuster vos filtres ou <RouterLink :to="{ name: 'professor-form' }">ajoutez un nouveau professeur</RouterLink>.</p>
      </div>
    </template> <!-- End of v-if="!isLoadingList && !errorList" -->
  </div>
</template>

<style scoped>
.avatar-placeholder {
  width: 48px; /* Standardized avatar size */
  height: 48px;
}

.badge.fs-xs { /* Custom small badge */
  font-size: 0.75em;
  padding: 0.4em 0.6em;
}

.card {
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1)!important; /* Enhanced shadow on hover */
}

/* Make stat cards slightly smaller if needed, or adjust padding */
.card-body .d-flex .rounded-circle { /* Specific to stats cards icons */
  width: 40px;
  height: 40px;
}
.card-body .d-flex h3 { /* Specific to stats cards numbers */
  font-size: 1.5rem;
}
.input-group-text {
  border-right: 0; /* For seamless search input */
}
.form-control.border-start-0 {
  border-left:0;
}

</style>