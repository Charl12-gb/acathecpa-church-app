<template>
  <div class="container-fluid py-4 roles-page">
    <h1 class="h3 mb-1">Rôles et permissions</h1>
    <p class="text-muted mb-4">
      Les quatre rôles sont fixes. Vous réglez ce que peuvent faire les étudiants et les professeurs,
      et vous pouvez accorder ou retirer une permission à une personne précise.
    </p>

    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button type="button" class="btn-close" aria-label="Fermer" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>
    </div>

    <template v-else>
      <!-- Matrix -->
      <section class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="d-flex flex-wrap justify-content-between gap-2 mb-3">
            <h2 class="h5 mb-0">Permissions par rôle</h2>
            <label for="perm-search" class="visually-hidden">Filtrer les permissions</label>
            <input id="perm-search" v-model.trim="search" class="form-control form-control-sm" style="max-width: 260px"
              placeholder="Filtrer les permissions">
          </div>
          <p class="small text-muted mb-3">
            <i class="bi bi-lock-fill"></i> L'admin a toutes les permissions sauf la gestion des rôles et des permissions ;
            le super admin a tout. Ces deux colonnes ne se règlent pas.
          </p>
          <div class="table-responsive">
            <table class="table table-sm align-middle matrix">
              <thead>
                <tr>
                  <th>Permission</th>
                  <th v-for="col in columns" :key="col.name" class="text-center">{{ col.label }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="group in groups" :key="group.category">
                  <tr class="table-light"><th :colspan="columns.length + 1" class="small text-uppercase">{{ group.category }}</th></tr>
                  <tr v-for="perm in group.items" :key="perm.id">
                    <td>
                      <div>{{ perm.title }}</div>
                      <code class="small text-muted">{{ perm.permission }}</code>
                    </td>
                    <td v-for="col in columns" :key="col.name" class="text-center">
                      <input v-if="col.editable" type="checkbox" class="form-check-input"
                        :id="`p-${col.name}-${perm.permission}`"
                        :aria-label="`${perm.title} pour ${col.label}`"
                        :checked="hasLink(col.name, perm.id)"
                        :disabled="busy.has(`${col.name}:${perm.id}`)"
                        @change="toggle(col.name, perm)">
                      <i v-else-if="lockedGranted(col.name, perm.permission)" class="bi bi-check-lg text-success"
                        :title="`Toujours accordé au rôle ${col.label}`"></i>
                      <i v-else class="bi bi-dash text-muted" :title="`Jamais accordé au rôle ${col.label}`"></i>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Overrides -->
      <section class="card border-0 shadow-sm">
        <div class="card-body">
          <h2 class="h5">Dérogations individuelles</h2>
          <p class="small text-muted">Ajouter une permission à une personne, ou lui en retirer une que son rôle lui donne.</p>

          <form class="row g-2 align-items-end mb-4" @submit.prevent="createOverride">
            <div class="col-md-4 position-relative">
              <label for="ov-user" class="form-label small">Utilisateur</label>
              <input id="ov-user" v-model.trim="userQuery" class="form-control" placeholder="Nom ou email" autocomplete="off"
                @input="searchUsers">
              <ul v-if="userResults.length && !selectedUser" class="list-group user-results">
                <li v-for="u in userResults" :key="u.id">
                  <button type="button" class="list-group-item list-group-item-action" @click="pickUser(u)">
                    {{ u.name || u.email }} <small class="text-muted">{{ u.email }}</small>
                  </button>
                </li>
              </ul>
            </div>
            <div class="col-md-4">
              <label for="ov-permission" class="form-label small">Permission</label>
              <select id="ov-permission" v-model="overrideForm.permissionId" class="form-select">
                <option value="" disabled>Choisir…</option>
                <optgroup v-for="group in groups" :key="group.category" :label="group.category">
                  <option v-for="perm in group.items" :key="perm.id" :value="perm.id">{{ perm.title }}</option>
                </optgroup>
              </select>
            </div>
            <div class="col-md-2">
              <label for="ov-type" class="form-label small">Action</label>
              <select id="ov-type" v-model="overrideForm.type" class="form-select">
                <option value="Add">Accorder</option>
                <option value="Remove">Retirer</option>
              </select>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary w-100" :disabled="!selectedUser || !overrideForm.permissionId">Ajouter</button>
            </div>
          </form>

          <p v-if="!overrides.length" class="text-muted mb-0">Aucune dérogation.</p>
          <ul v-else class="list-group">
            <li v-for="o in overrides" :key="o.id" class="list-group-item d-flex flex-wrap gap-2 align-items-center">
              <span class="badge" :class="o.type === 'Add' ? 'bg-success' : 'bg-danger'">{{ o.type === 'Add' ? 'Accordée' : 'Retirée' }}</span>
              <strong>{{ o.permission.title }}</strong>
              <span class="text-muted">pour {{ o.user_name || o.user_email }} ({{ o.user_email }})</span>
              <button type="button" class="btn btn-sm btn-outline-danger ms-auto" @click="deleteOverride(o)">Supprimer</button>
            </li>
          </ul>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  getRoles, getPermissionDefinitions, getRolePermissions, grantRolePermission, revokeRolePermission,
  getUserOverrides, addUserOverride, removeUserOverride,
  type PermissionItem, type RoleItem, type RolePermissionLink, type UserOverride,
} from '../../../services/api/permissions';
import { getUsers } from '../../../services/api/user';

// Same list as SUPER_ADMIN_ONLY_PERMISSIONS on the server: never given to admins.
const SUPER_ADMIN_ONLY = new Set([
  'create_role', 'edit_role', 'delete_role', 'assign_permission_to_role', 'remove_permission_from_role',
  'create_permission_def', 'edit_permission_def', 'delete_permission_def',
  'assign_user_permission_override', 'remove_user_permission_override',
]);

const columns = [
  { name: 'student', label: 'Étudiant', editable: true },
  { name: 'professor', label: 'Professeur', editable: true },
  { name: 'admin', label: 'Admin', editable: false },
  { name: 'super_admin', label: 'Super admin', editable: false },
];

const loading = ref(true);
const error = ref('');
const search = ref('');
const roles = ref<RoleItem[]>([]);
const permissions = ref<PermissionItem[]>([]);
const links = ref<RolePermissionLink[]>([]);
const overrides = ref<UserOverride[]>([]);
const busy = ref(new Set<string>());

const roleId = (name: string) => roles.value.find(r => r.name === name)?.id;
const linkFor = (roleName: string, permId: string) =>
  links.value.find(l => l.role.name === roleName && l.permission.id === permId);
const hasLink = (roleName: string, permId: string) => !!linkFor(roleName, permId);
const lockedGranted = (roleName: string, permName: string) =>
  roleName === 'super_admin' || (roleName === 'admin' && !SUPER_ADMIN_ONLY.has(permName));

const groups = computed(() => {
  const q = search.value.toLowerCase();
  const byCategory = new Map<string, PermissionItem[]>();
  for (const p of permissions.value) {
    if (q && !p.title.toLowerCase().includes(q) && !p.permission.includes(q)) continue;
    byCategory.set(p.category, [...(byCategory.get(p.category) ?? []), p]);
  }
  return [...byCategory].map(([category, items]) => ({ category, items }));
});

const apiError = (err: any, fallback: string) => err.response?.data?.detail || fallback;

const toggle = async (roleName: string, perm: PermissionItem) => {
  const key = `${roleName}:${perm.id}`;
  busy.value.add(key);
  try {
    const existing = linkFor(roleName, perm.id);
    if (existing) {
      await revokeRolePermission(existing.id);
      links.value = links.value.filter(l => l.id !== existing.id);
    } else {
      links.value.push(await grantRolePermission(roleId(roleName)!, perm.id));
    }
  } catch (err: any) {
    error.value = apiError(err, 'La permission n\'a pas pu être modifiée.');
  } finally {
    busy.value.delete(key);
  }
};

// --- Overrides ---
const userQuery = ref('');
const userResults = ref<any[]>([]);
const selectedUser = ref<any | null>(null);
const overrideForm = ref<{ permissionId: string; type: 'Add' | 'Remove' }>({ permissionId: '', type: 'Add' });
let searchTimer: ReturnType<typeof setTimeout> | undefined;

const searchUsers = () => {
  selectedUser.value = null;
  clearTimeout(searchTimer);
  if (userQuery.value.length < 2) { userResults.value = []; return; }
  searchTimer = setTimeout(async () => {
    userResults.value = (await getUsers('', 0, 10, { search: userQuery.value })).slice(0, 8);
  }, 250);
};

const pickUser = (u: any) => {
  selectedUser.value = u;
  userQuery.value = u.email;
  userResults.value = [];
};

const createOverride = async () => {
  if (!selectedUser.value) return;
  try {
    overrides.value.unshift(await addUserOverride(selectedUser.value.id, overrideForm.value.permissionId, overrideForm.value.type));
    selectedUser.value = null;
    userQuery.value = '';
    overrideForm.value.permissionId = '';
  } catch (err: any) {
    error.value = apiError(err, 'La dérogation n\'a pas pu être ajoutée.');
  }
};

const deleteOverride = async (o: UserOverride) => {
  try {
    await removeUserOverride(o.id);
    overrides.value = overrides.value.filter(x => x.id !== o.id);
  } catch (err: any) {
    error.value = apiError(err, 'La dérogation n\'a pas pu être supprimée.');
  }
};

onMounted(async () => {
  try {
    [roles.value, permissions.value, links.value, overrides.value] = await Promise.all([
      getRoles(), getPermissionDefinitions(), getRolePermissions(), getUserOverrides(),
    ]);
  } catch (err: any) {
    error.value = apiError(err, 'Impossible de charger les rôles et permissions.');
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.roles-page { max-width: 1100px; }
.matrix th:not(:first-child), .matrix td:not(:first-child) { width: 110px; }
.user-results {
  position: absolute;
  z-index: 10;
  left: 4px;
  right: 4px;
  max-height: 240px;
  overflow-y: auto;
  padding: 0;
  list-style: none;
}
.user-results button { width: 100%; text-align: left; }
</style>
