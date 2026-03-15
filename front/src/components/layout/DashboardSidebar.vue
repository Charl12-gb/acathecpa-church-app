<script setup lang="ts">
import { computed, ref, inject, watch, type Ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { UserRole } from '../../types/api/userTypes'
import { APP_NAME } from '../../config'

const route = useRoute()
const authStore = useAuthStore()

const canAccessStudent = computed(() => authStore.hasMinRole(UserRole.STUDENT))
const canAccessProfessor = computed(() => authStore.hasMinRole(UserRole.PROFESSOR))
const canAccessAdmin = computed(() => authStore.hasMinRole(UserRole.ADMIN))

const collapsed = ref(false)
const mobileMenuOpen = inject<Ref<boolean>>('mobileMenuOpen', ref(false))

// Close mobile menu on route change
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

const isActive = (path: string) => route.path === path
const isActiveGroup = (paths: string[]) => paths.some(p => route.path.startsWith(p))
</script>

<template>
  <aside class="dashboard-sidebar" :class="{ collapsed, 'mobile-open': mobileMenuOpen }">
    <!-- Brand -->
    <div class="sidebar-brand">
      <RouterLink to="/" class="brand-link">
        <i class="bi bi-mortarboard-fill brand-icon"></i>
        <span v-if="!collapsed" class="brand-text">{{ APP_NAME }}</span>
      </RouterLink>
      <button class="btn-collapse" @click="collapsed = !collapsed" :title="collapsed ? 'Ouvrir' : 'Réduire'">
        <i :class="collapsed ? 'bi bi-chevron-right' : 'bi bi-chevron-left'"></i>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <!-- Général -->
      <div class="nav-section">
        <span v-if="!collapsed" class="nav-section-title">Général</span>
        <RouterLink to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }">
          <i class="bi bi-grid-1x2-fill"></i>
          <span v-if="!collapsed">Tableau de bord</span>
        </RouterLink>
        <RouterLink to="/profile" class="nav-item" :class="{ active: isActive('/profile') }">
          <i class="bi bi-person-fill"></i>
          <span v-if="!collapsed">Mon profil</span>
        </RouterLink>
        <RouterLink to="/my-content" class="nav-item" :class="{ active: isActive('/my-content') || isActive('/content/editor') }">
          <i class="bi bi-file-earmark-text-fill"></i>
          <span v-if="!collapsed">Mes contenus</span>
        </RouterLink>
      </div>

      <!-- Étudiant -->
      <div v-if="canAccessStudent" class="nav-section">
        <span v-if="!collapsed" class="nav-section-title">Étudiant</span>
        <RouterLink to="/my-courses" class="nav-item" :class="{ active: isActiveGroup(['/my-courses', '/course/', '/lesson/']) }">
          <i class="bi bi-book-fill"></i>
          <span v-if="!collapsed">Mes cours</span>
        </RouterLink>
        <RouterLink to="/certificates" class="nav-item" :class="{ active: isActive('/certificates') }">
          <i class="bi bi-award-fill"></i>
          <span v-if="!collapsed">Certificats</span>
        </RouterLink>
        <RouterLink to="/browse-courses" class="nav-item" :class="{ active: isActive('/browse-courses') }">
          <i class="bi bi-search"></i>
          <span v-if="!collapsed">Explorer les cours</span>
        </RouterLink>
      </div>

      <!-- Professeur -->
      <div v-if="canAccessProfessor" class="nav-section">
        <span v-if="!collapsed" class="nav-section-title">Professeur</span>
        <RouterLink to="/manage-courses" class="nav-item" :class="{ active: isActiveGroup(['/manage-courses', '/course-editor']) }">
          <i class="bi bi-journal-richtext"></i>
          <span v-if="!collapsed">Gérer les cours</span>
        </RouterLink>
        <RouterLink to="/live-sessions" class="nav-item" :class="{ active: isActiveGroup(['/live-sessions', '/live-session']) }">
          <i class="bi bi-broadcast-pin"></i>
          <span v-if="!collapsed">Sessions en direct</span>
        </RouterLink>
      </div>

      <!-- Administration -->
      <div v-if="canAccessAdmin" class="nav-section">
        <span v-if="!collapsed" class="nav-section-title">Administration</span>
        <RouterLink to="/manage-users" class="nav-item" :class="{ active: isActiveGroup(['/manage-users', '/user-form']) }">
          <i class="bi bi-people-fill"></i>
          <span v-if="!collapsed">Utilisateurs</span>
        </RouterLink>
        <RouterLink to="/manage-professors" class="nav-item" :class="{ active: isActiveGroup(['/manage-professors', '/professor-form', '/professors/']) }">
          <i class="bi bi-person-badge-fill"></i>
          <span v-if="!collapsed">Professeurs</span>
        </RouterLink>
      </div>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <RouterLink to="/" class="nav-item">
        <i class="bi bi-box-arrow-left"></i>
        <span v-if="!collapsed">Retour au site</span>
      </RouterLink>
    </div>
  </aside>
</template>

<style scoped lang="scss">
$sidebar-width: 250px;
$sidebar-collapsed: 68px;
$sidebar-bg: #1a2332;
$sidebar-hover: #243044;
$sidebar-active: #2453a7;
$sidebar-text: #a0aec0;
$sidebar-text-active: #ffffff;
$transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);

.dashboard-sidebar {
  width: $sidebar-width;
  min-height: 100vh;
  background: $sidebar-bg;
  display: flex;
  flex-direction: column;
  transition: width $transition;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  overflow-x: hidden;

  &.collapsed {
    width: $sidebar-collapsed;
  }
}

.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 64px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  white-space: nowrap;
  overflow: hidden;
}

.brand-icon {
  font-size: 1.5rem;
  color: #d4a843;
  flex-shrink: 0;
}

.btn-collapse {
  background: none;
  border: none;
  color: $sidebar-text;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  flex-shrink: 0;
  &:hover { color: #fff; background: $sidebar-hover; }
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
}

.nav-section {
  padding: 0.25rem 0;

  & + .nav-section {
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    margin-top: 0.25rem;
    padding-top: 0.5rem;
  }
}

.nav-section-title {
  display: block;
  padding: 0.35rem 1.25rem;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: rgba(160, 174, 192, 0.55);
  font-weight: 600;
  white-space: nowrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 1.25rem;
  color: $sidebar-text;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.15s;
  border-left: 3px solid transparent;

  i {
    font-size: 1.1rem;
    flex-shrink: 0;
    width: 20px;
    text-align: center;
  }

  &:hover {
    color: $sidebar-text-active;
    background: $sidebar-hover;
  }

  &.active {
    color: $sidebar-text-active;
    background: rgba($sidebar-active, 0.18);
    border-left-color: $sidebar-active;

    i { color: lighten($sidebar-active, 15%); }
  }
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.5rem 0;
}

// Collapsed state
.collapsed {
  .sidebar-brand { justify-content: center; padding: 1rem 0.5rem; }
  .brand-link { justify-content: center; }
  .btn-collapse { display: none; }
  .nav-item { justify-content: center; padding: 0.65rem 0; border-left: none; }
  .nav-section-title { display: none; }
}

// Mobile responsive
@media (max-width: 991.98px) {
  .dashboard-sidebar {
    transform: translateX(-100%);

    &.mobile-open {
      transform: translateX(0);
      box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    }
  }
}

// Mobile
@media (max-width: 991.98px) {
  .dashboard-sidebar {
    transform: translateX(-100%);
    &.mobile-open { transform: translateX(0); }
  }
}
</style>
