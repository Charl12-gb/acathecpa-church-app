<template>
  <div class="categories-page">
    <!-- Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h1 class="page-title mb-1">Catégories de cours</h1>
          <p class="page-subtitle mb-0">Gérez les catégories disponibles pour les cours</p>
        </div>
        <button class="btn btn-primary-custom" @click="openCreate">
          <i class="bi bi-plus-lg me-2"></i>Nouvelle catégorie
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card app-card filter-card mb-4">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-transparent"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control" v-model="search" placeholder="Rechercher une catégorie…">
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="card app-card table-card">
      <div class="card-body">
        <div v-if="isLoading" class="text-center py-5 text-muted">
          <div class="spinner-border spinner-border-sm me-2"></div> Chargement…
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Description</th>
                <th>Statut</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cat in filtered" :key="cat.id">
                <td class="fw-semibold">{{ cat.name }}</td>
                <td class="text-muted">{{ cat.description || '—' }}</td>
                <td>
                  <span class="badge" :class="cat.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ cat.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="text-end">
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-custom" @click="openEdit(cat)" title="Modifier">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger-custom" @click="removeCategory(cat)" title="Supprimer">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!filtered.length" class="empty-state">
            <div class="empty-icon"><i class="bi bi-tags"></i></div>
            <h3>Aucune catégorie</h3>
            <p class="text-muted">Créez votre première catégorie.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-backdrop-custom" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-head">
          <h5>{{ editing ? 'Modifier la catégorie' : 'Nouvelle catégorie' }}</h5>
          <button class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body-custom">
          <div v-if="formError" class="alert alert-danger py-2">{{ formError }}</div>
          <div class="mb-3">
            <label class="form-label">Nom <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model="form.name" placeholder="Ex : Théologie & Doctrine">
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea class="form-control" rows="2" v-model="form.description" placeholder="Optionnelle"></textarea>
          </div>
          <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" id="cat_active" v-model="form.is_active">
            <label class="form-check-label" for="cat_active">Catégorie active</label>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-light" @click="closeModal">Annuler</button>
          <button class="btn btn-primary-custom" @click="save" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ editing ? 'Enregistrer' : 'Créer' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../../../services/api/category'
import type { Category } from '../../../types/api'

const categories = ref<Category[]>([])
const isLoading = ref(false)
const search = ref('')

const showModal = ref(false)
const editing = ref<Category | null>(null)
const saving = ref(false)
const formError = ref('')
const form = ref<{ name: string; description: string; is_active: boolean }>({
  name: '', description: '', is_active: true,
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return categories.value
  return categories.value.filter(c => c.name.toLowerCase().includes(q))
})

const fetchCategories = async () => {
  isLoading.value = true
  try {
    categories.value = await getCategories()
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchCategories)

const openCreate = () => {
  editing.value = null
  form.value = { name: '', description: '', is_active: true }
  formError.value = ''
  showModal.value = true
}

const openEdit = (cat: Category) => {
  editing.value = cat
  form.value = { name: cat.name, description: cat.description || '', is_active: cat.is_active }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => { showModal.value = false }

const save = async () => {
  formError.value = ''
  if (!form.value.name.trim()) {
    formError.value = 'Le nom est requis.'
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      const updated = await updateCategory(editing.value.id, { ...form.value })
      const idx = categories.value.findIndex(c => c.id === editing.value!.id)
      if (idx !== -1) categories.value[idx] = updated
    } else {
      const created = await createCategory({ ...form.value })
      categories.value.push(created)
      categories.value.sort((a, b) => a.name.localeCompare(b.name))
    }
    showModal.value = false
  } catch (err: any) {
    formError.value = err.response?.data?.name?.[0] || err.response?.data?.detail || 'Erreur lors de l’enregistrement.'
  } finally {
    saving.value = false
  }
}

const removeCategory = async (cat: Category) => {
  if (!confirm(`Supprimer la catégorie « ${cat.name} » ?`)) return
  try {
    await deleteCategory(cat.id)
    categories.value = categories.value.filter(c => c.id !== cat.id)
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression.')
  }
}
</script>

<style scoped lang="scss">
.categories-page { max-width: 1000px; margin: 0 auto; }
.page-title { font-size: 1.75rem; font-weight: 700; color: #1a2332; }
.page-subtitle { color: #6b7280; font-size: 0.95rem; }
.btn-primary-custom {
  background: #2453a7; color: #fff; border: none; border-radius: 8px;
  padding: 0.5rem 1.2rem; font-weight: 500; font-size: 0.875rem;
  &:hover { background: #1a3f8a; color: #fff; }
}
.btn-outline-custom {
  background: transparent; border: 1px solid #e7edf5; color: #4b5563; border-radius: 6px; font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}
.btn-outline-danger-custom {
  background: transparent; border: 1px solid #fecaca; color: #dc2626; border-radius: 6px; font-size: 0.8rem;
  &:hover { background: #fef2f2; }
}
.app-card { border: 1px solid #e7edf5; border-radius: 12px; box-shadow: none; }
.table { margin-bottom: 0; }
.table thead th { background: #f8fafc; color: #4b5563; font-size: 0.8rem; font-weight: 600; border-bottom: 1px solid #e7edf5; }
.badge { padding: 0.4rem 0.75rem; }
.empty-state { text-align: center; padding: 3rem 2rem; }
.empty-icon {
  width: 80px; height: 80px; border-radius: 50%; background: rgba(36,83,167,0.08);
  display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;
  .bi { font-size: 2rem; color: #2453a7; }
}
.empty-state h3 { font-size: 1.2rem; font-weight: 600; color: #1a2332; margin-bottom: 0.5rem; }

/* Modal */
.modal-backdrop-custom {
  position: fixed; inset: 0; background: rgba(15,23,42,0.5); z-index: 1050;
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.modal-card {
  background: #fff; border-radius: 14px; width: 100%; max-width: 480px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden;
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid #eef2f7;
  h5 { margin: 0; font-weight: 700; color: #1a2332; }
}
.modal-body-custom { padding: 1.25rem; }
.modal-foot {
  display: flex; justify-content: flex-end; gap: 0.5rem;
  padding: 1rem 1.25rem; border-top: 1px solid #eef2f7;
}
.form-check-input:checked { background-color: #2453a7; border-color: #2453a7; }
</style>
