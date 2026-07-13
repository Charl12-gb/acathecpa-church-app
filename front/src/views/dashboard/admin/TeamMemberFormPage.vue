<template>
  <div class="team-form-page">
    <div class="page-header mb-4 d-flex align-items-center gap-3">
      <button class="btn-back" @click="router.push('/manage-team')" title="Retour">
        <i class="bi bi-arrow-left"></i>
      </button>
      <div>
        <h1 class="page-title mb-1">{{ isEdit ? 'Modifier le membre' : 'Nouveau membre' }}</h1>
        <p class="page-subtitle mb-0">Informations affichées dans « Notre équipe »</p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5 text-muted">
      <div class="spinner-border spinner-border-sm me-2"></div> Chargement…
    </div>

    <div v-else class="card app-card">
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div class="row g-3">
          <div class="col-md-8">
            <div class="mb-3">
              <label class="form-label">Nom complet <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="form.name" placeholder="Ex : Dr. Jean Dupont">
            </div>
            <div class="mb-3">
              <label class="form-label">Fonction / rôle <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="form.title" placeholder="Ex : Directeur académique">
            </div>
            <div class="mb-3">
              <label class="form-label">Biographie</label>
              <textarea class="form-control" rows="3" v-model="form.bio" placeholder="Courte présentation (optionnelle)"></textarea>
            </div>
          </div>

          <div class="col-md-4">
            <label class="form-label">Photo</label>
            <FileUploader
              v-model="form.photo_url"
              category="image"
              accept="image/*"
              help-text="PNG, JPG (max 10 Mo)"
            />
          </div>
        </div>

        <hr class="my-4">
        <h6 class="section-label mb-3"><i class="bi bi-share me-2"></i>Réseaux sociaux</h6>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label"><i class="bi bi-linkedin me-1 text-primary"></i>LinkedIn</label>
            <input type="url" class="form-control" v-model="form.social_links.linkedin" placeholder="https://linkedin.com/in/…">
          </div>
          <div class="col-md-6">
            <label class="form-label"><i class="bi bi-twitter-x me-1"></i>Twitter / X</label>
            <input type="url" class="form-control" v-model="form.social_links.twitter" placeholder="https://x.com/…">
          </div>
          <div class="col-md-6">
            <label class="form-label"><i class="bi bi-facebook me-1 text-primary"></i>Facebook</label>
            <input type="url" class="form-control" v-model="form.social_links.facebook" placeholder="https://facebook.com/…">
          </div>
          <div class="col-md-6">
            <label class="form-label"><i class="bi bi-envelope me-1"></i>Email</label>
            <input type="email" class="form-control" v-model="form.social_links.email" placeholder="prenom@exemple.com">
          </div>
        </div>

        <hr class="my-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label">Ordre d'affichage</label>
            <input type="number" class="form-control" v-model.number="form.order" min="0">
          </div>
          <div class="col-md-8">
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" id="member_active" v-model="form.is_active">
              <label class="form-check-label" for="member_active">Afficher sur la page d'accueil</label>
            </div>
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-4">
          <button class="btn btn-light" @click="router.push('/manage-team')">Annuler</button>
          <button class="btn btn-primary-custom" @click="save" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ isEdit ? 'Enregistrer' : 'Créer le membre' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTeamMember, createTeamMember, updateTeamMember } from '../../../services/api/team'
import type { TeamMemberSocialLinks } from '../../../types/api'
const FileUploader = defineAsyncComponent(() => import('../../../components/FileUploader.vue'))

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const isLoading = ref(false)
const saving = ref(false)
const error = ref('')

const form = ref<{
  name: string; title: string; photo_url: string | null; bio: string;
  social_links: TeamMemberSocialLinks; order: number; is_active: boolean;
}>({
  name: '', title: '', photo_url: null, bio: '',
  social_links: {}, order: 0, is_active: true,
})

onMounted(async () => {
  if (!isEdit.value) return
  isLoading.value = true
  try {
    const m = await getTeamMember(Number(route.params.id))
    form.value = {
      name: m.name, title: m.title, photo_url: m.photo_url || null, bio: m.bio || '',
      social_links: m.social_links || {}, order: m.order, is_active: m.is_active,
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Membre introuvable.'
  } finally {
    isLoading.value = false
  }
})

const save = async () => {
  error.value = ''
  if (!form.value.name.trim() || !form.value.title.trim()) {
    error.value = 'Le nom et la fonction sont requis.'
    return
  }
  saving.value = true
  try {
    const payload = { ...form.value }
    if (isEdit.value) {
      await updateTeamMember(Number(route.params.id), payload)
    } else {
      await createTeamMember(payload)
    }
    router.push('/manage-team')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Erreur lors de l’enregistrement.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.team-form-page { max-width: 860px; margin: 0 auto; }
.page-title { font-size: 1.6rem; font-weight: 700; color: #1a2332; }
.page-subtitle { color: #6b7280; font-size: 0.9rem; }
.btn-back {
  width: 40px; height: 40px; border-radius: 10px; border: 1px solid #e7edf5;
  background: #f6f8fc; color: #1a2332; display: grid; place-items: center; cursor: pointer;
  &:hover { background: #eaf2ff; color: #2453a7; border-color: #2453a7; }
}
.app-card { border: 1px solid #e7edf5; border-radius: 12px; box-shadow: none; }
.section-label { font-weight: 700; color: #1a2332; font-size: 0.95rem; }
.btn-primary-custom {
  background: #2453a7; color: #fff; border: none; border-radius: 8px;
  padding: 0.5rem 1.4rem; font-weight: 500; font-size: 0.875rem;
  &:hover { background: #1a3f8a; color: #fff; }
}
.form-check-input:checked { background-color: #2453a7; border-color: #2453a7; }
</style>
