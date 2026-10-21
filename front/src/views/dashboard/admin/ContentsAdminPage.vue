<template>
  <div class="container-fluid py-4" style="max-width: 1150px">
    <div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-1">
      <h1 class="h3 mb-0">Tous les contenus</h1>
      <RouterLink to="/content/editor" class="btn btn-primary btn-sm"><i class="bi bi-plus-lg me-1"></i>Nouveau contenu</RouterLink>
    </div>
    <p class="text-muted mb-4">Articles et podcasts de tous les auteurs : modifiez-les, changez leur statut ou supprimez-les.</p>

    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button type="button" class="btn-close" aria-label="Fermer" @click="error = ''"></button>
    </div>

    <form class="d-flex flex-wrap gap-2 mb-3" @submit.prevent="load">
      <label for="contents-search" class="visually-hidden">Rechercher</label>
      <input id="contents-search" v-model.trim="q" class="form-control" style="max-width: 280px" placeholder="Titre, auteur ou email">
      <label for="contents-status" class="visually-hidden">Statut</label>
      <select id="contents-status" v-model="status" class="form-select" style="max-width: 180px" @change="load">
        <option value="">Tous les statuts</option>
        <option value="published">Publiés</option>
        <option value="draft">Brouillons</option>
      </select>
      <label for="contents-type" class="visually-hidden">Type</label>
      <select id="contents-type" v-model="type" class="form-select" style="max-width: 180px" @change="load">
        <option value="">Articles et podcasts</option>
        <option value="article">Articles</option>
        <option value="podcast">Podcasts</option>
      </select>
      <button type="submit" class="btn btn-outline-primary">Rechercher</button>
    </form>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>
    </div>
    <p v-else-if="!contents.length" class="text-muted">Aucun contenu ne correspond.</p>

    <div v-else class="table-responsive card border-0 shadow-sm">
      <table class="table align-middle mb-0">
        <thead class="table-light">
          <tr><th>Contenu</th><th>Auteur</th><th>Statut</th><th>Mis à jour</th><th class="text-end">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in contents" :key="c.id">
            <td>
              <div class="fw-semibold">{{ c.title }}</div>
              <small class="text-muted">
                {{ c.type === 'podcast' ? 'Podcast' : 'Article' }} · {{ FORMATS[c.format ?? 'text'] || c.format }}
                <span v-if="c.is_premium" class="badge bg-warning text-dark ms-1">Premium {{ c.price }} XOF</span>
              </small>
            </td>
            <td class="small">{{ c.author_name || c.author?.name || '—' }}</td>
            <td style="min-width: 150px">
              <label :for="`status-${c.id}`" class="visually-hidden">Statut de {{ c.title }}</label>
              <select :id="`status-${c.id}`" class="form-select form-select-sm" :value="c.status"
                :disabled="busyId === c.id" @change="changeStatus(c, ($event.target as HTMLSelectElement).value)">
                <option value="draft">Brouillon</option>
                <option value="published">Publié</option>
              </select>
            </td>
            <td class="small text-nowrap">{{ formatDate(c.updated_at) }}</td>
            <td class="text-end text-nowrap">
              <RouterLink v-if="c.status === 'published'" :to="publicLink(c)" class="btn btn-sm btn-link" title="Voir sur le site">Voir</RouterLink>
              <RouterLink :to="`/content/editor/${c.id}?back=manage`" class="btn btn-sm btn-outline-primary">Modifier</RouterLink>
              <button type="button" class="btn btn-sm btn-outline-danger ms-1" @click="askDelete(c)">Supprimer</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Deletion confirmation -->
    <div v-if="toDelete" class="del-backdrop" @click.self="toDelete = null">
      <div class="del-dialog" role="dialog" aria-modal="true" aria-labelledby="content-del-title">
        <h5 id="content-del-title">Supprimer « {{ toDelete.title }} » ?</h5>
        <p class="text-muted">Le contenu de {{ toDelete.author_name || 'cet auteur' }} sera supprimé définitivement.</p>
        <div class="d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-light" @click="toDelete = null">Annuler</button>
          <button type="button" class="btn btn-danger" :disabled="busyId === toDelete.id" @click="confirmDelete">Supprimer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getAllContentsForAdmin, updateContentStatus, deleteContent, type AdminContentRow } from '../../../services/api/content';

const FORMATS: Record<string, string> = { text: 'texte', audio: 'audio', video: 'vidéo', pdf: 'PDF' };

const contents = ref<AdminContentRow[]>([]);
const loading = ref(true);
const error = ref('');
const q = ref('');
const status = ref('');
const type = ref('');
const busyId = ref<number | null>(null);
const toDelete = ref<AdminContentRow | null>(null);

const formatDate = (iso: string) => new Date(iso).toLocaleDateString('fr-FR', { dateStyle: 'medium' });
const publicLink = (c: AdminContentRow) => (c.type === 'podcast' ? `/podcasts/${c.id}` : `/articles/${c.id}`);
const apiError = (err: any, fallback: string) => err.response?.data?.detail || fallback;

const load = async () => {
  loading.value = true;
  try {
    contents.value = await getAllContentsForAdmin({ q: q.value || undefined, status: status.value || undefined, type: type.value || undefined });
  } catch (err: any) {
    error.value = apiError(err, 'Impossible de charger les contenus.');
  } finally {
    loading.value = false;
  }
};

const changeStatus = async (c: AdminContentRow, next: string) => {
  busyId.value = c.id;
  try {
    const updated = await updateContentStatus(c.id, next as AdminContentRow['status']);
    c.status = updated.status;
    c.updated_at = updated.updated_at;
  } catch (err: any) {
    error.value = apiError(err, 'Le statut n\'a pas pu être modifié.');
  } finally {
    busyId.value = null;
  }
};

const askDelete = (c: AdminContentRow) => { toDelete.value = c; };

const confirmDelete = async () => {
  const target = toDelete.value;
  if (!target) return;
  busyId.value = target.id;
  try {
    await deleteContent(target.id);
    contents.value = contents.value.filter(c => c.id !== target.id);
    toDelete.value = null;
  } catch (err: any) {
    error.value = apiError(err, 'Le contenu n\'a pas pu être supprimé.');
  } finally {
    busyId.value = null;
  }
};

onMounted(load);
</script>

<style scoped>
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
  max-width: 460px;
}
</style>
