<script setup lang="ts">
import { ref, computed, provide } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
// @ts-ignore Vetur false positive on Vue SFC default export
import DashboardSidebar from './DashboardSidebar.vue'
import { useAuthStore } from '../../stores/auth'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)
const route = useRoute()

const mobileMenuOpen = ref(false)
provide('mobileMenuOpen', mobileMenuOpen)

const handleLogout = async () => {
  const result = await Swal.fire({
    title: 'Déconnexion',
    text: 'Êtes-vous sûr de vouloir vous déconnecter ?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Oui, me déconnecter',
    cancelButtonText: 'Annuler',
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6b7280',
    reverseButtons: true,
  })
  if (result.isConfirmed) {
    authStore.logout()
  }
}

const pageTitle = computed(() => {
  const name = route.name as string
  const titles: Record<string, string> = {
    dashboard: 'Tableau de bord',
    profile: 'Mon profil',
    'my-content': 'Mes contenus',
    'content-editor': 'Éditeur de contenu',
    'student-courses': 'Mes cours',
    'course-detail': 'Détail du cours',
    certificates: 'Certificats',
    'browse-courses': 'Explorer les cours',
    'lesson-viewer': 'Leçon',
    'professor-courses': 'Gérer les cours',
    'course-editor': 'Éditeur de cours',
    'live-sessions': 'Sessions en direct',
    'live-session': 'Session en direct',
    'manage-professors': 'Gérer les professeurs',
    'professor-form': 'Formulaire professeur',
    'professor-detail': 'Détail professeur',
    'manage-users': 'Gérer les utilisateurs',
    'user-form': 'Formulaire utilisateur',
  }
  return titles[name] || 'Espace privé'
})

interface Breadcrumb {
  label: string
  to?: string
}

const breadcrumbs = computed<Breadcrumb[]>(() => {
  const name = route.name as string
  const crumbs: Breadcrumb[] = [{ label: 'Dashboard', to: '/dashboard' }]

  // Route hierarchy mapping: route name → parent section + current label
  const hierarchy: Record<string, { section?: Breadcrumb; label: string }> = {
    dashboard: { label: 'Tableau de bord' },
    profile: { label: 'Mon profil' },
    'my-content': { label: 'Mes contenus' },
    'content-editor': {
      section: { label: 'Mes contenus', to: '/my-content' },
      label: route.params.id ? 'Modifier' : 'Nouveau contenu',
    },
    'student-courses': {
      section: { label: 'Étudiant' },
      label: 'Mes cours',
    },
    'course-detail': {
      section: { label: 'Mes cours', to: '/my-courses' },
      label: 'Détail du cours',
    },
    certificates: {
      section: { label: 'Étudiant' },
      label: 'Certificats',
    },
    'browse-courses': {
      section: { label: 'Étudiant' },
      label: 'Explorer les cours',
    },
    'lesson-viewer': {
      section: { label: 'Mes cours', to: '/my-courses' },
      label: 'Leçon',
    },
    'professor-courses': {
      section: { label: 'Professeur' },
      label: 'Gérer les cours',
    },
    'course-editor': {
      section: { label: 'Gérer les cours', to: '/manage-courses' },
      label: route.params.id ? 'Modifier le cours' : 'Nouveau cours',
    },
    'live-sessions': {
      section: { label: 'Professeur' },
      label: 'Sessions en direct',
    },
    'live-session': {
      section: { label: 'Sessions en direct', to: '/live-sessions' },
      label: route.params.id ? 'Modifier la session' : 'Nouvelle session',
    },
    'manage-professors': {
      section: { label: 'Administration' },
      label: 'Professeurs',
    },
    'professor-form': {
      section: { label: 'Professeurs', to: '/manage-professors' },
      label: route.params.id ? 'Modifier' : 'Nouveau professeur',
    },
    'professor-detail': {
      section: { label: 'Professeurs', to: '/manage-professors' },
      label: 'Détail professeur',
    },
    'manage-users': {
      section: { label: 'Administration' },
      label: 'Utilisateurs',
    },
    'user-form': {
      section: { label: 'Utilisateurs', to: '/manage-users' },
      label: route.params.id ? 'Modifier' : 'Nouvel utilisateur',
    },
  }

  const entry = hierarchy[name]
  if (entry) {
    if (entry.section) {
      crumbs.push(entry.section)
    }
    crumbs.push({ label: entry.label })
  }

  return crumbs
})
</script>

<script lang="ts">
export default {
  name: 'DashboardLayout',
}
</script>

<template>
  <div class="dashboard-wrapper">
    <DashboardSidebar />

    <!-- Main Content Area -->
    <div class="dashboard-main">
      <!-- Topbar -->
      <header class="dashboard-topbar">
        <div class="topbar-left">
          <button class="btn-mobile-menu d-lg-none" @click="mobileMenuOpen = !mobileMenuOpen">
            <i class="bi bi-list"></i>
          </button>
          <h1 class="topbar-title">{{ pageTitle }}</h1>
        </div>

        <div class="topbar-right">
          <!-- Back to public site -->
          <RouterLink to="/" class="topbar-link me-3" title="Retour au site">
            <i class="bi bi-house-door"></i>
          </RouterLink>

          <!-- User dropdown -->
          <div class="dropdown">
            <button
              class="topbar-user"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <div class="user-avatar">
                <i class="bi bi-person-fill"></i>
              </div>
              <span class="user-name d-none d-md-inline">{{ currentUser?.name }}</span>
              <i class="bi bi-chevron-down ms-1 small"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow-sm">
              <li>
                <div class="dropdown-header">
                  <strong>{{ currentUser?.name }}</strong>
                  <br><small class="text-muted">{{ currentUser?.email }}</small>
                </div>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink class="dropdown-item" to="/profile"><i class="bi bi-person me-2"></i>Mon profil</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/"><i class="bi bi-house-door me-2"></i>Retour au site</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><button class="dropdown-item text-danger" @click="handleLogout"><i class="bi bi-box-arrow-right me-2"></i>Déconnexion</button></li>
            </ul>
          </div>
        </div>
      </header>

      <!-- Breadcrumb -->
      <nav v-if="breadcrumbs.length > 1" class="dashboard-breadcrumb" aria-label="Fil d'Ariane">
        <ol>
          <li v-for="(crumb, idx) in breadcrumbs" :key="idx" :class="{ active: idx === breadcrumbs.length - 1 }">
            <RouterLink v-if="crumb.to && idx !== breadcrumbs.length - 1" :to="crumb.to">
              <i v-if="idx === 0" class="bi bi-house-door-fill"></i>
              {{ crumb.label }}
            </RouterLink>
            <span v-else>
              <i v-if="idx === 0" class="bi bi-house-door-fill"></i>
              {{ crumb.label }}
            </span>
            <i v-if="idx < breadcrumbs.length - 1" class="bi bi-chevron-right separator"></i>
          </li>
        </ol>
      </nav>

      <!-- Page Content -->
      <div class="dashboard-content">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
$sidebar-width: 250px;

.dashboard-wrapper {
  display: flex;
  min-height: 100vh;
  background: #f4f6fb;
}

.dashboard-main {
  flex: 1;
  margin-left: $sidebar-width;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.dashboard-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 1.5rem;
  background: #fff;
  border-bottom: 1px solid #e7edf5;
  position: sticky;
  top: 0;
  z-index: 1030;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.topbar-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1a2332;
  margin: 0;
}

.btn-mobile-menu {
  background: none;
  border: none;
  font-size: 1.4rem;
  color: #4b5563;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  &:hover { background: #f0f2f5; }
}

.topbar-right {
  display: flex;
  align-items: center;
}

.topbar-link {
  color: #6b7280;
  font-size: 1.2rem;
  padding: 6px;
  border-radius: 8px;
  transition: all 0.15s;
  &:hover { color: #2453a7; background: #f0f4ff; }
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1px solid #e7edf5;
  border-radius: 24px;
  padding: 0.3rem 0.75rem 0.3rem 0.3rem;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { border-color: #d0d7e3; background: #f8f9fb; }
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2453a7, #2f6ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.9rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a2332;
}

.dashboard-breadcrumb {
  padding: 0.65rem 1.5rem;
  background: #fff;
  border-bottom: 1px solid #eef1f6;

  ol {
    display: flex;
    align-items: center;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 0;
    flex-wrap: wrap;
  }

  li {
    display: flex;
    align-items: center;
    font-size: 0.8rem;
    color: #6b7280;

    a {
      color: #2453a7;
      text-decoration: none;
      font-weight: 500;
      transition: color 0.15s;

      &:hover {
        color: #1a3d7c;
        text-decoration: underline;
      }

      i {
        font-size: 0.85rem;
        margin-right: 0.2rem;
        vertical-align: -1px;
      }
    }

    span {
      i {
        font-size: 0.85rem;
        margin-right: 0.2rem;
        vertical-align: -1px;
      }
    }

    &.active {
      color: #1a2332;
      font-weight: 600;
    }
  }

  .separator {
    font-size: 0.55rem;
    color: #c0c7d1;
    margin: 0 0.45rem;
  }
}

.dashboard-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

// Mobile
@media (max-width: 991.98px) {
  .dashboard-main {
    margin-left: 0;
  }
}
</style>
