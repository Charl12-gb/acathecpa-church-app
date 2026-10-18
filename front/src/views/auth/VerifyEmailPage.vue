<template>
  <div class="container py-5">
    <div class="row">
      <div class="col-lg-6 mx-auto text-center">
        <div v-if="state === 'loading'" class="py-4">
          <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Vérification…</span></div>
        </div>
        <template v-else-if="state === 'ok'">
          <i class="bi bi-patch-check-fill text-success display-5"></i>
          <h1 class="h3 mt-3">Adresse email confirmée</h1>
          <p class="text-muted">Merci ! Votre compte est entièrement activé.</p>
          <RouterLink :to="authStore.isAuthenticated ? '/dashboard' : '/login'" class="btn btn-primary">
            {{ authStore.isAuthenticated ? 'Aller à mon espace' : 'Se connecter' }}
          </RouterLink>
        </template>
        <template v-else>
          <i class="bi bi-x-octagon text-danger display-5"></i>
          <h1 class="h3 mt-3">Lien invalide ou expiré</h1>
          <p class="text-muted">{{ message }}</p>
          <RouterLink :to="authStore.isAuthenticated ? '/dashboard' : '/login'" class="btn btn-outline-primary">
            {{ authStore.isAuthenticated ? 'Renvoyer un lien depuis mon espace' : 'Se connecter pour recevoir un nouveau lien' }}
          </RouterLink>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { verifyEmail } from '../../services/api/auth';
import { useAuthStore } from '../../stores/auth';

const route = useRoute();
const authStore = useAuthStore();
const state = ref<'loading' | 'ok' | 'error'>('loading');
const message = ref('');

onMounted(async () => {
  try {
    await verifyEmail(String(route.query.token || ''));
    state.value = 'ok';
    // Hide the reminder banner right away for a signed-in user.
    if (authStore.isAuthenticated) await authStore.refreshMe().catch(() => undefined);
  } catch (err: any) {
    message.value = err.response?.data?.detail || 'Ce lien ne peut pas être utilisé.';
    state.value = 'error';
  }
});
</script>
