<template>
  <div class="container py-5 legal">
    <div class="row">
      <article class="col-lg-8 mx-auto">
        <h1 class="h2 mb-2">{{ title }}</h1>
        <p class="text-muted small mb-4">Dernière mise à jour : {{ ORGANISATION.legalUpdatedAt }}</p>
        <slot />
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ORGANISATION } from '../config';

defineProps<{ title: string }>();
</script>

<style scoped>
.legal :deep(h2) { font-size: 1.2rem; margin-top: 2rem; margin-bottom: .75rem; }
.legal :deep(p), .legal :deep(li) { line-height: 1.7; color: #374151; }
.legal :deep(ul) { padding-left: 1.2rem; }
</style>
