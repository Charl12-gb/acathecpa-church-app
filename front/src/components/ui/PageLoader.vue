<template>
  <div class="page-loader" role="status" aria-live="polite">
    <span class="page-loader__spinner" aria-hidden="true"></span>
    <p class="page-loader__text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ text?: string }>(), { text: 'Chargement…' });
</script>

<style scoped>
.page-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 64px 16px;
  color: #6b7280;
}
.page-loader__spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #dfe8f6;
  border-top-color: #2453a7;
  border-radius: 50%;
  animation: page-loader-spin .8s linear infinite;
}
.page-loader__text {
  margin: 0;
  font-size: .95rem;
}
@keyframes page-loader-spin {
  to { transform: rotate(360deg); }
}
@media (prefers-reduced-motion: reduce) {
  .page-loader__spinner { animation-duration: 2.4s; }
}
</style>
