<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { APP_NAME } from '../../config'
import Swal from 'sweetalert2'

const route = useRoute()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.user)
const mobileOpen = ref(false)

watch(() => route.path, () => { mobileOpen.value = false })

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
</script>

<script lang="ts">
export default {
  name: 'Navbar',
}
</script>

<template>
  <nav class="site-navbar">
    <div class="container">
      <div class="navbar-inner">
        <!-- Brand -->
        <RouterLink class="navbar-brand" to="/">{{ APP_NAME }}</RouterLink>

        <!-- Public links (desktop) -->
        <ul class="nav-links">
          <li><RouterLink to="/">Accueil</RouterLink></li>
          <li><RouterLink to="/articles">Articles</RouterLink></li>
          <li><RouterLink to="/podcasts">Podcasts</RouterLink></li>
          <li><RouterLink to="/contact">Contact</RouterLink></li>
        </ul>

        <!-- Auth area (desktop) -->
        <div class="nav-auth">
          <template v-if="!isAuthenticated">
            <RouterLink to="/login" class="btn-login">Connexion</RouterLink>
            <RouterLink to="/register" class="btn-register">Inscription</RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/dashboard" class="btn-dashboard">
              <i class="bi bi-grid-1x2-fill"></i>
              Tableau de bord
            </RouterLink>
            <div class="user-sep"></div>
            <span class="user-name-display">{{ currentUser?.name }}</span>
            <button class="btn-logout" @click="handleLogout" title="Déconnexion">
              <i class="bi bi-box-arrow-right"></i>
            </button>
          </template>
        </div>

        <!-- Hamburger (mobile) -->
        <button class="hamburger" :class="{ open: mobileOpen }" @click="mobileOpen = !mobileOpen" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>

    <!-- Mobile drawer -->
    <Transition name="drawer">
      <div v-if="mobileOpen" class="mobile-menu">
        <ul class="mobile-links">
          <li><RouterLink to="/"><i class="bi bi-house"></i> Accueil</RouterLink></li>
          <li><RouterLink to="/articles"><i class="bi bi-journal-richtext"></i> Articles</RouterLink></li>
          <li><RouterLink to="/podcasts"><i class="bi bi-mic-fill"></i> Podcasts</RouterLink></li>
          <li><RouterLink to="/contact"><i class="bi bi-envelope-fill"></i> Contact</RouterLink></li>
        </ul>
        <div class="mobile-auth">
          <template v-if="!isAuthenticated">
            <RouterLink to="/login" class="btn-mobile btn-mobile-login">Connexion</RouterLink>
            <RouterLink to="/register" class="btn-mobile btn-mobile-register">Inscription</RouterLink>
          </template>
          <template v-else>
            <span class="mobile-user"><i class="bi bi-person-circle"></i> {{ currentUser?.name }}</span>
            <RouterLink to="/dashboard" class="btn-mobile btn-mobile-register">
              <i class="bi bi-grid-1x2-fill"></i> Tableau de bord
            </RouterLink>
            <button class="btn-mobile btn-mobile-logout" @click="handleLogout">
              <i class="bi bi-box-arrow-right"></i> Déconnexion
            </button>
          </template>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<style scoped lang="scss">
.site-navbar {
  background: #fff;
  border-bottom: 1px solid #e7edf5;
  box-shadow: 0 1px 8px rgba(36, 83, 167, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 2rem;
}

.navbar-brand {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1a2332;
  text-decoration: none;
  letter-spacing: -0.02em;
  flex-shrink: 0;

  &:hover { color: #2453a7; }
}

.nav-links {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.25rem;
  flex: 1;

  li a {
    display: block;
    padding: 0.4rem 0.75rem;
    color: #4b5563;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.15s;

    &:hover, &.router-link-active {
      color: #2453a7;
      background: #f0f4ff;
    }
  }
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.btn-login {
  padding: 0.4rem 1rem;
  border: 1.5px solid #d0d7e3;
  border-radius: 8px;
  color: #1a2332;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s;

  &:hover { border-color: #2453a7; color: #2453a7; background: #f0f4ff; }
}

.btn-register {
  padding: 0.4rem 1rem;
  border-radius: 8px;
  background: #2453a7;
  color: #fff;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.15s;

  &:hover { background: #1a3d7c; }
}

.btn-dashboard {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  background: #2453a7;
  color: #fff;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.15s;

  i { font-size: 0.85rem; }

  &:hover { background: #1a3d7c; }
}

.user-sep {
  width: 1px;
  height: 22px;
  background: #e7edf5;
}

.user-name-display {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1.5px solid #e7edf5;
  border-radius: 8px;
  background: none;
  color: #6b7280;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    border-color: #f5c6cb;
    color: #dc3545;
    background: #fff5f5;
  }
}

/* ═══════ HAMBURGER ═══════ */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 36px;
  height: 36px;
  padding: 6px;
  margin-left: auto;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 8px;
  transition: background .15s;
  &:hover { background: #f0f4ff; }
  span {
    display: block;
    width: 100%;
    height: 2.5px;
    border-radius: 2px;
    background: #1a2332;
    transition: all .25s;
  }
  &.open span:nth-child(1) {
    transform: translateY(7.5px) rotate(45deg);
  }
  &.open span:nth-child(2) {
    opacity: 0;
  }
  &.open span:nth-child(3) {
    transform: translateY(-7.5px) rotate(-45deg);
  }
}

/* ═══════ MOBILE DRAWER ═══════ */
.mobile-menu {
  background: #fff;
  border-top: 1px solid #e7edf5;
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
  padding: 16px 20px 24px;
}

@media (max-width: 767.98px) {
  .nav-links { display: none; }
  .nav-auth { display: none; }
  .navbar-inner { gap: 1rem; }
  .hamburger { display: flex; }
}
.drawer-enter-active,
.drawer-leave-active {
  transition: all .25s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.mobile-links {
  list-style: none;
  margin: 0 0 16px;
  padding: 0;
  li a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 10px;
    color: #4b5563;
    text-decoration: none;
    font-size: .92rem;
    font-weight: 500;
    transition: all .15s;
    i { font-size: 1rem; width: 20px; text-align: center; color: #2453a7; }
    &:hover, &.router-link-active {
      color: #2453a7;
      background: #f0f4ff;
    }
  }
}
.mobile-auth {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid #e7edf5;
  padding-top: 16px;
}
.mobile-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: .88rem;
  font-weight: 600;
  color: #1a2332;
  padding: 0 4px 4px;
  i { color: #2453a7; }
}
.btn-mobile {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 11px;
  border-radius: 10px;
  font-size: .9rem;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all .15s;
}
.btn-mobile-login {
  border: 1.5px solid #d0d7e3;
  background: #fff;
  color: #1a2332;
  &:hover { border-color: #2453a7; color: #2453a7; }
}
.btn-mobile-register {
  background: #2453a7;
  color: #fff;
  &:hover { background: #1a3d7c; }
}
.btn-mobile-logout {
  background: #fff5f5;
  color: #dc3545;
  border: 1.5px solid #f5c6cb;
  &:hover { background: #fce4e4; }
}
</style>