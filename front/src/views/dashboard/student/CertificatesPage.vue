<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router'; // Keep if needed for "Explorer les cours"
import { getUserCertificates } from '../../../services/api/course'; // Adjust path
import type { CertificateDisplay } from '../../../types/api'; // Adjust path

// Assume an auth store or similar provides the user ID
// For placeholder: const userId = 1;
// Replace this with actual user ID retrieval, e.g. from a Pinia store
const getCurrentUserId = (): number | null => {
  // Placeholder: In a real app, get this from your auth store (e.g., Pinia, Vuex)
  // const authStore = useAuthStore();
  // return authStore.userId;
  console.warn('Using placeholder user ID for fetching certificates.');
  return 1; // Replace with actual logic
};

const certificates = ref<CertificateDisplay[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

const fetchCertificates = async () => {
  const userId = getCurrentUserId();
  if (!userId) {
    error.value = "Impossible de récupérer l'identifiant de l'utilisateur.";
    return;
  }

  isLoading.value = true;
  error.value = null;
  try {
    certificates.value = await getUserCertificates(userId);
  } catch (err: any) {
    console.error('Failed to fetch certificates:', err);
    error.value = err.message || 'Erreur lors du chargement des certificats.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchCertificates();
});

const handleDownloadCertificate = (certificate: CertificateDisplay) => {
  if (certificate.certificate_url) {
    window.open(certificate.certificate_url, '_blank');
  } else {
    // Handle cases where URL might be missing, e.g., show a message
    console.warn('Certificate URL is missing for ID:', certificate.id);
    alert('Le lien de téléchargement du certificat n\'est pas disponible.');
  }
};

const handleShareCertificate = (certificate: CertificateDisplay) => {
  console.log('Sharing certificate:', certificate.id);
  // Placeholder: Implement sharing logic, e.g., copy link to clipboard
  if (certificate.certificate_url) {
    navigator.clipboard.writeText(certificate.certificate_url)
      .then(() => alert('Lien du certificat copié dans le presse-papiers!'))
      .catch(err => {
        console.error('Failed to copy certificate link:', err);
        alert('Impossible de copier le lien du certificat.');
      });
  } else {
    alert('Aucun lien de certificat disponible à partager.');
  }
};

</script>

<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-1">Mes Certificats</h1>
        <p class="text-muted mb-0">Vos réalisations et certifications obtenues</p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p>Chargement des certificats...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <!-- Certificates Grid -->
    <div v-else-if="certificates.length > 0" class="row g-4">
      <div v-for="certificate in certificates" :key="certificate.id" class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex mb-4">
              <img
                v-if="certificate.course_image_url"
                :src="certificate.course_image_url"
                :alt="certificate.course_title"
                class="rounded me-3"
                style="width: 80px; height: 80px; object-fit: cover;"
              >
              <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3" v-else>
                <i class="bi bi-award-fill text-primary fs-4"></i>
              </div>
              <div>
                <h5 class="mb-1">{{ certificate.course_title || `Certificat pour Cours ID ${certificate.course_id}` }}</h5>
                <p class="mb-0 text-muted">Obtenu le: {{ new Date(certificate.issue_date).toLocaleDateString() }}</p>
              </div>
            </div>

            <!-- Fields like grade, score, skills are not in CertificateDisplay from backend -->
            <!-- So, removing them for now. These would require schema/service changes. -->
            <!--
            <div class="row g-3 mb-4"> ... grade and score ... </div>
            <div class="mb-4"> <h6 class="mb-3">Compétences acquises</h6> ... skills ... </div>
            -->

            <div class="mb-3" v-if="certificate.verification_code">
                <small class="text-muted d-block">Code de vérification:</small>
                <strong>{{ certificate.verification_code }}</strong>
            </div>


            <div class="d-flex justify-content-between align-items-center">
              <small class="text-muted">
                ID du certificat: {{ certificate.id }}
              </small>
              <div class="btn-group">
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="handleDownloadCertificate(certificate)"
                  :disabled="!certificate.certificate_url"
                >
                  <i class="bi bi-download me-2"></i>{{ certificate.certificate_url ? 'Télécharger' : 'Indisponible' }}
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="handleShareCertificate(certificate)"
                  :disabled="!certificate.certificate_url"
                >
                  <i class="bi bi-share me-2"></i>Partager
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <div class="mb-4">
        <i class="bi bi-award display-1 text-muted"></i>
      </div>
      <h3>Pas encore de certificats</h3>
      <p class="text-muted">Terminez vos cours pour obtenir vos premiers certificats</p>
      <RouterLink to="/my-courses" class="btn btn-primary">
        Voir mes cours
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.badge {
  padding: 0.5rem 1rem;
  font-weight: normal;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>