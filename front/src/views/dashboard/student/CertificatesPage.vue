<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { getMyCertificates } from '../../../services/api/course';
import type { CertificateDisplay } from '../../../types/api';
import { useAuthStore } from '../../../stores/auth';

const authStore = useAuthStore();
const certificates = ref<CertificateDisplay[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const previewCert = ref<CertificateDisplay | null>(null);

const studentName = computed(() => authStore.user?.name || 'Étudiant');

const fetchCertificates = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    certificates.value = await getMyCertificates();
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

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' });

const openPreview = (cert: CertificateDisplay) => {
  previewCert.value = cert;
};
const closePreview = () => {
  previewCert.value = null;
};

const certHtml = (cert: CertificateDisplay, name: string, autoPrint = true) => {
  const issueDate = formatDate(cert.issue_date);
  const courseTitle = cert.course_title || `Cours ID ${cert.course_id}`;
  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Certificat - ${courseTitle}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');
@page { size: A4 landscape; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Lato', sans-serif; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
.cert-page { width: 297mm; height: 210mm; background: #fff; position: relative; overflow: hidden; }
.cert-border { position: absolute; inset: 8mm; border: 2px solid #b8860b; }
.cert-border-inner { position: absolute; inset: 11mm; border: 1px solid #d4a843; }
.cert-corner { position: absolute; width: 60px; height: 60px; }
.cert-corner svg { width: 100%; height: 100%; }
.corner-tl { top: 12mm; left: 12mm; }
.corner-tr { top: 12mm; right: 12mm; transform: scaleX(-1); }
.corner-bl { bottom: 12mm; left: 12mm; transform: scaleY(-1); }
.corner-br { bottom: 12mm; right: 12mm; transform: scale(-1); }
.cert-content { position: absolute; inset: 20mm; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; z-index: 2; }
.cert-watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 140px; font-family: 'Playfair Display', serif; color: rgba(180,160,100,0.04); font-weight: 700; pointer-events: none; white-space: nowrap; z-index: 1; }
.cert-institution { font-size: 14px; text-transform: uppercase; letter-spacing: 6px; color: #b8860b; font-weight: 700; margin-bottom: 8px; }
.cert-title { font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 700; color: #1a2332; margin-bottom: 4px; }
.cert-subtitle { font-size: 13px; color: #6b7280; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 28px; }
.cert-divider { width: 100px; height: 2px; background: linear-gradient(90deg, transparent, #b8860b, transparent); margin: 0 auto 24px; }
.cert-label { font-size: 13px; color: #9ca3af; margin-bottom: 8px; }
.cert-name { font-family: 'Playfair Display', serif; font-size: 34px; color: #1a2332; font-weight: 700; margin-bottom: 24px; }
.cert-for-label { font-size: 13px; color: #9ca3af; margin-bottom: 6px; }
.cert-course { font-size: 22px; font-weight: 700; color: #2453a7; margin-bottom: 28px; }
.cert-date { font-size: 13px; color: #6b7280; }
.cert-footer { position: absolute; bottom: 16mm; left: 20mm; right: 20mm; display: flex; justify-content: space-between; align-items: flex-end; z-index: 2; }
.cert-signature { text-align: center; min-width: 160px; }
.cert-sig-line { width: 160px; border-top: 1px solid #ccc; margin-bottom: 4px; }
.cert-sig-label { font-size: 11px; color: #9ca3af; }
.cert-code { font-size: 10px; color: #b0b0b0; letter-spacing: 1px; text-align: center; }
.cert-seal { width: 64px; height: 64px; border-radius: 50%; border: 2px solid #b8860b; display: flex; align-items: center; justify-content: center; font-size: 28px; color: #b8860b; background: rgba(184,134,11,0.05); }
@media print { body { background: #fff; } .cert-page { box-shadow: none; } body { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
</style>
</head>
<body>
<div class="cert-page">
  <div class="cert-border"></div>
  <div class="cert-border-inner"></div>
  <div class="cert-corner corner-tl"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg></div>
  <div class="cert-corner corner-tr"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg></div>
  <div class="cert-corner corner-bl"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg></div>
  <div class="cert-corner corner-br"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg></div>
  <div class="cert-watermark">CERTIFICAT</div>
  <div class="cert-content">
    <div class="cert-institution">ACATHE CPA</div>
    <div class="cert-title">Certificat de Réussite</div>
    <div class="cert-subtitle">Certificate of Achievement</div>
    <div class="cert-divider"></div>
    <div class="cert-label">Ce certificat est fièrement décerné à</div>
    <div class="cert-name">${name}</div>
    <div class="cert-for-label">Pour avoir complété avec succès le cours</div>
    <div class="cert-course">${courseTitle}</div>
    <div class="cert-date">Délivré le ${issueDate}</div>
  </div>
  <div class="cert-footer">
    <div class="cert-signature">
      <div class="cert-sig-line"></div>
      <div class="cert-sig-label">Directeur Académique</div>
    </div>
    <div class="cert-code">${cert.verification_code ? 'Vérification : ' + cert.verification_code : ''}</div>
    <div class="cert-seal">✦</div>
  </div>
</div>
${autoPrint ? '<script>window.onload=function(){window.print()}<\/script>' : ''}
</body>
</html>`;
};

const handleDownloadCertificate = (cert: CertificateDisplay) => {
  const w = window.open('', '_blank');
  if (!w) return;
  w.document.write(certHtml(cert, studentName.value, true));
  w.document.close();
};

const handlePrintCertificate = (cert: CertificateDisplay) => {
  const w = window.open('', '_blank');
  if (!w) return;
  w.document.write(certHtml(cert, studentName.value, true));
  w.document.close();
};

const handleShareCertificate = (cert: CertificateDisplay) => {
  const text = cert.verification_code
    ? `Certificat ACATHE CPA — ${cert.course_title || 'Cours'} décerné à ${studentName.value} | Code : ${cert.verification_code}`
    : `Certificat ACATHE CPA — ${cert.course_title || 'Cours'} décerné à ${studentName.value}`;
  navigator.clipboard.writeText(text)
    .then(() => alert('Informations du certificat copiées dans le presse-papiers !'))
    .catch(() => alert('Impossible de copier dans le presse-papiers.'));
};
</script>

<template>
  <div class="certificates-page">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <h1 class="page-title mb-1">Mes Certificats</h1>
      <p class="page-subtitle mb-0">Vos réalisations et certifications obtenues</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p class="text-muted mt-3">Chargement des certificats...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger d-flex align-items-center">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-auto" @click="fetchCertificates">Réessayer</button>
    </div>

    <!-- Certificates List -->
    <div v-else-if="certificates.length > 0" class="cert-list">
      <div v-for="cert in certificates" :key="cert.id" class="cert-list-item d-flex align-items-center gap-3">
        <div class="cert-icon-box flex-shrink-0">
          <i class="bi bi-award-fill"></i>
        </div>
        <div class="flex-grow-1 min-w-0">
          <h6 class="mb-0 text-truncate fw-semibold">{{ cert.course_title || `Cours ID ${cert.course_id}` }}</h6>
          <div class="d-flex flex-wrap gap-3 mt-1">
            <small class="text-muted"><i class="bi bi-calendar3 me-1"></i>Délivré le {{ formatDate(cert.issue_date) }}</small>
            <small v-if="cert.verification_code" class="text-success"><i class="bi bi-shield-check me-1"></i>{{ cert.verification_code }}</small>
          </div>
        </div>
        <div class="d-flex gap-2 flex-shrink-0">
          <button class="btn btn-primary-custom btn-sm" @click="openPreview(cert)">
            <i class="bi bi-eye me-1"></i>Prévisualiser
          </button>
          <button class="btn btn-outline-custom btn-sm" @click="handleShareCertificate(cert)" title="Partager le code de vérification">
            <i class="bi bi-share"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <i class="bi bi-award"></i>
      </div>
      <h3>Pas encore de certificats</h3>
      <p class="text-muted">Terminez vos cours pour obtenir vos premiers certificats</p>
      <RouterLink to="/my-courses" class="btn btn-primary-custom">
        <i class="bi bi-plus-lg me-2"></i>Voir mes cours
      </RouterLink>
    </div>

    <!-- Preview Modal -->
    <Teleport to="body">
      <div v-if="previewCert" class="cert-modal-backdrop" @click.self="closePreview">
        <div class="cert-modal">
          <div class="cert-modal-header">
            <h5 class="mb-0"><i class="bi bi-award me-2"></i>Aperçu du certificat</h5>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-success" @click="handleDownloadCertificate(previewCert)">
                <i class="bi bi-file-earmark-pdf me-1"></i>Télécharger PDF
              </button>
              <button class="btn btn-sm btn-outline-light" @click="handlePrintCertificate(previewCert)">
                <i class="bi bi-printer me-1"></i>Imprimer
              </button>
              <button class="btn btn-sm btn-outline-light" @click="closePreview" title="Fermer">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>
          <div class="cert-modal-body">
            <div class="cert-full-preview">
              <div class="cert-full-border"></div>
              <div class="cert-full-border-inner"></div>
              <!-- Corners -->
              <svg class="cert-corner-svg corner-tl" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-tr" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-bl" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-br" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <!-- Watermark -->
              <div class="cert-full-watermark">CERTIFICAT</div>
              <!-- Content -->
              <div class="cert-full-content">
                <div class="cert-full-institution">ACATHE CPA</div>
                <h2 class="cert-full-title">Certificat de Réussite</h2>
                <div class="cert-full-subtitle">Certificate of Achievement</div>
                <div class="cert-full-divider"></div>
                <div class="cert-full-label">Ce certificat est fièrement décerné à</div>
                <div class="cert-full-name">{{ studentName }}</div>
                <div class="cert-full-for">Pour avoir complété avec succès le cours</div>
                <div class="cert-full-course">{{ previewCert.course_title }}</div>
                <div class="cert-full-date">Délivré le {{ formatDate(previewCert.issue_date) }}</div>
              </div>
              <!-- Footer -->
              <div class="cert-full-footer">
                <div class="cert-full-sig">
                  <div class="cert-full-sig-line"></div>
                  <div class="cert-full-sig-label">Directeur Académique</div>
                </div>
                <div class="cert-full-code" v-if="previewCert.verification_code">
                  Vérification : {{ previewCert.verification_code }}
                </div>
                <div class="cert-full-seal">✦</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

.certificates-page {
  max-width: 1100px;
  margin: 0 auto;
}
.page-title { font-size: 1.75rem; font-weight: 700; color: #1a2332; }
.page-subtitle { color: #6b7280; font-size: 0.95rem; }

/* Buttons */
.btn-primary-custom {
  background: #2453a7; color: #fff; border: none; border-radius: 8px;
  font-weight: 500; font-size: 0.8rem;
  &:hover { background: #1a3f8a; color: #fff; }
}
.btn-outline-custom {
  background: transparent; border: 1px solid #e7edf5; color: #4b5563; border-radius: 6px; font-size: 0.8rem;
  &:hover { background: #f6f8fc; border-color: #2453a7; color: #2453a7; }
}

/* Card reduced / list */
.cert-list {
  display: flex; flex-direction: column; gap: 0.75rem;
}
.cert-list-item {
  background: #fff; border: 1px solid #e7edf5; border-radius: 12px;
  padding: 1rem 1.25rem; transition: border-color 0.2s, box-shadow 0.2s;
  &:hover { border-color: #d7e3f4; box-shadow: 0 2px 10px rgba(36,83,167,0.07); }
}
.cert-icon-box {
  width: 48px; height: 48px; border-radius: 12px;
  background: linear-gradient(135deg, #b8860b22, #d4a84322);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  .bi { font-size: 1.4rem; color: #b8860b; }
}

/* ====== Full Preview Modal ====== */
.cert-modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  z-index: 9999; display: flex; align-items: center; justify-content: center;
  padding: 1rem; animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.cert-modal {
  width: 100%; max-width: 960px; background: #1a2332; border-radius: 12px;
  overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.cert-modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 1.25rem; background: #1a2332; color: #fff;
}
.cert-modal-body {
  padding: 1.5rem; background: #2c3444; display: flex; justify-content: center;
}

.cert-full-preview {
  width: 100%; aspect-ratio: 297 / 210; background: #fff; position: relative;
  border-radius: 4px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.cert-full-border { position: absolute; inset: 3%; border: 2px solid #b8860b; }
.cert-full-border-inner { position: absolute; inset: 4%; border: 1px solid #d4a843; }

.cert-corner-svg { position: absolute; width: 40px; height: 40px; }
.corner-tl { top: 4.5%; left: 4.5%; }
.corner-tr { top: 4.5%; right: 4.5%; transform: scaleX(-1); }
.corner-bl { bottom: 4.5%; left: 4.5%; transform: scaleY(-1); }
.corner-br { bottom: 4.5%; right: 4.5%; transform: scale(-1); }

.cert-full-watermark {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  font-size: 6rem; font-family: 'Playfair Display', serif; color: rgba(180,160,100,0.04);
  font-weight: 700; pointer-events: none; white-space: nowrap;
}
.cert-full-content {
  position: absolute; inset: 8%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center; z-index: 2;
}
.cert-full-institution { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 5px; color: #b8860b; font-weight: 700; margin-bottom: 4px; }
.cert-full-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: #1a2332; margin-bottom: 2px; }
.cert-full-subtitle { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; }
.cert-full-divider { width: 60px; height: 2px; background: linear-gradient(90deg, transparent, #b8860b, transparent); margin: 0 auto 14px; }
.cert-full-label { font-size: 0.65rem; color: #9ca3af; margin-bottom: 4px; }
.cert-full-name { font-family: 'Playfair Display', serif; font-size: 1.6rem; color: #1a2332; font-weight: 700; margin-bottom: 14px; }
.cert-full-for { font-size: 0.65rem; color: #9ca3af; margin-bottom: 4px; }
.cert-full-course { font-size: 1.05rem; font-weight: 700; color: #2453a7; margin-bottom: 16px; }
.cert-full-date { font-size: 0.65rem; color: #6b7280; }

.cert-full-footer {
  position: absolute; bottom: 5%; left: 8%; right: 8%;
  display: flex; justify-content: space-between; align-items: flex-end; z-index: 2;
}
.cert-full-sig { text-align: center; }
.cert-full-sig-line { width: 100px; border-top: 1px solid #ccc; margin-bottom: 2px; }
.cert-full-sig-label { font-size: 0.55rem; color: #9ca3af; }
.cert-full-code { font-size: 0.5rem; color: #b0b0b0; letter-spacing: 1px; }
.cert-full-seal {
  width: 40px; height: 40px; border-radius: 50%; border: 2px solid #b8860b;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; color: #b8860b; background: rgba(184,134,11,0.05);
}

/* Empty State */
.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon {
  width: 80px; height: 80px; border-radius: 50%; background: rgba(36,83,167,0.08);
  display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;
  .bi { font-size: 2rem; color: #2453a7; }
}
.empty-state h3 { font-size: 1.2rem; font-weight: 600; color: #1a2332; margin-bottom: 0.5rem; }
</style>