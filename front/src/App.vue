<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'
import DashboardLayout from './components/layout/DashboardLayout.vue'

const route = useRoute()

const hideLayoutRoutes = ['/login', '/register', '/forgot-password', '/reset-password']

const isDashboard = computed(() => route.meta.layout === 'dashboard')
const isAuthPage = computed(() => hideLayoutRoutes.includes(route.path))
</script>

<template>
  <div id="app-root">
    <!-- Auth pages: aucun layout -->
    <RouterView v-if="isAuthPage" />

    <!-- Dashboard layout: sidebar + topbar -->
    <DashboardLayout v-else-if="isDashboard" />

    <!-- Public layout: navbar + footer -->
    <template v-else>
      <Navbar />
      <main>
        <RouterView />
      </main>
      <Footer />
    </template>
  </div>
</template>

<style>
main {
  min-height: calc(100vh - 136px);
}
</style>
