<template>
  <div class="team-page">
    <!-- Header -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h1 class="page-title mb-1">Notre équipe</h1>
          <p class="page-subtitle mb-0">Gérez les membres affichés sur la page d'accueil</p>
        </div>
        <RouterLink to="/team-form" class="btn btn-primary-custom">
          <i class="bi bi-plus-lg me-2"></i>Ajouter un membre
        </RouterLink>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5 text-muted">
      <div class="spinner-border spinner-border-sm me-2"></div> Chargement…
    </div>

    <!-- Grid -->
    <div v-else-if="members.length" class="members-grid">
      <div v-for="m in members" :key="m.id" class="member-card" :class="{ inactive: !m.is_active }">
        <div class="member-photo">
          <img v-if="m.photo_url" :src="resolveMediaUrl(m.photo_url)" :alt="m.name">
          <span v-else class="member-initials">{{ initials(m.name) }}</span>
        </div>
        <div class="member-info">
          <h5 class="member-name">{{ m.name }}</h5>
          <p class="member-title">{{ m.title }}</p>
          <span v-if="!m.is_active" class="badge bg-secondary">Masqué</span>
        </div>
        <div class="member-actions">
          <RouterLink :to="`/team-form/${m.id}`" class="btn btn-sm btn-outline-custom" title="Modifier">
            <i class="bi bi-pencil"></i>
          </RouterLink>
          <button class="btn btn-sm btn-outline-danger-custom" @click="removeMember(m)" title="Supprimer">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="empty-state">
      <div class="empty-icon"><i class="bi bi-people"></i></div>
      <h3>Aucun membre</h3>
      <p class="text-muted">Ajoutez les membres de votre équipe.</p>
      <RouterLink to="/team-form" class="btn btn-primary-custom">
        <i class="bi bi-plus-lg me-2"></i>Ajouter un membre
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getTeamMembers, deleteTeamMember } from '../../../services/api/team'
import { resolveMediaUrl } from '../../../services/api/upload'
import type { TeamMember } from '../../../types/api'

const members = ref<TeamMember[]>([])
const isLoading = ref(false)

const initials = (name: string) =>
  (name || '').split(' ').filter(Boolean).slice(0, 2).map(w => w[0]?.toUpperCase()).join('')

const fetchMembers = async () => {
  isLoading.value = true
  try {
    members.value = await getTeamMembers()
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchMembers)

const removeMember = async (m: TeamMember) => {
  if (!confirm(`Supprimer « ${m.name} » de l'équipe ?`)) return
  try {
    await deleteTeamMember(m.id)
    members.value = members.value.filter(x => x.id !== m.id)
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erreur lors de la suppression.')
  }
}
</script>

<style scoped lang="scss">
.team-page { max-width: 1000px; margin: 0 auto; }
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
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1rem;
}
.member-card {
  background: #fff; border: 1px solid #e7edf5; border-radius: 14px;
  padding: 1.25rem; text-align: center; position: relative;
  transition: transform 0.2s, border-color 0.2s;
  &:hover { transform: translateY(-2px); border-color: #d7e3f4; }
  &.inactive { opacity: 0.7; }
}
.member-photo {
  width: 84px; height: 84px; border-radius: 50%; margin: 0 auto 0.85rem;
  overflow: hidden; background: #eef2f9; display: flex; align-items: center; justify-content: center;
  img { width: 100%; height: 100%; object-fit: cover; }
}
.member-initials { font-size: 1.6rem; font-weight: 700; color: #2453a7; }
.member-name { font-size: 1rem; font-weight: 700; color: #1a2332; margin: 0 0 0.15rem; }
.member-title { font-size: 0.82rem; color: #6b7280; margin: 0 0 0.5rem; }
.member-actions { display: flex; justify-content: center; gap: 0.4rem; margin-top: 0.75rem; }
.badge { padding: 0.35rem 0.7rem; }
.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon {
  width: 80px; height: 80px; border-radius: 50%; background: rgba(36,83,167,0.08);
  display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;
  .bi { font-size: 2rem; color: #2453a7; }
}
.empty-state h3 { font-size: 1.2rem; font-weight: 600; color: #1a2332; margin-bottom: 0.5rem; }
</style>
