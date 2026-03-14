<script setup lang="ts">
import { APP_NAME } from '../../config'
</script>

<template>
  <footer class="bg-light py-4 mt-5 border-top">
    <div class="container">
      <div class="row">
        <div class="col-md-4 mb-3 mb-md-0">
          <h5 class="mb-3">{{ APP_NAME }}</h5>
          <p class="text-muted">Centre de formation professionnelle de qualité, offrant des cours adaptés aux besoins du marché.</p>
        </div>
        <div class="col-md-4 mb-3 mb-md-0">
          <h5 class="mb-3">Liens Rapides</h5>
          <ul class="list-unstyled">
            <li><RouterLink class="text-decoration-none text-muted" to="/">Accueil</RouterLink></li>
            <li><RouterLink class="text-decoration-none text-muted" to="/contact">Nous Contacter</RouterLink></li>
            <li><RouterLink class="text-decoration-none text-muted" to="/login">Connexion</RouterLink></li>
            <li><RouterLink class="text-decoration-none text-muted" to="/register">Inscription</RouterLink></li>
          </ul>
        </div>
        <div class="col-md-4">
          <h5 class="mb-3">Contact</h5>
          <ul class="list-unstyled text-muted">
            <li><i class="bi bi-geo-alt me-2"></i> 123 Rue Principale, Ville</li>
            <li><i class="bi bi-telephone me-2"></i> +123 456 789</li>
            <li><i class="bi bi-envelope me-2"></i> info@acathecpa.com</li>
          </ul>
          <div class="social-icons mt-2">
            <a href="#" class="text-muted me-2"><i class="bi bi-facebook"></i></a>
            <a href="#" class="text-muted me-2"><i class="bi bi-twitter"></i></a>
            <a href="#" class="text-muted me-2"><i class="bi bi-instagram"></i></a>
            <a href="#" class="text-muted"><i class="bi bi-linkedin"></i></a>
          </div>
        </div>
      </div>
      <hr class="my-3">
      <div class="text-center text-muted">
        <small>&copy; {{ new Date().getFullYear() }} {{ APP_NAME }}. Tous droits réservés.</small>
      </div>
    </div>
  </footer>
</template>

<style scoped>
footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.social-icons a {
  font-size: 1.2rem;
  transition: color 0.3s;
}

.social-icons a:hover {
  color: white !important;
}
</style>