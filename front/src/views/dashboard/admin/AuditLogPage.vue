<template>
  <div class="container-fluid py-4" style="max-width: 1100px">
    <h1 class="h3 mb-1">Journal d'audit</h1>
    <p class="text-muted mb-4">Changements de rôle, désactivations, suppressions et réglages des permissions, du plus récent au plus ancien.</p>

    <form class="d-flex flex-wrap gap-2 mb-3" @submit.prevent="load">
      <label for="audit-action" class="visually-hidden">Type d'action</label>
      <select id="audit-action" v-model="action" class="form-select" style="max-width: 320px" @change="load">
        <option value="">Toutes les actions</option>
        <option v-for="(label, value) in ACTIONS" :key="value" :value="value">{{ label }}</option>
      </select>
      <label for="audit-search" class="visually-hidden">Rechercher</label>
      <input id="audit-search" v-model.trim="q" class="form-control" style="max-width: 260px" placeholder="Auteur ou compte visé">
      <button type="submit" class="btn btn-outline-primary">Rechercher</button>
    </form>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>
    </div>
    <p v-else-if="!entries.length" class="text-muted">Aucune action enregistrée.</p>

    <div v-else class="table-responsive card border-0 shadow-sm">
      <table class="table align-middle mb-0">
        <thead class="table-light">
          <tr><th>Date</th><th>Auteur</th><th>Action</th><th>Visé</th><th>Détails</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in entries" :key="e.id">
            <td class="text-nowrap small">{{ formatDate(e.created_at) }}</td>
            <td class="small">{{ e.actor_email || '—' }}</td>
            <td>{{ e.action_label }}</td>
            <td class="small">{{ e.target_label }}</td>
            <td class="small text-muted">{{ describe(e) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getAuditLogs, type AuditEntry } from '../../../services/api/audit';

const ACTIONS: Record<string, string> = {
  'user.role_changed': 'Changement de rôle',
  'user.deactivated': 'Compte désactivé',
  'user.reactivated': 'Compte réactivé',
  'user.password_reset': 'Mot de passe modifié par un administrateur',
  'user.deleted': 'Compte supprimé',
  'user.deleted_with_data': 'Compte supprimé définitivement avec ses données',
  'role.permission_granted': 'Permission accordée à un rôle',
  'role.permission_revoked': 'Permission retirée à un rôle',
  'user.permission_override_added': 'Dérogation ajoutée',
  'user.permission_override_removed': 'Dérogation supprimée',
};
const HISTORY: Record<string, string> = {
  enrollments: 'inscription(s)', payments: 'paiement(s)', certificates: 'certificat(s)', courses: 'cours',
  course_enrollments: 'inscription(s) à ses cours', contents: 'contenu(s)', live_sessions: 'session(s)',
};

const entries = ref<AuditEntry[]>([]);
const loading = ref(true);
const error = ref('');
const action = ref('');
const q = ref('');

const formatDate = (iso: string) => new Date(iso).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' });

const describe = (e: AuditEntry) => {
  const d = e.details || {};
  if (d.old !== undefined) return `${d.old ?? 'aucun'} → ${d.new ?? 'aucun'}`;
  if (d.history) {
    const parts = Object.entries(d.history as Record<string, number>).filter(([, n]) => n).map(([k, n]) => `${n} ${HISTORY[k] ?? k}`);
    return parts.length ? parts.join(', ') : 'aucun historique';
  }
  if (d.permission) return d.type ? `${d.permission} (${d.type === 'Add' ? 'accordée' : 'retirée'})` : d.permission;
  return '';
};

const load = async () => {
  loading.value = true;
  error.value = '';
  try {
    entries.value = await getAuditLogs({ action: action.value || undefined, q: q.value || undefined });
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Impossible de charger le journal.';
  } finally {
    loading.value = false;
  }
};

onMounted(load);
</script>
