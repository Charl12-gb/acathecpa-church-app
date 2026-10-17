<template>
  <div class="container py-5">
    <div class="row">
      <div class="col-lg-6 mx-auto">
        <h1 class="h3 mb-2">Vérifier un certificat</h1>
        <p class="text-muted mb-4">Saisissez le code inscrit sur le certificat (par exemple CERT-3F9A2C71B0).</p>

        <form class="d-flex gap-2 mb-4" @submit.prevent="submit">
          <label for="cert-code" class="visually-hidden">Code de vérification</label>
          <input id="cert-code" v-model.trim="code" class="form-control" placeholder="CERT-…" autocomplete="off">
          <button class="btn btn-primary" type="submit" :disabled="!code || loading">Vérifier</button>
        </form>

        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Vérification...</span></div>
        </div>

        <div v-else-if="result" class="card border-success">
          <div class="card-body">
            <p class="text-success fw-semibold mb-3"><i class="bi bi-patch-check-fill me-2"></i>Certificat authentique</p>
            <dl class="row mb-0">
              <dt class="col-sm-4">Titulaire</dt><dd class="col-sm-8">{{ result.holder_name }}</dd>
              <dt class="col-sm-4">Formation</dt><dd class="col-sm-8">{{ result.course_title }}</dd>
              <dt class="col-sm-4">Délivré le</dt><dd class="col-sm-8">{{ formatDate(result.issue_date) }}</dd>
              <dt class="col-sm-4">Code</dt><dd class="col-sm-8"><code>{{ result.verification_code }}</code></dd>
            </dl>
          </div>
        </div>

        <div v-else-if="notFound" class="alert alert-danger">
          Aucun certificat ne correspond au code « {{ checkedCode }} ». Vérifiez la saisie, en respectant les majuscules.
        </div>
        <div v-else-if="error" class="alert alert-warning">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { verifyCertificate } from '../../services/api/course';
import type { CertificateVerification } from '../../types/api';

const route = useRoute();
const router = useRouter();

const code = ref((route.params.code as string) || '');
const checkedCode = ref('');
const result = ref<CertificateVerification | null>(null);
const loading = ref(false);
const notFound = ref(false);
const error = ref<string | null>(null);

const formatDate = (iso: string) => new Date(iso).toLocaleDateString('fr-FR', { dateStyle: 'long' });

const check = async (value: string) => {
  result.value = null;
  notFound.value = false;
  error.value = null;
  if (!value) return;
  checkedCode.value = value;
  loading.value = true;
  try {
    result.value = await verifyCertificate(value);
  } catch (err: any) {
    if (err.response?.status === 404) notFound.value = true;
    else error.value = 'La vérification est momentanément indisponible. Réessayez plus tard.';
  } finally {
    loading.value = false;
  }
};

// Keep the code in the URL so a verification link can be shared.
const submit = () => router.push({ name: 'certificate-verify', params: { code: code.value } });

watch(() => route.params.code, (value) => {
  code.value = (value as string) || '';
  check(code.value);
});

onMounted(() => check(code.value));
</script>
