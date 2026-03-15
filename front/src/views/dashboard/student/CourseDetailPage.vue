<template>
  <div class="course-detail">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement du cours…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-banner">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <span>{{ error }}</span>
    </div>

    <template v-else-if="course">
      <!-- ═══ Hero Banner ═══ -->
      <section class="hero">
        <img
          :src="course.image_url || 'https://placehold.co/1200x400/1a2332/ffffff?text=Cours'"
          alt=""
          class="hero-bg"
        >
        <div class="hero-overlay"></div>
        <div class="hero-content">
          <nav class="hero-breadcrumb">
            <RouterLink to="/my-courses">Mes cours</RouterLink>
            <i class="bi bi-chevron-right"></i>
            <span>{{ course.title }}</span>
          </nav>

          <div class="hero-body">
            <div class="hero-main">
              <div class="hero-price" :class="{ free: course.is_free }">
                <template v-if="course.is_free">Gratuit</template>
                <template v-else-if="course.price != null">{{ course.price }} XOF</template>
                <template v-else>—</template>
              </div>
              <h1>{{ course.title }}</h1>
              <p v-if="course.short_description" class="hero-subtitle">{{ course.short_description }}</p>
              <div class="hero-meta">
                <span class="meta-item">
                  <span class="meta-avatar"><i class="bi bi-person-fill"></i></span>
                  {{ course.instructor.name }}
                </span>
                <span class="meta-item">
                  <i class="bi bi-collection"></i>
                  {{ course.sections.length }} section{{ course.sections.length > 1 ? 's' : '' }}
                </span>
                <span class="meta-item">
                  <i class="bi bi-journal-text"></i>
                  {{ totalLessonsCount }} leçon{{ totalLessonsCount > 1 ? 's' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ Progress Strip ═══ -->
      <div class="progress-strip">
        <div class="progress-strip-inner">
          <div class="progress-strip-info">
            <span class="progress-strip-label">Progression</span>
            <span class="progress-strip-badge" :class="progressBadgeClass">{{ progressLabel }}</span>
          </div>
          <div class="progress-strip-bar">
            <div class="progress-strip-fill" :class="progressBarClass" :style="{ width: effectiveProgress + '%' }"></div>
          </div>
          <div class="progress-strip-details">
            <span>{{ completedLessonsTotal }} / {{ totalLessonsCount }} leçons complétées</span>
            <strong :class="progressTextClass">{{ effectiveProgress }}%</strong>
          </div>
        </div>
      </div>

      <!-- ═══ Main Layout ═══ -->
      <div class="main-layout">
        <!-- ── Left Column ── -->
        <div class="content-col">
          <!-- Description -->
          <div v-if="course.description" class="detail-card">
            <h3 class="detail-card-title"><i class="bi bi-info-circle"></i> À propos de ce cours</h3>
            <p class="detail-card-text">{{ course.description }}</p>
          </div>

          <!-- Objectives + Prerequisites -->
          <div class="detail-card" v-if="(course.objectives && course.objectives.length > 0) || (course.prerequisites && course.prerequisites.length > 0)">
            <div v-if="course.objectives && course.objectives.length > 0" class="objectives-block">
              <h3 class="detail-card-title"><i class="bi bi-check-circle-fill"></i> Ce que vous apprendrez</h3>
              <div class="checklist">
                <div v-for="(objective, index) in course.objectives" :key="'obj-' + index" class="check-item">
                  <i class="bi bi-check-lg"></i>
                  <span>{{ objective }}</span>
                </div>
              </div>
            </div>

            <div
              v-if="course.objectives && course.objectives.length > 0 && course.prerequisites && course.prerequisites.length > 0"
              class="detail-divider"
            ></div>

            <div v-if="course.prerequisites && course.prerequisites.length > 0" class="prerequisites-block">
              <h3 class="detail-card-title"><i class="bi bi-list-ul"></i> Prérequis</h3>
              <div class="checklist prereq">
                <div v-for="(prerequisite, index) in course.prerequisites" :key="'pre-' + index" class="check-item">
                  <i class="bi bi-arrow-right-short"></i>
                  <span>{{ prerequisite }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Course Sections -->
          <div class="sections-block">
            <h3 class="sections-title">
              <i class="bi bi-book"></i> Contenu du cours
              <span class="sections-count">{{ course.sections.length }} sections · {{ totalLessonsCount }} leçons</span>
            </h3>

            <div class="section-accordion">
              <div
                v-for="(section, sectionIndex) in course.sections"
                :key="section.id"
                class="section-panel"
                :class="{ complete: isSectionComplete(section), 'in-progress': !isSectionComplete(section) && getCompletedLessonsCount(section) > 0 }"
              >
                <button
                  class="section-header"
                  :class="{ open: sectionIndex === activeSection }"
                  @click="activeSection = activeSection === sectionIndex ? -1 : sectionIndex"
                >
                  <div class="section-header-left">
                    <span class="section-dot" :class="getSectionDotClass(section)"></span>
                    <span class="section-label">Section {{ sectionIndex + 1 }}</span>
                    <span class="section-name">{{ section.title }}</span>
                  </div>
                  <div class="section-header-right">
                    <div class="section-mini-bar">
                      <div :class="getSectionBarClass(section)" :style="{ width: getSectionProgress(section) + '%' }"></div>
                    </div>
                    <span class="section-counter" :class="getSectionCountClass(section)">
                      {{ getCompletedLessonsCount(section) }}/{{ section.lessons.length }}
                    </span>
                    <i class="bi bi-chevron-down section-chevron" :class="{ rotated: sectionIndex === activeSection }"></i>
                  </div>
                </button>

                <div class="section-body" v-show="sectionIndex === activeSection">
                  <div
                    v-for="lesson in section.lessons"
                    :key="lesson.id"
                    class="lesson-row"
                    :class="{ completed: lesson.is_completed }"
                  >
                    <div class="lesson-icon">
                      <i class="bi" :class="lesson.is_completed ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                    </div>
                    <div class="lesson-info">
                      <span class="lesson-title">{{ lesson.title }}</span>
                      <span v-if="lesson.duration" class="lesson-duration"><i class="bi bi-clock"></i> {{ lesson.duration }}</span>
                    </div>
                    <router-link :to="`/lesson/${course.id}/${lesson.id}`" class="lesson-action">
                      {{ lesson.is_completed ? 'Revoir' : 'Commencer' }}
                      <i class="bi bi-arrow-right"></i>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Right Sidebar ── -->
        <aside class="sidebar-col">
          <!-- Progress Card -->
          <div class="sidebar-card progress-card">
            <h4>Votre progression</h4>
            <div class="progress-ring-wrap">
              <div class="progress-ring" :class="progressCircleClass" :style="{ '--progress': effectiveProgress }">
                <div class="progress-ring-inner">
                  <span class="ring-value" :class="progressTextClass">{{ effectiveProgress }}%</span>
                  <span class="ring-label">{{ progressLabel }}</span>
                </div>
              </div>
            </div>

            <div class="sidebar-summary">
              <div
                v-for="(section, idx) in course.sections"
                :key="'summary-' + section.id"
                class="summary-row"
              >
                <i class="bi" :class="isSectionComplete(section) ? 'bi-check-circle-fill text-success' : (getCompletedLessonsCount(section) > 0 ? 'bi-circle-half text-warning' : 'bi-circle text-muted')"></i>
                <span class="summary-name">S{{ idx + 1 }}: {{ section.title }}</span>
                <span class="summary-badge" :class="isSectionComplete(section) ? 'done' : (getCompletedLessonsCount(section) > 0 ? 'wip' : '')">
                  {{ getCompletedLessonsCount(section) }}/{{ section.lessons.length }}
                </span>
              </div>
            </div>

            <div class="sidebar-actions">
              <template v-if="!isEnrolled">
                <button class="btn-continue enroll" @click="openEnrollModal">
                  <i class="bi bi-box-arrow-in-right"></i>
                  {{ course.is_free || !course.price ? "S'inscrire à la formation" : 'Payer et s\'inscrire' }}
                </button>
                <div v-if="course.price && !course.is_free" class="enroll-price-hint">
                  <i class="bi bi-tag-fill"></i> {{ course.price }} XOF
                </div>
              </template>
              <template v-else>
                <button v-if="effectiveProgress < 100" class="btn-continue" @click="continueLastLesson">
                  <i class="bi bi-play-fill"></i> Continuer le cours
                </button>
                <button v-else-if="!certificate?.certificate_url" class="btn-continue success" @click="continueLastLesson">
                  <i class="bi bi-check-circle"></i> Revoir le cours
                </button>
                <button
                  class="btn-certificate"
                  :class="{ earned: certificate?.certificate_url }"
                  @click="handleGetCertificate"
                  :disabled="isCertificateButtonDisabled"
                >
                  <span v-if="isCertificateLoading" class="spinner-border spinner-border-sm" role="status"></span>
                  <i v-else-if="certificate?.certificate_url" class="bi bi-award"></i>
                  <i v-else-if="effectiveProgress === 100" class="bi bi-patch-check"></i>
                  <i v-else class="bi bi-lock"></i>
                  {{ certificateButtonText }}
                </button>
              </template>
            </div>
            <div v-if="certificateError" class="cert-error">{{ certificateError }}</div>
          </div>

          <!-- Notes Card -->
          <div class="sidebar-card">
            <h4><i class="bi bi-journal-text"></i> Mes notes</h4>
            <textarea v-model="notes" rows="5" placeholder="Prenez des notes pendant le cours…"></textarea>
            <button class="btn-save-notes" @click="saveNotes">
              <i class="bi bi-floppy"></i> Enregistrer
            </button>
          </div>
        </aside>
      </div>

      <!-- ═══ Enrollment Modal ═══ -->
      <Teleport to="body">
        <div v-if="showEnrollModal" class="enroll-modal-backdrop" @click.self="closeEnrollModal">
          <div class="enroll-modal">
            <button class="enroll-modal-close" @click="closeEnrollModal"><i class="bi bi-x-lg"></i></button>

            <!-- Success state -->
            <div v-if="enrollSuccess" class="enroll-modal-body enroll-success-state">
              <div class="success-icon"><i class="bi bi-check-circle-fill"></i></div>
              <h3>Inscription réussie !</h3>
              <p>Vous êtes maintenant inscrit à <strong>{{ course.title }}</strong>.</p>
              <button class="enroll-modal-btn primary" @click="closeEnrollModal">
                <i class="bi bi-play-fill"></i> Commencer le cours
              </button>
            </div>

            <!-- Confirm state -->
            <template v-else>
              <div class="enroll-modal-header">
                <div class="enroll-modal-icon" :class="{ free: course.is_free || !course.price }">
                  <i :class="course.is_free || !course.price ? 'bi bi-bookmark-check-fill' : 'bi bi-credit-card-fill'"></i>
                </div>
                <h3>{{ course.is_free || !course.price ? 'Confirmer l\'inscription' : 'Paiement & inscription' }}</h3>
                <p class="enroll-modal-subtitle">{{ course.title }}</p>
              </div>

              <div class="enroll-modal-body">
                <div class="enroll-modal-details">
                  <div class="enroll-detail-row">
                    <span class="detail-label"><i class="bi bi-person"></i> Formateur</span>
                    <span class="detail-value">{{ course.instructor.name }}</span>
                  </div>
                  <div class="enroll-detail-row">
                    <span class="detail-label"><i class="bi bi-collection"></i> Contenu</span>
                    <span class="detail-value">{{ course.sections.length }} sections · {{ totalLessonsCount }} leçons</span>
                  </div>
                  <div class="enroll-detail-row highlight">
                    <span class="detail-label"><i class="bi bi-tag-fill"></i> Prix</span>
                    <span class="detail-value price">
                      <template v-if="course.is_free || !course.price">Gratuit</template>
                      <template v-else>{{ course.price }} XOF</template>
                    </span>
                  </div>
                </div>

                <div v-if="enrollError" class="enroll-error">
                  <i class="bi bi-exclamation-triangle-fill"></i> {{ enrollError }}
                </div>

                <div class="enroll-modal-actions">
                  <button class="enroll-modal-btn secondary" @click="closeEnrollModal" :disabled="enrolling">
                    Annuler
                  </button>
                  <button class="enroll-modal-btn primary" @click="confirmEnroll" :disabled="enrolling">
                    <span v-if="enrolling" class="spinner-border spinner-border-sm"></span>
                    <template v-else>
                      <i :class="course.is_free || !course.price ? 'bi bi-check-lg' : 'bi bi-lock-fill'"></i>
                      {{ course.is_free || !course.price ? "Confirmer l'inscription" : 'Payer ' + course.price + ' XOF' }}
                    </template>
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCourseById, getMyCertificateForCourse, getMyCourseEnrollmentProgress, triggerStudentCertificateCheck, enrollInCourse } from '../../../services/api/course';
import { initiatePayment, confirmPayment } from '../../../services/api/payment';
import type { Course, CourseSection, EnrollmentProgress } from '../../../types/api';
import type { CertificateDisplay } from '../../../types/api';

const route = useRoute()
const router = useRouter()
// const courseStore = useCourseStore() // Remove if not used

// State
const course = ref<Course | null>(null)
const loading = ref(true)
const error = ref('')
const activeSection = ref(0)
const notes = ref('')
const certificate = ref<CertificateDisplay | null>(null);
const isCertificateLoading = ref(false);
const currentEnrollmentProgress = ref<EnrollmentProgress | null>(null);
const certificateEligibilityChecked = ref(false);
const certificateError = ref<string | null>(null);

// Enrollment state
const isEnrolled = ref(false);
const showEnrollModal = ref(false);
const enrolling = ref(false);
const enrollError = ref<string | null>(null);
const enrollSuccess = ref(false);

// Computed progress helpers
const effectiveProgress = computed(() => {
    return currentEnrollmentProgress.value?.progress_percentage ?? course.value?.progress ?? 0;
});

const totalLessonsCount = computed(() => {
    if (!course.value) return 0;
    return course.value.sections.reduce((acc, s) => acc + s.lessons.length, 0);
});

const completedLessonsTotal = computed(() => {
    if (!course.value) return 0;
    return course.value.sections.reduce((acc, s) => acc + getCompletedLessonsCount(s), 0);
});

const progressLabel = computed(() => {
    const p = effectiveProgress.value;
    if (p === 100) return 'Terminé';
    if (p >= 75) return 'Bientôt fini';
    if (p >= 50) return 'Mi-parcours';
    if (p > 0) return 'En cours';
    return 'Non commencé';
});

const progressBadgeClass = computed(() => {
    const p = effectiveProgress.value;
    if (p === 100) return 'bg-success';
    if (p >= 50) return 'bg-warning text-dark';
    if (p > 0) return 'bg-info';
    return 'bg-secondary';
});

const progressBarClass = computed(() => {
    const p = effectiveProgress.value;
    if (p === 100) return 'bg-success';
    if (p >= 75) return 'bg-success';
    if (p >= 50) return 'bg-warning';
    if (p > 0) return 'bg-info';
    return 'bg-secondary';
});

const progressTextClass = computed(() => {
    const p = effectiveProgress.value;
    if (p === 100) return 'text-success';
    if (p >= 50) return 'text-warning';
    if (p > 0) return 'text-info';
    return 'text-muted';
});

const progressCircleClass = computed(() => {
    const p = effectiveProgress.value;
    if (p === 100) return 'circle-success';
    if (p >= 50) return 'circle-warning';
    if (p > 0) return 'circle-info';
    return 'circle-muted';
});

// Section helpers
const isSectionComplete = (section: CourseSection) => {
    return section.lessons.length > 0 && getCompletedLessonsCount(section) === section.lessons.length;
};

const getSectionProgress = (section: CourseSection) => {
    if (section.lessons.length === 0) return 0;
    return Math.round((getCompletedLessonsCount(section) / section.lessons.length) * 100);
};

const getSectionDotClass = (section: CourseSection) => {
    if (isSectionComplete(section)) return 'dot-success';
    if (getCompletedLessonsCount(section) > 0) return 'dot-warning';
    return 'dot-muted';
};

const getSectionBarClass = (section: CourseSection) => {
    if (isSectionComplete(section)) return 'bg-success';
    if (getCompletedLessonsCount(section) > 0) return 'bg-warning';
    return 'bg-secondary';
};

const getSectionCountClass = (section: CourseSection) => {
    if (isSectionComplete(section)) return 'text-success fw-semibold';
    if (getCompletedLessonsCount(section) > 0) return 'text-warning fw-semibold';
    return 'text-muted';
};

// Load course data
const loadCourseDetailsAndProgress = async () => {
    loading.value = true
    error.value = ''
    certificate.value = null;
    currentEnrollmentProgress.value = null;
    certificateEligibilityChecked.value = false; // Reset on load
    certificateError.value = null; // Reset on load

    try {
        const courseIdParam = parseInt(route.params.id as string);
        if (isNaN(courseIdParam)) {
            error.value = "Invalid course ID.";
            loading.value = false;
            return;
        }

        // Fetch full course details from API
        const fetchedCourse = await getCourseById(courseIdParam);
        course.value = fetchedCourse;

        if (course.value && course.value.id) {
            // Fetch student-specific enrollment progress
            try {
                currentEnrollmentProgress.value = await getMyCourseEnrollmentProgress(course.value.id);
                isEnrolled.value = true;
                if (currentEnrollmentProgress.value) {
                    // Update course.value.progress with the fresh progress_percentage
                    course.value.progress = currentEnrollmentProgress.value.progress_percentage;
                    // Update is_completed for all lessons in course.value
                    for (const section of course.value.sections) {
                        for (const lesson of section.lessons) {
                            lesson.is_completed = currentEnrollmentProgress.value.completed_lessons.includes(lesson.id);
                        }
                    }
                }
            } catch (enrollmentErr: any) {
                // 404 or 403 means user is not enrolled
                isEnrolled.value = false;
                console.warn('Not enrolled or failed to load progress:', enrollmentErr.message);
            }

            // Certificate logic based on (potentially updated) progress
            const finalProgress = currentEnrollmentProgress.value?.progress_percentage ?? course.value.progress ?? 0;
            if (finalProgress === 100) {
                // Silently check for an existing certificate
                try {
                    const existingCert = await getMyCertificateForCourse(course.value.id);
                    if (existingCert) {
                        certificate.value = existingCert;
                        certificateEligibilityChecked.value = true; // Already earned
                    }
                } catch (certError: any) {
                    // Non-critical if this fails, user can click button to try issuing
                    if (certError.response && certError.response.status !== 404) {
                         console.warn('Failed to silently load existing certificate:', certError.message);
                    }
                }
            } else {
                certificate.value = null; // Ensure no cert if progress < 100
                certificateEligibilityChecked.value = false;
            }
            activeSection.value = findNextIncompleteSection(); // This should now use updated is_completed
        } else {
            error.value = 'Course data is not available or course ID is missing.';
        }
    } catch (err: any) {
        error.value = err.message || 'Failed to load course details or progress';
    } finally {
        loading.value = false
    }
}

// Helper functions
// Ensure CourseSection and its lessons align with types from api.ts (using is_completed)
const getCompletedLessonsCount = (section: CourseSection) => {
    return section.lessons.filter(lesson => lesson.is_completed).length;
}

const findNextIncompleteSection = () => {
    if (!course.value) return 0;

    for (let i = 0; i < course.value.sections.length; i++) {
        const section = course.value.sections[i];
        if (getCompletedLessonsCount(section) < section.lessons.length) {
            return i;
        }
    }
    return 0; // Default to first section or handle as fully completed
}

// Actions
const continueLastLesson = () => {
    if (!course.value) return;

    const sectionIndex = findNextIncompleteSection();
    const section = course.value.sections[sectionIndex];

    if (section) {
        const incompleteLesson = section.lessons.find(lesson => !lesson.is_completed);
        if (incompleteLesson) {
            // Assuming startLesson was meant to navigate to the lesson viewer
            router.push(`/lesson/${course.value?.id}/${incompleteLesson.id}`);
        } else if (sectionIndex + 1 < course.value.sections.length) {
            // If all lessons in current section completed, try first lesson of next section
            const nextSection = course.value.sections[sectionIndex + 1];
            if (nextSection && nextSection.lessons.length > 0) {
                 router.push(`/lesson/${course.value?.id}/${nextSection.lessons[0].id}`);
            }
        }
    }
}

const handleGetCertificate = async () => {
  certificateError.value = null; // Clear previous errors

  if (certificate.value?.certificate_url) {
    router.push({ name: 'certificates' });
    return;
  }

  if (effectiveProgress.value === 100 && course.value?.id) {
    isCertificateLoading.value = true;
    try {
      // This now calls the POST endpoint that attempts to issue if needed
      const result = await triggerStudentCertificateCheck(course.value.id);
      if (result && typeof result === 'object' && result.certificate_url) { // Successfully issued or found
        certificate.value = result;
        certificateEligibilityChecked.value = true;
        // Optional: show a success message here using a toast or notification
      } else if (typeof result === 'string') { // Backend returned an error/info message string
        certificateError.value = result; // e.g., "NotAllLessonsCompleted", "PointsNotMet"
        certificateEligibilityChecked.value = true; // Checked, but failed
      } else if (!result) { // Should ideally be caught by string check, but if null/undefined
        certificateError.value = "Les conditions pour le certificat ne sont pas encore remplies ou le certificat existe déjà sans URL.";
        certificateEligibilityChecked.value = true;
      }
    } catch (err: any) {
      console.error('Error checking/issuing certificate:', err);
      certificateError.value = err.response?.data?.detail || err.message || "Erreur lors de la vérification du certificat.";
      certificateEligibilityChecked.value = true;
    } finally {
      isCertificateLoading.value = false;
    }
  } else if (effectiveProgress.value < 100) {
    certificateError.value = "Vous devez compléter 100% du cours pour obtenir le certificat.";
  }
};

// Computed property for button text
const certificateButtonText = computed(() => {
  if (certificate.value?.certificate_url) {
    return "Voir le certificat";
  }
  if (effectiveProgress.value === 100) {
    if (certificateEligibilityChecked.value && certificateError.value) {
        return "Réessayer la vérification";
    }
    return "Vérifier l'éligibilité au certificat";
  }
  return "Certificat (Compléter à 100%)";
});

// Computed property for button disabled state
const isCertificateButtonDisabled = computed(() => {
  if (isCertificateLoading.value) return true;
  if (effectiveProgress.value < 100 && !certificate.value?.certificate_url) return true;
  return false;
});

const saveNotes = () => {
    // TODO: Implement notes saving
    console.log('Saving notes:', notes.value)
}

// ── Enrollment actions ──────────────────────────
const openEnrollModal = () => {
  enrollError.value = null;
  enrollSuccess.value = false;
  showEnrollModal.value = true;
};

const closeEnrollModal = () => {
  showEnrollModal.value = false;
  if (enrollSuccess.value) {
    // Reload page data after successful enrollment
    loadCourseDetailsAndProgress();
  }
};

const confirmEnroll = async () => {
  if (!course.value) return;
  enrolling.value = true;
  enrollError.value = null;
  try {
    if (course.value.is_free || !course.value.price || course.value.price <= 0) {
      await enrollInCourse(course.value.id);
    } else {
      const payment = await initiatePayment({
        course_id: course.value.id,
        amount: course.value.price,
        currency: 'XOF',
      });
      await confirmPayment(payment.id);
      await enrollInCourse(course.value.id);
    }
    enrollSuccess.value = true;
    isEnrolled.value = true;
  } catch (err: any) {
    enrollError.value = err.response?.data?.detail || err.message || "Erreur lors de l'inscription.";
  } finally {
    enrolling.value = false;
  }
};

// Load course on mount
onMounted(() => {
    loadCourseDetailsAndProgress();
})
</script>

<style scoped lang="scss">
// ─── Palette ────────────────────────────────────
$primary:      #2453a7;
$primary-dark: #1a3f8a;
$primary-soft:  #eaf2ff;
$dark:         #1a2332;
$gray:         #6b7280;
$gray-light:   #f4f7fb;
$border:       #dfe8f6;
$radius:       14px;
$success:      #10b981;
$warning:      #f59e0b;

.course-detail {
  max-width: 1140px;
  margin: 0 auto;
}

// ─── Loading / Error ────────────────────────────
.loading-state {
  text-align: center;
  padding: 5rem 1rem;

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $border;
    border-top-color: $primary;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin: 0 auto 1rem;
  }
  p { color: $gray; font-size: 0.9rem; }
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.2rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 0.88rem;
}

// ═══════════════════════════════════════════════
// HERO
// ═══════════════════════════════════════════════
.hero {
  position: relative;
  border-radius: $radius;
  overflow: hidden;
  margin-bottom: 0;
  min-height: 260px;
  display: flex;
  align-items: flex-end;
}

.hero-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba($dark, 0.92) 0%,
    rgba($dark, 0.65) 50%,
    rgba($dark, 0.35) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 1.5rem 2rem 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hero-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: rgba(#fff, 0.6);

  a {
    color: rgba(#fff, 0.75);
    text-decoration: none;
    &:hover { color: #fff; }
  }
  i { font-size: 0.6rem; }
  span { color: rgba(#fff, 0.5); }
}

.hero-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 2rem;
}

.hero-main {
  flex: 1;
  min-width: 0;
}

.hero-price {
  display: inline-block;
  background: rgba(#fff, 0.15);
  border: 1px solid rgba(#fff, 0.2);
  color: #fff;
  border-radius: 999px;
  padding: 0.2rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 0.6rem;
  backdrop-filter: blur(4px);

  &.free {
    background: rgba($success, 0.25);
    border-color: rgba($success, 0.4);
    color: lighten($success, 30%);
  }
}

.hero h1 {
  color: #fff;
  font-size: 1.65rem;
  font-weight: 800;
  line-height: 1.25;
  margin-bottom: 0.3rem;
}

.hero-subtitle {
  color: rgba(#fff, 0.75);
  font-size: 0.92rem;
  margin-bottom: 0.75rem;
  max-width: 600px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: rgba(#fff, 0.8);
  font-size: 0.82rem;

  i { font-size: 0.9rem; }
}

.meta-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(#fff, 0.15);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  i { font-size: 0.75rem; color: #fff; }
}

// ═══════════════════════════════════════════════
// PROGRESS STRIP
// ═══════════════════════════════════════════════
.progress-strip {
  background: #fff;
  border: 1px solid $border;
  border-top: none;
  border-radius: 0 0 $radius $radius;
  margin-bottom: 1.5rem;
}

.progress-strip-inner {
  padding: 0.85rem 1.5rem;
}

.progress-strip-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-strip-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: $dark;
}

.progress-strip-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  color: #fff;
}

.progress-strip-bar {
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.4rem;
}

.progress-strip-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-strip-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: $gray;
}

// ═══════════════════════════════════════════════
// MAIN LAYOUT
// ═══════════════════════════════════════════════
.main-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
  align-items: start;
}

.content-col {
  min-width: 0;
}

// ── Detail Cards ────────────────────────────────
.detail-card {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 1.3rem 1.5rem;
  margin-bottom: 1.2rem;
}

.detail-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: $dark;
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  i {
    color: $primary;
    font-size: 1rem;
  }

  .objectives-block & i { color: $success; }
}

.detail-card-text {
  font-size: 0.88rem;
  color: $gray;
  line-height: 1.65;
  margin: 0;
}

.detail-divider {
  height: 1px;
  background: $border;
  margin: 1.2rem 0;
}

// Checklists
.checklist {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-item {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font-size: 0.85rem;
  color: $dark;
  line-height: 1.5;

  i {
    margin-top: 0.15rem;
    flex-shrink: 0;
    color: $success;
    font-size: 0.9rem;
  }
}

.checklist.prereq .check-item i {
  color: $primary;
}

// ── Sections Block ──────────────────────────────
.sections-block {
  margin-bottom: 1.5rem;
}

.sections-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: $dark;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;

  i { color: $primary; }
}

.sections-count {
  font-size: 0.75rem;
  font-weight: 500;
  color: $gray;
  margin-left: auto;
}

.section-accordion {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.section-panel {
  background: #fff;
  border: 1px solid $border;
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;

  &.complete { border-left: 3px solid $success; }
  &.in-progress { border-left: 3px solid $warning; }
}

.section-header {
  width: 100%;
  background: none;
  border: none;
  padding: 0.85rem 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: $gray-light; }
  &.open { background: $primary-soft; }
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.section-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-success { background: $success; }
.dot-warning { background: $warning; }
.dot-muted   { background: #ced4da; }

.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: $primary;
  white-space: nowrap;
}

.section-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: $dark;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.section-header-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.section-mini-bar {
  width: 50px;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;

  > div {
    height: 100%;
    border-radius: 2px;
    transition: width 0.4s ease;
  }
}

.section-counter {
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.section-chevron {
  font-size: 0.75rem;
  color: $gray;
  transition: transform 0.25s;

  &.rotated { transform: rotate(180deg); }
}

// Lesson rows
.section-body {
  border-top: 1px solid $border;
}

.lesson-row {
  display: flex;
  align-items: center;
  padding: 0.7rem 1.1rem;
  gap: 0.75rem;
  border-bottom: 1px solid lighten($border, 3%);
  transition: background 0.15s;

  &:last-child { border-bottom: none; }
  &:hover { background: $gray-light; }

  &.completed {
    .lesson-icon i { color: $success; }
    .lesson-title { color: $gray; }
  }
}

.lesson-icon {
  flex-shrink: 0;
  i { font-size: 1.05rem; color: #ced4da; }
}

.lesson-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.lesson-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: $dark;
}

.lesson-duration {
  font-size: 0.72rem;
  color: $gray;
  i { margin-right: 0.2rem; }
}

.lesson-action {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: $primary;
  text-decoration: none;
  padding: 0.3rem 0.7rem;
  border: 1px solid $border;
  border-radius: 8px;
  transition: all 0.2s;

  &:hover {
    background: $primary-soft;
    border-color: $primary;
  }
}

// ═══════════════════════════════════════════════
// SIDEBAR
// ═══════════════════════════════════════════════
.sidebar-col {
  position: sticky;
  top: 1rem;
}

.sidebar-card {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 1.3rem;
  margin-bottom: 1rem;

  h4 {
    font-size: 0.92rem;
    font-weight: 700;
    color: $dark;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;

    i { color: $primary; }
  }
}

.progress-card {
  border-top: 3px solid $primary;
}

// Ring
.progress-ring-wrap {
  text-align: center;
  margin-bottom: 1rem;
}

.progress-ring {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.5s ease;
}

.circle-success { background: conic-gradient($success calc(var(--progress) * 1%), #e9ecef calc(var(--progress) * 1%)); }
.circle-warning { background: conic-gradient($warning calc(var(--progress) * 1%), #e9ecef calc(var(--progress) * 1%)); }
.circle-info    { background: conic-gradient(#0dcaf0 calc(var(--progress) * 1%), #e9ecef calc(var(--progress) * 1%)); }
.circle-muted   { background: conic-gradient(#6c757d calc(var(--progress) * 1%), #e9ecef calc(var(--progress) * 1%)); }

.progress-ring-inner {
  width: 105px;
  height: 105px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-value {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1;
}

.ring-label {
  font-size: 0.68rem;
  color: $gray;
  margin-top: 0.15rem;
}

// Summary list
.sidebar-summary {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-bottom: 1rem;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid lighten($border, 3%);
  font-size: 0.8rem;

  &:last-child { border-bottom: none; }

  > i { flex-shrink: 0; font-size: 0.85rem; }
}

.summary-name {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: $dark;
}

.summary-badge {
  flex-shrink: 0;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: $gray-light;
  color: $gray;

  &.done { background: rgba($success, 0.1); color: $success; }
  &.wip  { background: rgba($warning, 0.12); color: darken($warning, 10%); }
}

// Actions
.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-continue {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem;
  background: $primary;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;

  &:hover { background: $primary-dark; }
  &.success { background: $success; &:hover { background: darken($success, 8%); } }
  &.enroll { background: #10b981; &:hover { background: darken(#10b981, 8%); } }
}

.enroll-price-hint {
  text-align: center;
  font-size: 0.78rem;
  color: $gray;
  i { color: $primary; margin-right: 0.2rem; }
}

.btn-certificate {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.55rem;
  background: #fff;
  color: $primary;
  border: 1.5px solid $border;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) { border-color: $primary; background: $primary-soft; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
  &.earned { background: $success; color: #fff; border-color: $success; &:hover { background: darken($success, 8%); } }
}

.cert-error {
  margin-top: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  font-size: 0.78rem;
  color: #92400e;
}

// Notes
.sidebar-card textarea {
  width: 100%;
  border: 1.5px solid $border;
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  font-size: 0.85rem;
  color: $dark;
  background: $gray-light;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  margin-bottom: 0.6rem;

  &:focus { border-color: $primary; background: #fff; }
}

.btn-save-notes {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem;
  background: $gray-light;
  color: $dark;
  border: 1.5px solid $border;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover { border-color: $primary; color: $primary; }
}

// ─── Bootstrap overrides ────────────────────────
.bg-success  { background-color: $success !important; }
.bg-warning  { background-color: $warning !important; }
.bg-info     { background-color: #0dcaf0 !important; }
.bg-secondary { background-color: #6c757d !important; }

.text-success { color: $success !important; }
.text-warning { color: $warning !important; }
.text-info    { color: #0dcaf0 !important; }
.text-muted   { color: $gray !important; }

// ═══════════════════════════════════════════════
// ENROLLMENT MODAL
// ═══════════════════════════════════════════════
.enroll-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: modalFadeIn 0.2s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.enroll-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  animation: modalSlideUp 0.25s ease;
}

@keyframes modalSlideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.enroll-modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  color: $gray;
  font-size: 1rem;
  cursor: pointer;
  z-index: 1;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  &:hover { background: $gray-light; color: $dark; }
}

.enroll-modal-header {
  padding: 1.5rem 1.5rem 0.75rem;
  text-align: center;

  h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 0.25rem;
  }
}

.enroll-modal-subtitle {
  font-size: 0.85rem;
  color: $gray;
  margin: 0;
}

.enroll-modal-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: $primary-soft;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;

  i { font-size: 1.4rem; color: $primary; }

  &.free {
    background: rgba($success, 0.1);
    i { color: $success; }
  }
}

.enroll-modal-body {
  padding: 0.75rem 1.5rem 1.5rem;
}

.enroll-modal-details {
  background: $gray-light;
  border: 1px solid $border;
  border-radius: 12px;
  padding: 0.15rem 0;
  margin-bottom: 1rem;
}

.enroll-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;

  &:not(:last-child) { border-bottom: 1px solid $border; }

  &.highlight {
    background: rgba($primary, 0.03);
  }
}

.detail-label {
  color: $gray;
  display: flex;
  align-items: center;
  gap: 0.4rem;

  i { color: $primary; font-size: 0.85rem; }
}

.detail-value {
  font-weight: 600;
  color: $dark;

  &.price {
    font-size: 1.05rem;
    font-weight: 800;
    color: $primary;
  }
}

.enroll-error {
  padding: 0.6rem 0.85rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-size: 0.82rem;
  margin-bottom: 1rem;

  i { margin-right: 0.3rem; }
}

.enroll-modal-actions {
  display: flex;
  gap: 0.6rem;
}

.enroll-modal-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.65rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;

  &.primary {
    background: $primary;
    color: #fff;
    &:hover:not(:disabled) { background: $primary-dark; }
  }

  &.secondary {
    background: $gray-light;
    color: $gray;
    border: 1px solid $border;
    &:hover:not(:disabled) { color: $dark; border-color: darken($border, 8%); }
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.enroll-success-state {
  text-align: center;
  padding: 2rem 1.5rem !important;

  h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 0.4rem;
  }

  p {
    font-size: 0.88rem;
    color: $gray;
    margin: 0 0 1.2rem;
  }

  .enroll-modal-btn { max-width: 250px; margin: 0 auto; }
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba($success, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  i { font-size: 2rem; color: $success; }
}

// ─── Responsive ─────────────────────────────────
@media (max-width: 991.98px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .sidebar-col {
    position: static;
  }
}

@media (max-width: 767.98px) {
  .hero {
    min-height: 220px;
  }

  .hero-content {
    padding: 1.2rem 1.2rem 1.4rem;
  }

  .hero h1 {
    font-size: 1.3rem;
  }

  .hero-meta {
    gap: 0.75rem;
  }

  .progress-strip-inner {
    padding: 0.75rem 1rem;
  }

  .detail-card {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .section-header-right {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>