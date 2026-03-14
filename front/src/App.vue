<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'

const route = useRoute()

// Liste des routes où on veut cacher Navbar et Footer
const hideLayoutRoutes = ['/login', '/register', '/forgot-password', '/reset-password']
</script>

<template>
  <!-- Afficher Navbar seulement si la route n'est pas dans hideLayoutRoutes -->
  <Navbar v-if="!hideLayoutRoutes.includes(route.path)" />

  <main>
    <RouterView />
  </main>

  <!-- Afficher Footer seulement si la route n'est pas dans hideLayoutRoutes -->
  <Footer v-if="!hideLayoutRoutes.includes(route.path)" />
</template>

<style>
main {
  min-height: calc(100vh - 136px);
}
</style>
