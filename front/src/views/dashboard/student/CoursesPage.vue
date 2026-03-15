<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import { getMyEnrolledCourses, getMyCourseEnrollmentProgress, getMyCertificateForCourse } from '../../../services/api/course';
import type { Course, CertificateDisplay } from '../../../types/api';
import { useAuthStore } from '../../../stores/auth';

// Define an extended type for courses with their specific progress
type CourseWithProgress = Course & { studentProgressPercentage?: number };

const courses = ref<CourseWithProgress[]>([]);
const isLoading = ref(true); // Set to true initially
const error = ref<string | null>(null);
// Optional: const isFetchingProgress = ref(false); // If you want a separate indicator

// Filter options
const filters = ref({
  status: 'all', // all, in-progress, completed
  sort: 'recent', // recent, progress, alphabetical
});

const fetchMyCoursesAndProgress = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const baseCourses = await getMyEnrolledCourses();
    const enrichedCourses: CourseWithProgress[] = [];

    // isFetchingProgress.value = true; // If using a separate loading state for progress part
    for (const course of baseCourses) {
      let progressPercentage = course.progress; // Use existing progress from course object as a fallback
      try {
        const enrollmentProgress = await getMyCourseEnrollmentProgress(course.id);
        if (enrollmentProgress) {
          progressPercentage = enrollmentProgress.progress_percentage;
        }
      } catch (progressError) {
        console.warn(`Failed to fetch progress for course ${course.id}:`, progressError);
        // If fetching progress fails, use course.progress or default to 0
        if (progressPercentage === undefined || progressPercentage === null) progressPercentage = 0;
      }
      enrichedCourses.push({ ...course, studentProgressPercentage: progressPercentage });
    }
    courses.value = enrichedCourses;
    // isFetchingProgress.value = false;

  } catch (err: any) {
    console.error('Failed to fetch enrolled courses or their progress:', err);
    error.value = err.message || 'Erreur lors du chargement de vos cours et de leur progression.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchMyCoursesAndProgress();
});

// ── Certificate preview modal ─────────────────────────────────────────────
const authStore = useAuthStore();
const studentName = computed(() => authStore.user?.name || 'Étudiant');

const previewCert = ref<CertificateDisplay | null>(null);
const loadingCertificateCourseId = ref<number | null>(null);

const openCertPreview = async (courseId: number) => {
  loadingCertificateCourseId.value = courseId;
  try {
    const certificate = await getMyCertificateForCourse(courseId);
    if (certificate) {
      previewCert.value = certificate;
    }
  } catch (e) {
    console.error('Impossible de charger le certificat', e);
  } finally {
    loadingCertificateCourseId.value = null;
  }
};

const closePreview = () => { previewCert.value = null; };

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' });

const certHtml = (cert: CertificateDisplay, name: string, autoPrint = true) => {
  const issueDate = formatDate(cert.issue_date);
  const courseTitle = cert.course_title || `Cours ID ${cert.course_id}`;
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>Certificat - ${courseTitle}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');
@page { size: A4 landscape; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Lato',sans-serif; background:#f0f0f0; display:flex; justify-content:center; align-items:center; min-height:100vh; }
.cert-page { width:297mm; height:210mm; background:#fff; position:relative; overflow:hidden; }
.cert-border { position:absolute; inset:8mm; border:2px solid #b8860b; }
.cert-border-inner { position:absolute; inset:11mm; border:1px solid #d4a843; }
.cert-corner { position:absolute; width:60px; height:60px; } .cert-corner svg { width:100%; height:100%; }
.corner-tl{top:12mm;left:12mm;} .corner-tr{top:12mm;right:12mm;transform:scaleX(-1);} .corner-bl{bottom:12mm;left:12mm;transform:scaleY(-1);} .corner-br{bottom:12mm;right:12mm;transform:scale(-1);}
.cert-content { position:absolute; inset:20mm; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; z-index:2; }
.cert-watermark { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:140px; font-family:'Playfair Display',serif; color:rgba(180,160,100,0.04); font-weight:700; pointer-events:none; white-space:nowrap; z-index:1; }
.cert-institution { font-size:14px; text-transform:uppercase; letter-spacing:6px; color:#b8860b; font-weight:700; margin-bottom:8px; }
.cert-title { font-family:'Playfair Display',serif; font-size:42px; font-weight:700; color:#1a2332; margin-bottom:4px; }
.cert-subtitle { font-size:13px; color:#6b7280; text-transform:uppercase; letter-spacing:3px; margin-bottom:28px; }
.cert-divider { width:100px; height:2px; background:linear-gradient(90deg,transparent,#b8860b,transparent); margin:0 auto 24px; }
.cert-label { font-size:13px; color:#9ca3af; margin-bottom:8px; }
.cert-name { font-family:'Playfair Display',serif; font-size:34px; color:#1a2332; font-weight:700; margin-bottom:24px; }
.cert-for-label { font-size:13px; color:#9ca3af; margin-bottom:6px; }
.cert-course { font-size:22px; font-weight:700; color:#2453a7; margin-bottom:28px; }
.cert-date { font-size:13px; color:#6b7280; }
.cert-footer { position:absolute; bottom:16mm; left:20mm; right:20mm; display:flex; justify-content:space-between; align-items:flex-end; z-index:2; }
.cert-sig-line { width:160px; border-top:1px solid #ccc; margin-bottom:4px; }
.cert-sig-label { font-size:11px; color:#9ca3af; }
.cert-code { font-size:10px; color:#b0b0b0; letter-spacing:1px; text-align:center; }
.cert-seal { width:64px; height:64px; border-radius:50%; border:2px solid #b8860b; display:flex; align-items:center; justify-content:center; font-size:28px; color:#b8860b; background:rgba(184,134,11,0.05); }
@media print { body{background:#fff;} .cert-page{box-shadow:none;} body{print-color-adjust:exact;-webkit-print-color-adjust:exact;} }
</style></head><body>
<div class="cert-page">
  <div class="cert-border"></div><div class="cert-border-inner"></div>
  <div class="cert-corner corner-tl"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/></svg></div>
  <div class="cert-corner corner-tr"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/></svg></div>
  <div class="cert-corner corner-bl"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/></svg></div>
  <div class="cert-corner corner-br"><svg viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/></svg></div>
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
    <div><div class="cert-sig-line"></div><div class="cert-sig-label">Directeur Académique</div></div>
    <div class="cert-code">${cert.verification_code ? 'Vérification : ' + cert.verification_code : ''}</div>
    <div class="cert-seal">✦</div>
  </div>
</div>
${autoPrint ? '<script>window.onload=function(){window.print()}<\/script>' : ''}
</body></html>`;
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
// ─────────────────────────────────────────────────────────────────────────────

// Computed courses based on filters
const filteredCourses = computed(() => {
  let filtered = [...courses.value];
  
  // Apply status filter
  if (filters.value.status === 'in-progress') {
    filtered = filtered.filter(course => (course.studentProgressPercentage ?? 0) < 100);
  } else if (filters.value.status === 'completed') {
    filtered = filtered.filter(course => (course.studentProgressPercentage ?? 0) === 100);
  }
  
  // Apply sorting
  switch (filters.value.sort) {
    case 'progress':
      filtered.sort((a, b) => (b.studentProgressPercentage ?? 0) - (a.studentProgressPercentage ?? 0));
      break;
    case 'alphabetical':
      filtered.sort((a, b) => a.title.localeCompare(b.title));
      break;
    default: // recent (using updated_at, assuming it reflects recent activity)
      filtered.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  }
  
  return filtered;
});
</script>

<template>
  <div class="student-courses-page">
    <!-- Toolbar : Filters unified -->
    <div class="toolbar">
      <div class="toolbar-top">
        <div class="toolbar-title">
          <h1>Mes Cours</h1>
          <span class="result-count">
            <strong>{{ filteredCourses.length }}</strong> cours{{ filteredCourses.length > 1 ? 's' : '' }}
          </span>
        </div>
        <RouterLink to="/browse-courses" class="btn-explore">
          <i class="bi bi-plus-lg"></i> Explorer les cours
        </RouterLink>
      </div>

      <div class="toolbar-bottom">
        <div class="toolbar-selects">
          <div class="select-wrap">
            <i class="bi bi-funnel"></i>
            <select v-model="filters.status">
              <option value="all">Tous les cours</option>
              <option value="in-progress">En cours</option>
              <option value="completed">Terminés</option>
            </select>
          </div>
          <div class="select-wrap">
            <i class="bi bi-sort-down"></i>
            <select v-model="filters.sort">
              <option value="recent">Plus récents</option>
              <option value="progress">Progression</option>
              <option value="alphabetical">Ordre alphabétique</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement de vos cours…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-banner">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <span>{{ error }}</span>
      <button @click="fetchMyCoursesAndProgress">Réessayer</button>
    </div>

    <!-- Course List -->
    <div v-else-if="filteredCourses.length > 0" class="course-list">
      <article v-for="course in filteredCourses" :key="course.id" class="course-card">
        <!-- Thumbnail -->
        <RouterLink :to="{ name: 'course-detail', params: { id: course.id } }" class="card-thumb">
          <img
            :src="course.image_url || 'https://placehold.co/400x220/e8eef7/2453a7?text=Cours'"
            :alt="course.title"
          >
          <span
            class="thumb-badge"
            :class="{
              completed: (course.studentProgressPercentage ?? 0) === 100,
              'in-progress': (course.studentProgressPercentage ?? 0) > 0 && (course.studentProgressPercentage ?? 0) < 100
            }"
          >
            <template v-if="(course.studentProgressPercentage ?? 0) === 100">
              <i class="bi bi-patch-check-fill"></i> Terminé
            </template>
            <template v-else>
              {{ course.studentProgressPercentage ?? 0 }}%
            </template>
          </span>
        </RouterLink>

        <!-- Body -->
        <div class="card-body">
          <div class="card-header-row">
            <span
              :class="['status-badge', course.status === 'published' ? 'published' : 'draft']"
            >
              {{ course.status === 'published' ? 'Publié' : 'Brouillon' }}
            </span>
            <span class="card-date">
              <i class="bi bi-clock"></i> {{ new Date(course.updated_at).toLocaleDateString('fr-FR') }}
            </span>
          </div>

          <RouterLink :to="{ name: 'course-detail', params: { id: course.id } }" class="card-title">
            {{ course.title }}
          </RouterLink>
          <p class="card-desc">{{ course.short_description || course.description?.substring(0, 130) + '…' }}</p>

          <div class="card-progress">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: (course.studentProgressPercentage ?? 0) + '%' }"></div>
            </div>
            <span class="progress-label">{{ course.studentProgressPercentage ?? 0 }}%</span>
          </div>

          <div class="card-meta">
            <span class="meta-instructor">
              <span class="instructor-avatar"><i class="bi bi-person-fill"></i></span>
              {{ course.instructor.name }}
            </span>
          </div>
        </div>

        <!-- Side panel -->
        <div class="card-side">
          <template v-if="(course.studentProgressPercentage ?? 0) < 100">
            <RouterLink
              class="btn-action primary"
              :to="{ name: 'course-detail', params: { id: course.id } }"
            >
              <i class="bi bi-play-fill"></i> Continuer
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink
              class="btn-action outline"
              :to="{ name: 'course-detail', params: { id: course.id } }"
            >
              <i class="bi bi-eye"></i> Revoir
            </RouterLink>
            <button
              class="btn-action cert"
              :disabled="loadingCertificateCourseId === course.id"
              @click="openCertPreview(course.id)"
            >
              <span v-if="loadingCertificateCourseId === course.id" class="spinner-border spinner-border-sm"></span>
              <template v-else>
                <i class="bi bi-award-fill"></i> Certificat
              </template>
            </button>
          </template>
          <RouterLink
            :to="{ name: 'course-detail', params: { id: course.id } }"
            class="btn-details"
          >
            Voir détails <i class="bi bi-arrow-right"></i>
          </RouterLink>
        </div>
      </article>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-illustration">
        <i class="bi bi-journal-x"></i>
      </div>
      <h3>Aucun cours trouvé</h3>
      <p>Ajustez vos filtres ou explorez notre catalogue de cours</p>
      <RouterLink to="/browse-courses" class="btn-reset">
        <i class="bi bi-plus-lg"></i> Explorer les cours
      </RouterLink>
    </div>

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
              <svg class="cert-corner-svg corner-tl" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-tr" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-bl" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <svg class="cert-corner-svg corner-br" viewBox="0 0 60 60"><path d="M0,60 Q0,0 60,0" fill="none" stroke="#b8860b" stroke-width="1.5"/><path d="M10,60 Q10,10 60,10" fill="none" stroke="#d4a843" stroke-width="0.8"/></svg>
              <div class="cert-full-watermark">CERTIFICAT</div>
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
              <div class="cert-full-footer">
                <div class="cert-full-sig">
                  <div class="cert-full-sig-line"></div>
                  <div class="cert-full-sig-label">Directeur Académique</div>
                </div>
                <div v-if="previewCert.verification_code" class="cert-full-code">
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
// ─── Palette ────────────────────────────────────
$primary:     #2453a7;
$primary-dark:#1a3f8a;
$primary-soft:#eaf2ff;
$dark:        #1a2332;
$gray:        #6b7280;
$gray-light:  #f4f7fb;
$border:      #dfe8f6;
$radius:      14px;

.student-courses-page {
  max-width: 1140px;
  margin: 0 auto;
}

// ─── Toolbar ─────────────────────────────────────
.toolbar {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(16, 24, 40, 0.04);
}

.toolbar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.toolbar-title {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;

  h1 {
    font-size: 1.45rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}

.result-count {
  font-size: 0.78rem;
  color: $gray;
  white-space: nowrap;
  strong { color: $primary; font-weight: 700; }
}

.btn-explore {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.1rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s;
  &:hover { background: $primary-dark; color: #fff; }
}

.toolbar-bottom {
  padding-top: 0.75rem;
  border-top: 1px solid lighten($border, 3%);
}

.toolbar-selects {
  display: flex;
  gap: 0.5rem;
}

.select-wrap {
  position: relative;
  display: flex;
  align-items: center;

  > i {
    position: absolute;
    left: 0.65rem;
    color: $primary;
    font-size: 0.78rem;
    pointer-events: none;
  }

  select {
    border: 1.5px solid $border;
    border-radius: 10px;
    padding: 0.55rem 1.8rem 0.55rem 2rem;
    font-size: 0.82rem;
    color: $dark;
    background: $gray-light;
    appearance: auto;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s;
    &:focus { border-color: $primary; }
  }
}

// ─── Loading ────────────────────────────────────
.loading-state {
  text-align: center;
  padding: 4rem 1rem;

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $border;
    border-top-color: $primary;
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    margin: 0 auto 1rem;
  }

  p { color: $gray; font-size: 0.9rem; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// ─── Error banner ───────────────────────────────
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1.2rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 0.88rem;

  button {
    margin-left: auto;
    background: none;
    border: 1px solid #dc2626;
    color: #dc2626;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    cursor: pointer;
    &:hover { background: #dc2626; color: #fff; }
  }
}

// ─── Course List ────────────────────────────────
.course-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

// ─── Course Card (horizontal) ───────────────────
.course-card {
  display: flex;
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  overflow: hidden;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;

  &:hover {
    border-color: lighten($primary, 28%);
    box-shadow: 0 8px 30px rgba($primary, 0.1);
  }
}

// ── Thumbnail ───────────────────────────────────
.card-thumb {
  position: relative;
  flex-shrink: 0;
  width: 260px;
  height: 200px;
  overflow: hidden;
  display: block;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
  }

  .course-card:hover & img {
    transform: scale(1.06);
  }
}

.thumb-badge {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  background: rgba(#fff, 0.95);
  color: $primary-dark;
  border-radius: 8px;
  padding: 0.2rem 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

  &.completed {
    background: #10b981;
    color: #fff;
  }

  &.in-progress {
    background: $primary;
    color: #fff;
  }
}

// ── Body (center) ───────────────────────────────
.card-body {
  flex: 1;
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.card-header-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}

.status-badge {
  border-radius: 6px;
  padding: 0.15rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;

  &.published { background: #dcfce7; color: #15803d; }
  &.draft     { background: #f3f4f6; color: #6b7280; }
}

.card-date {
  font-size: 0.72rem;
  color: $gray;
  i { margin-right: 0.2rem; }
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  line-height: 1.35;
  margin-bottom: 0.3rem;
  text-decoration: none;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.15s;
  &:hover { color: $primary; }
}

.card-desc {
  font-size: 0.82rem;
  color: $gray;
  line-height: 1.55;
  margin-bottom: 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

// ── Progress bar ────────────────────────────────
.card-progress {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.6rem;
}

.progress-track {
  flex: 1;
  height: 6px;
  background: #eef3fb;
  border-radius: 99px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary, #2f6ed8);
  border-radius: 99px;
  transition: width 0.4s ease;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: $primary;
  white-space: nowrap;
}

// ── Meta ────────────────────────────────────────
.card-meta {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.meta-instructor {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: $dark;
}

.instructor-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: $primary-soft;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  i { color: $primary; font-size: 0.75rem; }
}

// ── Side panel (right) ──────────────────────────
.card-side {
  flex-shrink: 0;
  width: 150px;
  padding: 1rem 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border-left: 1px solid $border;
  background: $gray-light;
}

.btn-action {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem 0.6rem;
  border: none;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s, transform 0.15s;

  &.primary {
    background: $primary;
    color: #fff;
    &:hover { background: $primary-dark; transform: translateY(-1px); color: #fff; }
  }

  &.outline {
    background: #fff;
    color: $primary;
    border: 1.5px solid $border;
    &:hover { border-color: $primary; background: $primary-soft; color: $primary; }
  }

  &.cert {
    background: linear-gradient(135deg, #b8860b, #d4a843);
    color: #fff;
    &:hover { background: linear-gradient(135deg, #9a7209, #b8860b); transform: translateY(-1px); }
    &:disabled { opacity: 0.6; cursor: not-allowed; }
  }
}

.btn-details {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: $primary;
  text-decoration: none;
  transition: gap 0.2s;
  &:hover { gap: 0.5rem; text-decoration: underline; }
}

// ─── Empty state ────────────────────────────────
.empty-state {
  text-align: center;
  padding: 4.5rem 2rem;
}

.empty-illustration {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: $primary-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  i { font-size: 2.2rem; color: $primary; }
}

.empty-state h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: $dark;
  margin-bottom: 0.4rem;
}

.empty-state p {
  color: $gray;
  font-size: 0.88rem;
  max-width: 340px;
  margin: 0 auto 1.3rem;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.3rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s;
  &:hover { background: $primary-dark; color: #fff; }
}

// ─── Certificate Modal ──────────────────────────
.cert-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.cert-modal {
  width: 100%;
  max-width: 960px;
  background: $dark;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

.cert-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  background: $dark;
  color: #fff;
}

.cert-modal-body {
  padding: 1.5rem;
  background: #2c3444;
  display: flex;
  justify-content: center;
}

.cert-full-preview {
  width: 100%;
  aspect-ratio: 297 / 210;
  background: #fff;
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0,0,0,0.3);
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
  font-size: 6rem; font-family: 'Playfair Display', serif;
  color: rgba(180,160,100,0.04); font-weight: 700;
  pointer-events: none; white-space: nowrap;
}

.cert-full-content {
  position: absolute; inset: 8%;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; z-index: 2;
}

.cert-full-institution { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 5px; color: #b8860b; font-weight: 700; margin-bottom: 4px; }
.cert-full-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: $dark; margin-bottom: 2px; }
.cert-full-subtitle { font-size: 0.65rem; color: $gray; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; }
.cert-full-divider { width: 60px; height: 2px; background: linear-gradient(90deg, transparent, #b8860b, transparent); margin: 0 auto 14px; }
.cert-full-label { font-size: 0.65rem; color: #9ca3af; margin-bottom: 4px; }
.cert-full-name { font-family: 'Playfair Display', serif; font-size: 1.6rem; color: $dark; font-weight: 700; margin-bottom: 14px; }
.cert-full-for { font-size: 0.65rem; color: #9ca3af; margin-bottom: 4px; }
.cert-full-course { font-size: 1.05rem; font-weight: 700; color: $primary; margin-bottom: 16px; }
.cert-full-date { font-size: 0.65rem; color: $gray; }

.cert-full-footer {
  position: absolute; bottom: 5%; left: 8%; right: 8%;
  display: flex; justify-content: space-between;
  align-items: flex-end; z-index: 2;
}

.cert-full-sig { text-align: center; }
.cert-full-sig-line { width: 100px; border-top: 1px solid #ccc; margin-bottom: 2px; }
.cert-full-sig-label { font-size: 0.55rem; color: #9ca3af; }
.cert-full-code { font-size: 0.5rem; color: #b0b0b0; letter-spacing: 1px; }
.cert-full-seal {
  width: 40px; height: 40px; border-radius: 50%;
  border: 2px solid #b8860b;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; color: #b8860b;
  background: rgba(184,134,11,0.05);
}

// ─── Responsive ─────────────────────────────────
@media (max-width: 767.98px) {
  .toolbar-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-selects {
    flex-direction: column;
    width: 100%;
    .select-wrap {
      width: 100%;
      select { width: 100%; }
    }
  }

  .course-card {
    flex-direction: column;
  }

  .card-thumb {
    width: 100%;
    height: 210px;
  }

  .card-side {
    width: 100%;
    border-left: none;
    border-top: 1px solid $border;
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0.75rem 1rem;
    justify-content: center;
  }

  .btn-action { width: auto; flex: 1; min-width: 100px; }
}
</style>