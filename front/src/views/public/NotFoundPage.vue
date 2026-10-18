<template>
  <div class="container py-5 text-center">
    <p class="display-4 fw-bold text-muted mb-2">404</p>
    <h1 class="h3 mb-3">Cette page n'existe pas</h1>
    <p class="text-muted mb-4">Le lien est peut-être incomplet, ou la page a été déplacée.</p>
    <div class="d-flex flex-wrap justify-content-center gap-2">
      <RouterLink to="/" class="btn btn-primary">Accueil</RouterLink>
      <RouterLink to="/browse-courses" class="btn btn-outline-primary">Voir les formations</RouterLink>
      <RouterLink to="/contact" class="btn btn-link">Nous contacter</RouterLink>
    </div>
  </div>
</template>
