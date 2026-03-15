<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useProfessorStore } from '../../../stores/professor';
import { storeToRefs } from 'pinia';
import { Professor } from '../../../types/api/professorTypes';
import { fetchAdminProfessors } from '../../../services/api/adminDashboardService';
import type { ProfessorStat } from '../../../types/api/admin_dashboard';

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

const professorInsights = ref<Record<number, ProfessorStat>>({});

const loadProfessorInsights = async () => {
  const stats = await fetchAdminProfessors();
  professorInsights.value = stats.reduce<Record<number, ProfessorStat>>((acc, item) => {
    acc[item.id] = item;
    return acc;
  }, {});
};

// Filters (local to component)
const filters = ref({
  status: 'all', // 'all', 'active', 'inactive'
  search: '',
  sort: 'name' // name, specialization
});

onMounted(async () => {
  await Promise.all([fetchProfessors(), loadProfessorInsights()]);
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
      delete professorInsights.value[userId];
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
      await loadProfessorInsights();
      alert(`Statut du professeur mis à jour.`);
      // Store action updates the professor in the list.
    } catch (err: any) {
      console.error('Error toggling professor status from component:', err);
      alert(err.message || 'Erreur lors du changement de statut.');
    }
  }
};


const profRows = computed(() => filteredProfessors.value.map((professor) => {
  const insight = professorInsights.value[professor.id];
  return {
    ...professor,
    courses_count: insight?.courses_count ?? 0,
    published_courses_count: insight?.published_courses_count ?? 0,
    students_count: insight?.students_count ?? 0,
    active_students_count: insight?.active_students_count ?? 0,
    latest_course_published_at: insight?.latest_course_published_at ?? null,
    specialization: insight?.specialization ?? professor.professor_profile?.specialization ?? null,
  };
}));

</script>

<template>
  <div class="container-fluid">
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
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white py-3 px-4 d-flex justify-content-between align-items-center border-bottom">
          <h5 class="mb-0">Liste des professeurs</h5>
          <span class="result-pill">{{ filteredProfessors.length }} resultat(s)</span>
        </div>

        <div class="prof-table-wrap">
          <table class="table table-hover align-middle mb-0 prof-table">
            <thead>
              <tr>
                <th>Professeur</th>
                <th>Contact</th>
                <th>Specialisation</th>
                <th>Statut</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="professor in profRows" :key="professor.id">
                <td>
                  <div class="d-flex align-items-center gap-3">
                    <div class="avatar-placeholder rounded-circle bg-primary text-white d-flex align-items-center justify-content-center">
                      <span class="fs-6 fw-bold">{{ professor.name ? professor.name.charAt(0).toUpperCase() : 'P' }}</span>
                    </div>
                    <div class="prof-ident">
                      <div class="fw-semibold text-dark">{{ professor.name || 'N/A' }}</div>
                      <small class="text-muted">
                        Inscrit le {{ professor.created_at ? new Date(professor.created_at).toLocaleDateString() : 'N/A' }}
                      </small>
                    </div>
                  </div>
                </td>

                <td>
                  <div class="small fw-medium">{{ professor.email }}</div>
                  <div class="small text-muted">{{ professor.phone || 'Téléphone non renseigné' }}</div>
                  <div class="small text-muted">{{ professor.country || 'Pays non renseigné' }}</div>
                </td>

                <td>
                  <span class="spec-pill">
                    {{ professor.specialization || 'Non specifiee' }}
                  </span>
                  <div class="small text-muted mt-2">
                    <i class="bi bi-journal-check me-1"></i>
                    {{ professor.published_courses_count }} cours publies / {{ professor.courses_count }} total
                  </div>
                  <div class="small text-muted">
                    <i class="bi bi-people me-1"></i>
                    {{ professor.active_students_count }} etudiants actifs / {{ professor.students_count }} inscrits
                  </div>
                  <div v-if="professor.latest_course_published_at" class="small text-muted">
                    <i class="bi bi-calendar-event me-1"></i>
                    Derniere publication: {{ new Date(professor.latest_course_published_at).toLocaleDateString() }}
                  </div>
                </td>

                <td>
                  <span :class="[
                    'status-pill',
                    professor.is_active ? 'status-active' : 'status-inactive'
                  ]">
                    <i :class="['bi me-1', professor.is_active ? 'bi-check-circle' : 'bi-pause-circle']"></i>
                    {{ professor.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>

                <td class="text-end">
                  <div class="btn-group btn-group-sm">
                    <RouterLink
                      :to="{ name: 'professor-detail', params: { id: professor.id } }"
                      class="btn btn-outline-info"
                      title="Details"
                    >
                      <i class="bi bi-eye"></i>
                    </RouterLink>
                    <RouterLink
                      :to="{ name: 'professor-form', params: { id: professor.id } }"
                      class="btn btn-outline-primary"
                      title="Modifier"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </RouterLink>
                    <button
                      class="btn btn-outline-secondary"
                      @click="handleToggleStatus(professor)"
                      :title="professor.is_active ? 'Desactiver' : 'Activer'"
                    >
                      <i :class="['bi', professor.is_active ? 'bi-toggle-on' : 'bi-toggle-off']"></i>
                    </button>
                    <button
                      class="btn btn-outline-danger"
                      @click="handleDeleteProfessor(professor.id)"
                      title="Supprimer"
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

.result-pill {
  padding: 0.32rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #f6f8fc;
  border: 1px solid #e6ebf3;
  color: #43536b;
}

.prof-table-wrap {
  overflow-x: auto;
}

.prof-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8fafc;
  color: #5b6b84;
  border-bottom: 1px solid #e7edf5;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 700;
  white-space: nowrap;
}

.prof-table tbody tr {
  border-bottom: 1px solid #eef3f8;
}

.prof-table tbody tr:nth-child(even) {
  background: #fcfdff;
}

.prof-table tbody tr:hover {
  background: #f6faff;
}

.prof-ident {
  min-width: 180px;
}

.spec-pill {
  display: inline-block;
  padding: 0.28rem 0.7rem;
  border-radius: 999px;
  border: 1px solid #d7e4ff;
  background: #eff5ff;
  color: #2453a7;
  font-size: 0.78rem;
  font-weight: 600;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.28rem 0.64rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-active {
  color: #18794e;
  background: #eaf8f1;
  border: 1px solid #c7efd9;
}

.status-inactive {
  color: #b02a37;
  background: #fdecef;
  border: 1px solid #f8c6cd;
}

.card {
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1)!important; /* Enhanced shadow on hover */
}

.input-group-text {
  border-right: 0; /* For seamless search input */
}
.form-control.border-start-0 {
  border-left:0;
}

@media (max-width: 991.98px) {
  .prof-table {
    min-width: 760px;
  }
}

</style>