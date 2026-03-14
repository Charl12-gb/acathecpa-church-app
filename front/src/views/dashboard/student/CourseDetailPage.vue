<template>
    <div class="container py-5">
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
            {{ error }}
        </div>

        <template v-else-if="course">
            <!-- Course Header -->
            <div class="row mb-4">
                <div class="col-12">
                    <nav aria-label="breadcrumb" class="mb-4">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <RouterLink to="/my-courses">Mes cours</RouterLink>
                            </li>
                            <li class="breadcrumb-item active" aria-current="page">
                                {{ course.title }}
                            </li>
                        </ol>
                    </nav>

                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h1 class="mb-3">{{ course.title }}</h1>
                                    <p v-if="course.short_description" class="lead text-muted mb-3">{{ course.short_description }}</p>
                                    <p class="mb-4">{{ course.description }}</p>

                                    <!-- Price/Free Status Display -->
                                    <div class="mb-3">
                                        <span v-if="course.is_free" class="badge bg-success fs-5">Gratuit</span>
                                        <span v-else-if="course.price != null" class="badge bg-primary fs-5">Prix: {{ course.price }}XOF</span>
                                        <span v-else class="badge bg-secondary fs-5">Prix non disponible</span>
                                    </div>

                                    <div class="d-flex flex-wrap gap-4 mb-4">
                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-light p-2 me-2">
                                                <i class="bi bi-person-circle text-primary"></i>
                                            </div>
                                            <div>
                                                <small class="text-muted d-block">Instructeur</small>
                                                <span>{{ course.instructor.name }}</span>
                                            </div>
                                        </div>

                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-light p-2 me-2">
                                                <i class="bi bi-book text-primary"></i>
                                            </div>
                                            <div>
                                                <small class="text-muted d-block">Sections</small>
                                                <span>{{ course.sections.length }}</span>
                                            </div>
                                        </div>

                                        <div class="d-flex align-items-center">
                                            <div class="rounded-circle bg-light p-2 me-2">
                                                <i class="bi bi-clock text-primary"></i>
                                            </div>
                                            <div>
                                                <small class="text-muted d-block">Progression</small>
                                                <span>{{ currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0 }}%</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="progress mb-2" style="height: 8px;">
                                        <div class="progress-bar" role="progressbar"
                                            :style="{ width: (currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0) + '%' }"
                                            :aria-valuenow="currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0"
                                            aria-valuemin="0" aria-valuemax="100"></div>
                                    </div>
                                </div>

                                <div class="col-md-4">
                                    <img :src="course.image_url || 'https://placehold.co/400x300?text=Image+Indisponible'"
                                        class="img-fluid rounded" :alt="course.title">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Course Content -->
            <div class="row">
                <div class="col-lg-8">
                    <!-- Objectives and Prerequisites -->
                    <div class="card border-0 shadow-sm mb-4" v-if="course.objectives && course.objectives.length > 0 || course.prerequisites && course.prerequisites.length > 0">
                        <div class="card-body">
                            <div v-if="course.objectives && course.objectives.length > 0" class="mb-4">
                                <h5 class="card-title mb-3"><i class="bi bi-check-circle-fill text-success me-2"></i>Ce que vous apprendrez</h5>
                                <ul class="list-unstyled mb-0">
                                    <li v-for="(objective, index) in course.objectives" :key="'obj-' + index" class="mb-2 d-flex">
                                        <i class="bi bi-check text-success me-2 pt-1"></i>
                                        <span>{{ objective }}</span>
                                    </li>
                                </ul>
                            </div>
                            <hr v-if="course.objectives && course.objectives.length > 0 && course.prerequisites && course.prerequisites.length > 0">
                            <div v-if="course.prerequisites && course.prerequisites.length > 0" class="mt-3">
                                <h5 class="card-title mb-3"><i class="bi bi-list-ul text-primary me-2"></i>Prérequis</h5>
                                <ul class="list-unstyled mb-0">
                                    <li v-for="(prerequisite, index) in course.prerequisites" :key="'pre-' + index" class="mb-2 d-flex">
                                        <i class="bi bi-dot text-primary me-2 pt-1"></i>
                                        <span>{{ prerequisite }}</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Course Sections -->
                    <h4 class="mb-3">Contenu du cours</h4>
                    <div class="accordion mb-4" id="courseSections">
                        <div v-for="(section, sectionIndex) in course.sections" :key="section.id"
                            class="accordion-item border-0 shadow-sm mb-3">
                            <h2 class="accordion-header">
                                <button class="accordion-button" :class="{ collapsed: sectionIndex !== activeSection }"
                                    type="button" data-bs-toggle="collapse" :data-bs-target="'#section-' + section.id"
                                    :aria-expanded="sectionIndex === activeSection"
                                    :aria-controls="'section-' + section.id">
                                    <div class="d-flex justify-content-between align-items-center w-100 me-3">
                                        <span>Section {{ sectionIndex + 1 }}: {{ section.title }}</span>
                                        <small class="text-muted">
                                            {{ getCompletedLessonsCount(section) }}/{{ section.lessons.length }} leçons
                                        </small>
                                    </div>
                                </button>
                            </h2>
                            <div :id="'section-' + section.id" class="accordion-collapse collapse"
                                :class="{ show: sectionIndex === activeSection }" data-bs-parent="#courseSections">
                                <div class="accordion-body">
                                    <div class="list-group list-group-flush">
                                        <div v-for="lesson in section.lessons" :key="lesson.id"
                                            class="list-group-item d-flex justify-content-between align-items-center px-0">
                                            <div class="d-flex align-items-center">
                                                <div class="rounded-circle p-2 me-3"
                                                    :class="lesson.is_completed ? 'bg-success bg-opacity-10' : 'bg-light'">
                                                    <i class="bi" :class="[
                                                        lesson.is_completed ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted',
                                                        lesson.type === 'video' ? 'bi-play-circle' :
                                                            lesson.type === 'quiz' ? 'bi-question-circle' : 'bi-file-text'
                                                    ]"></i>
                                                </div>
                                                <div>
                                                    <h6 class="mb-0">{{ lesson.title }}</h6>
                                                    <small class="text-muted">{{ lesson.duration }}</small>
                                                </div>
                                            </div>
                                            <router-link :to="`/lesson/${course.id}/${lesson.id}`"
                                                class="btn btn-outline-primary btn-sm">
                                                {{ lesson.is_completed ? 'Revoir' : 'Commencer' }}
                                            </router-link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Course Sidebar -->
                <div class="col-lg-4">
                    <!-- Progress Card -->
                    <div class="card border-0 shadow-sm mb-4">
                        <div class="card-body">
                            <h5 class="card-title mb-4">Votre progression</h5>

                            <div class="text-center mb-4">
                                <div class="progress-circle mx-auto mb-3" :style="{'--progress': currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0}">
                                    <div class="progress-circle-inner">
                                        <span class="h3 mb-0">{{ currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0 }}%</span>
                                        <small class="text-muted d-block">Complété</small>
                                    </div>
                                </div>
                            </div>

                            <div class="d-grid gap-2">
                                <button class="btn btn-primary" @click="continueLastLesson">
                                    Continuer le cours
                                </button>
                                <button
                                  class="btn btn-outline-primary"
                                  @click="handleGetCertificate"
                                  :disabled="isCertificateButtonDisabled"
                                >
                                  <span v-if="isCertificateLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                  <i v-if="!isCertificateLoading && certificate?.certificate_url" class="bi bi-award me-2"></i>
                                  <i v-if="!isCertificateLoading && !certificate?.certificate_url && (currentEnrollmentProgress?.progress_percentage ?? course.progress ?? 0) === 100" class="bi bi-patch-check me-2"></i>
                                  {{ certificateButtonText }}
                                </button>
                            </div>
                            <div v-if="certificateError" class="alert alert-warning alert-sm mt-3">
                                {{ certificateError }}
                            </div>
                        </div>
                    </div>

                    <!-- Notes Card -->
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title mb-4">Mes notes</h5>

                            <div class="mb-3">
                                <textarea class="form-control" v-model="notes" rows="5"
                                    placeholder="Prenez des notes pendant le cours..."></textarea>
                            </div>

                            <div class="d-grid">
                                <button class="btn btn-primary" @click="saveNotes">
                                    Enregistrer les notes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCourseById, getMyCertificateForCourse, getMyCourseEnrollmentProgress, triggerStudentCertificateCheck } from '../../../services/api/course';
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
const certificateEligibilityChecked = ref(false); // New state
const certificateError = ref<string | null>(null); // New state for errors

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
            } catch (enrollmentError) {
                console.error('Failed to load enrollment progress:', enrollmentError);
                // Potentially set a specific error message for progress loading failure
                // For now, the page will use course.value.progress which might be stale or 0
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
    window.open(certificate.value.certificate_url, '_blank');
    return;
  }

  const finalProgress = currentEnrollmentProgress.value?.progress_percentage ?? course.value?.progress ?? 0;
  if (finalProgress === 100 && course.value?.id) {
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
      certificateError.value = err.message || "Erreur lors de la vérification du certificat.";
    } finally {
      isCertificateLoading.value = false;
    }
  } else if (finalProgress < 100) {
    certificateError.value = "Vous devez compléter 100% du cours pour obtenir le certificat.";
  }
};

// Computed property for button text
const certificateButtonText = computed(() => {
  if (certificate.value?.certificate_url) {
    return "Voir le certificat";
  }
  const finalProgress = currentEnrollmentProgress.value?.progress_percentage ?? course.value?.progress ?? 0;
  if (finalProgress === 100) {
    if (certificateEligibilityChecked.value && certificateError.value) {
        return "Réessayer la vérification"; // Or just "Vérifier l'éligibilité"
    }
    return "Vérifier l'éligibilité au certificat";
  }
  return "Certificat (Compléter à 100%)";
});

// Computed property for button disabled state
const isCertificateButtonDisabled = computed(() => {
  if (isCertificateLoading.value) return true;
  const finalProgress = currentEnrollmentProgress.value?.progress_percentage ?? course.value?.progress ?? 0;
  if (finalProgress < 100 && !certificate.value?.certificate_url) return true; // Disabled if progress < 100 unless cert already exists
  return false;
});

const saveNotes = () => {
    // TODO: Implement notes saving
    console.log('Saving notes:', notes.value)
}

// Load course on mount
onMounted(() => {
    loadCourseDetailsAndProgress();
})
</script>

<style scoped>
/* Ensure --progress CSS variable is used by progress-circle if not already */
.progress-bar {
    background-color: var(--bs-primary);
}

.progress-circle {
    width: 150px;
    height: 150px;
    background: conic-gradient(var(--bs-primary) calc(var(--progress) * 1%),
            #e9ecef calc(var(--progress) * 1%));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-circle-inner {
    width: 120px;
    height: 120px;
    background: white;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.accordion-button:not(.collapsed) {
    background-color: var(--bs-primary);
    color: white;
}

.accordion-button:not(.collapsed)::after {
    filter: brightness(0) invert(1);
}

.list-group-item {
    border: none;
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.rounded-circle {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>