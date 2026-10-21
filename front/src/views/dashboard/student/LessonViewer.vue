<template>
  <div class="container-fluid py-5">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
      <div v-if="notEnrolled && course" class="mt-2">
        <RouterLink :to="`/course/${course.id}`" class="btn btn-sm btn-primary">Voir le cours et s'inscrire</RouterLink>
      </div>
    </div>

    <template v-else-if="course && currentStep">
      <!-- Navigation Header -->
      <div class="row mb-4">
        <div class="col-12">
          <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm rounded">
            <div class="container-fluid">
              <RouterLink :to="`/course/${course.id}`" class="navbar-brand">
                <i class="bi bi-arrow-left me-2"></i>{{ course.title }}
              </RouterLink>

              <div class="d-flex align-items-center">
                <div class="me-3">
                  <div class="progress" style="width: 200px; height: 8px;">
                    <div class="progress-bar" role="progressbar" :style="{ width: progressPercent + '%' }"
                      :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <small class="text-muted">{{ progressPercent }}% complété</small>
                </div>

                <div class="btn-group">
                  <button class="btn btn-outline-primary" @click="goToStep(stepIndex - 1)" :disabled="stepIndex <= 0" aria-label="Étape précédente">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button class="btn btn-outline-primary" @click="goToStep(stepIndex + 1)" :disabled="stepIndex >= steps.length - 1" aria-label="Étape suivante">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </div>
              </div>
            </div>
          </nav>
        </div>
      </div>

      <div class="row">
        <!-- Step Content -->
        <div class="col-lg-9">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body">
              <p class="text-muted small mb-1">{{ currentStep.section.title }}</p>

              <!-- Section introduction (its own text or video) -->
              <template v-if="currentStep.kind === 'intro'">
                <h2 class="mb-4">{{ currentStep.section.title }}</h2>
                <div v-if="currentStep.section.video_url" class="ratio ratio-16x9 mb-4">
                  <iframe :src="embedVideoUrl(currentStep.section.video_url)" allowfullscreen></iframe>
                </div>
                <div v-if="currentStep.section.text_content" class="lesson-content" v-html="currentStep.section.text_content"></div>
                <div class="mt-5 pt-4 border-top text-center">
                  <button class="btn btn-primary btn-lg" @click="goToStep(stepIndex + 1)" :disabled="stepIndex >= steps.length - 1">
                    Continuer
                  </button>
                </div>
              </template>

              <!-- Lesson -->
              <template v-else-if="currentStep.kind === 'lesson' && currentStep.lesson">
                <h2 class="mb-4">{{ currentStep.lesson.title }}</h2>
                <div v-if="currentStep.lesson.video_url" class="ratio ratio-16x9 mb-4">
                  <iframe :src="embedVideoUrl(currentStep.lesson.video_url)" allowfullscreen></iframe>
                </div>
                <div v-if="currentStep.lesson.content_body" class="lesson-content" v-html="currentStep.lesson.content_body"></div>
                <p v-if="!currentStep.lesson.video_url && !currentStep.lesson.content_body" class="text-muted">
                  Cette leçon n'a pas encore de contenu.
                </p>

                <div class="mt-5 pt-4 border-top text-center">
                  <button v-if="!isStepDone(currentStep)" class="btn btn-primary btn-lg" @click="completeLesson" :disabled="isCompleting">
                    <span v-if="isCompleting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Marquer la leçon comme terminée et continuer
                  </button>
                  <template v-else>
                    <button class="btn btn-success btn-lg me-2" disabled>
                      <i class="bi bi-check-circle me-2"></i>Leçon terminée
                    </button>
                    <button v-if="stepIndex < steps.length - 1" class="btn btn-outline-primary btn-lg" @click="goToStep(stepIndex + 1)">
                      Étape suivante
                    </button>
                  </template>
                </div>
              </template>

              <!-- Quiz -->
              <template v-else-if="currentStep.kind === 'quiz'">
                <h2 class="mb-2">Quiz : {{ currentStep.section.test?.title }}</h2>
                <p v-if="currentStep.section.test?.description" class="text-muted">{{ currentStep.section.test.description }}</p>

                <div v-if="isLoadingQuiz" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Chargement du quiz...</span>
                  </div>
                </div>

                <template v-else-if="quiz">
                  <ul class="list-unstyled text-muted small mb-4">
                    <li>{{ quiz.questions?.length || 0 }} question(s)</li>
                    <li>Score requis : {{ quiz.passing_score ?? 70 }} %</li>
                    <li v-if="quiz.max_attempts">Tentatives : {{ quizAttempts.length }} / {{ quiz.max_attempts }}</li>
                  </ul>

                  <!-- Last result -->
                  <div v-if="lastAttempt && !quizInProgress" class="quiz-results mb-4" :class="lastAttempt.passed ? 'border-success' : 'border-danger'">
                    <h5>Résultat de votre tentative n° {{ lastAttempt.attempt_number }}</h5>
                    <p class="mb-1">Score : {{ lastAttempt.score }} % ({{ lastAttempt.points_earned }} / {{ lastAttempt.points_possible }} points)</p>
                    <p :class="lastAttempt.passed ? 'text-success fw-bold' : 'text-danger fw-bold'" class="mb-0">
                      {{ lastAttempt.passed ? 'Réussi' : 'Échoué' }}
                    </p>
                  </div>

                  <div v-if="quizError" class="alert alert-warning">{{ quizError }}</div>

                  <!-- Questions -->
                  <form v-if="quizInProgress" @submit.prevent="handleQuizSubmit">
                    <div v-for="(question, qIndex) in quiz.questions" :key="question.id" class="quiz-question">
                      <p><strong>{{ qIndex + 1 }}. {{ question.question_text }}</strong> ({{ question.points }} point{{ question.points > 1 ? 's' : '' }})</p>
                      <div v-if="question.options?.length" class="quiz-options">
                        <div v-for="(option, optIndex) in question.options" :key="optIndex" class="form-check">
                          <input class="form-check-input" type="radio" :name="`question-${question.id}`"
                            :id="`option-${question.id}-${optIndex}`" :value="optIndex" v-model="userAnswers[question.id]">
                          <label class="form-check-label" :for="`option-${question.id}-${optIndex}`">{{ option.text }}</label>
                        </div>
                      </div>
                      <p v-else class="text-muted small">Question ouverte : elle n'est pas notée automatiquement.</p>
                    </div>
                    <p v-if="unansweredCount > 0" class="text-muted small">{{ unansweredCount }} question(s) sans réponse.</p>
                    <button type="submit" class="btn btn-success" :disabled="isSubmittingQuiz">
                      <span v-if="isSubmittingQuiz" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Soumettre mes réponses
                    </button>
                    <button type="button" class="btn btn-link" @click="quizInProgress = false">Annuler</button>
                  </form>

                  <template v-else>
                    <button v-if="canAttemptQuiz" class="btn btn-primary" @click="startQuiz">
                      <i class="bi bi-play-circle me-2"></i>{{ quizAttempts.length ? 'Repasser le quiz' : 'Commencer le quiz' }}
                    </button>
                    <p v-else-if="!quizPassed" class="text-muted">Nombre maximum de tentatives atteint.</p>
                    <button v-if="quizPassed && stepIndex < steps.length - 1" class="btn btn-outline-primary ms-2" @click="goToStep(stepIndex + 1)">
                      Étape suivante
                    </button>
                  </template>
                </template>
              </template>

              <!-- End of course -->
              <div v-if="progressPercent >= 100" class="alert alert-success mt-4 mb-0">
                <i class="bi bi-trophy me-2"></i>Vous avez terminé ce cours.
                <RouterLink :to="`/course/${course.id}`" class="alert-link">Obtenir mon certificat</RouterLink>
              </div>
            </div>
          </div>
        </div>

        <!-- Course Outline -->
        <div class="col-lg-3">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white py-3">
              <h5 class="mb-0">Plan du cours</h5>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <template v-for="section in course.sections" :key="section.id">
                  <div class="list-group-item bg-light">
                    <strong>{{ section.title }}</strong>
                    <small class="text-muted d-block">
                      {{ completedLessonsIn(section) }}/{{ section.lessons.length }} leçons
                      <span v-if="isSectionDone(section)" class="text-success"> · terminée</span>
                    </small>
                  </div>
                  <button v-for="step in stepsOf(section)" :key="step.key" type="button"
                    class="list-group-item list-group-item-action"
                    :class="{ active: step.key === currentStep.key }"
                    @click="goToStep(steps.indexOf(step))">
                    <div class="d-flex align-items-center">
                      <i class="bi me-2" :class="isStepDone(step) ? 'bi-check-circle-fill' : stepIcon(step)"></i>
                      <div>
                        <div class="small">{{ stepLabel(step) }}</div>
                        <small v-if="step.lesson?.duration" class="text-muted">{{ step.lesson.duration }}</small>
                      </div>
                    </div>
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="course" class="alert alert-info">Ce cours ne contient encore aucune leçon.</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
    getCourseById,
    fetchFullCourseTest,
    submitStudentTestAttempt,
    markStudentLessonCompleted,
    getMyCourseEnrollmentProgress,
} from '../../../services/api/course';
import type {
    Course, CourseSection, CourseLesson,
    CourseTest, EnrollmentProgress, TestAttemptResult,
} from '../../../types/api';

/**
 * The course is walked as a flat list of steps. For each section, in order:
 *   - its own text/video, if it has some ("intro")
 *   - its lessons
 *   - its quiz, if it has one
 *
 * Routes: /lesson/:courseId/:lessonId            -> a lesson
 *         /lesson/:courseId/section/:sectionId    -> a section's intro
 *         /lesson/:courseId/section/:sectionId/quiz -> a section's quiz
 */
interface Step {
  key: string;
  kind: 'intro' | 'lesson' | 'quiz';
  section: CourseSection;
  lesson?: CourseLesson;
}

const route = useRoute();
const router = useRouter();

const course = ref<Course | null>(null);
const progress = ref<EnrollmentProgress | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const notEnrolled = ref(false);
const isCompleting = ref(false);

// Quiz state
const quiz = ref<CourseTest | null>(null);
const isLoadingQuiz = ref(false);
const quizInProgress = ref(false);
const isSubmittingQuiz = ref(false);
const quizError = ref<string | null>(null);
const userAnswers = ref<Record<number, number | undefined>>({});

// --------------------------------------------------------------------------- //
// Steps
// --------------------------------------------------------------------------- //
const hasQuiz = (section: CourseSection) => !!section.test?.id;

const stepsOf = (section: CourseSection): Step[] => {
  const out: Step[] = [];
  if (section.text_content || section.video_url) {
    out.push({ key: `s${section.id}`, kind: 'intro', section });
  }
  for (const lesson of section.lessons) {
    out.push({ key: `l${lesson.id}`, kind: 'lesson', section, lesson });
  }
  if (hasQuiz(section)) {
    out.push({ key: `q${section.id}`, kind: 'quiz', section });
  }
  return out;
};

const steps = computed<Step[]>(() => (course.value ? course.value.sections.flatMap(stepsOf) : []));

const currentKey = computed(() => {
  if (route.params.sectionId) {
    return `${route.params.part === 'quiz' ? 'q' : 's'}${route.params.sectionId}`;
  }
  return `l${route.params.lessonId}`;
});

const stepIndex = computed(() => {
  const i = steps.value.findIndex(s => s.key === currentKey.value);
  return i === -1 ? 0 : i;
});
const currentStep = computed<Step | null>(() => steps.value[stepIndex.value] ?? null);

const stepPath = (step: Step) => {
  const base = `/lesson/${course.value!.id}`;
  if (step.kind === 'lesson') return `${base}/${step.lesson!.id}`;
  return `${base}/section/${step.section.id}${step.kind === 'quiz' ? '/quiz' : ''}`;
};

const goToStep = (index: number) => {
  const step = steps.value[index];
  if (step) router.push(stepPath(step));
};

const stepLabel = (step: Step) =>
  step.kind === 'lesson' ? step.lesson!.title : step.kind === 'quiz' ? `Quiz : ${step.section.test?.title ?? ''}` : 'Introduction';

const stepIcon = (step: Step) => {
  if (step.kind === 'quiz') return 'bi-question-circle';
  if (step.kind === 'intro') return 'bi-info-circle';
  return step.lesson?.type === 'video' ? 'bi-play-circle' : 'bi-file-text';
};

// --------------------------------------------------------------------------- //
// Progress
// --------------------------------------------------------------------------- //
const progressPercent = computed(() => Math.round(progress.value?.progress_percentage ?? 0));

const attemptsFor = (testId?: number): TestAttemptResult[] =>
  (progress.value?.test_attempts ?? []).filter(a => a.test_id === testId);

const isStepDone = (step: Step): boolean => {
  if (step.kind === 'lesson') return !!progress.value?.completed_lessons.includes(step.lesson!.id);
  if (step.kind === 'quiz') return attemptsFor(step.section.test?.id).some(a => a.passed);
  return false;
};

const completedLessonsIn = (section: CourseSection) =>
  section.lessons.filter(l => progress.value?.completed_lessons.includes(l.id)).length;

const isSectionDone = (section: CourseSection) => !!progress.value?.completed_sections.includes(section.id);

// --------------------------------------------------------------------------- //
// Quiz
// --------------------------------------------------------------------------- //
const quizAttempts = computed(() => attemptsFor(quiz.value?.id));
const lastAttempt = computed(() => quizAttempts.value[quizAttempts.value.length - 1] ?? null);
const quizPassed = computed(() => quizAttempts.value.some(a => a.passed));
const canAttemptQuiz = computed(() =>
  !!quiz.value && (!quiz.value.max_attempts || quizAttempts.value.length < quiz.value.max_attempts));
const unansweredCount = computed(() =>
  (quiz.value?.questions ?? []).filter(q => q.options?.length && userAnswers.value[q.id] === undefined).length);

const loadQuiz = async () => {
  quiz.value = null;
  quizInProgress.value = false;
  quizError.value = null;
  const testId = currentStep.value?.kind === 'quiz' ? currentStep.value.section.test?.id : undefined;
  if (!testId) return;
  isLoadingQuiz.value = true;
  try {
    quiz.value = await fetchFullCourseTest(testId);
  } catch (err: any) {
    quizError.value = err.response?.data?.detail || 'Impossible de charger le quiz.';
  } finally {
    isLoadingQuiz.value = false;
  }
};

const startQuiz = () => {
  userAnswers.value = {};
  quizError.value = null;
  quizInProgress.value = true;
};

const handleQuizSubmit = async () => {
  if (!quiz.value || !course.value) return;
  isSubmittingQuiz.value = true;
  quizError.value = null;
  try {
    progress.value = await submitStudentTestAttempt(course.value.id, quiz.value.id, {
      answers: (quiz.value.questions ?? []).map(q => ({
        question_id: q.id,
        answer: userAnswers.value[q.id] ?? null,
      })),
    });
    quizInProgress.value = false;
  } catch (err: any) {
    quizError.value = err.response?.data?.detail || 'Erreur lors de la soumission du quiz.';
  } finally {
    isSubmittingQuiz.value = false;
  }
};

// --------------------------------------------------------------------------- //
// Lessons
// --------------------------------------------------------------------------- //
const completeLesson = async () => {
  const step = currentStep.value;
  if (!course.value || !step?.lesson) return;
  isCompleting.value = true;
  try {
    progress.value = await markStudentLessonCompleted(course.value.id, step.lesson.id);
    if (stepIndex.value < steps.value.length - 1) goToStep(stepIndex.value + 1);
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Impossible d\'enregistrer la leçon.';
  } finally {
    isCompleting.value = false;
  }
};

const embedVideoUrl = (url: string | null | undefined): string => {
  if (!url) return '';
  if (url.includes('youtube.com/watch?v=')) {
    return `https://www.youtube.com/embed/${url.split('v=')[1].split('&')[0]}`;
  }
  if (url.includes('youtu.be/')) {
    return `https://www.youtube.com/embed/${url.split('youtu.be/')[1].split('?')[0]}`;
  }
  if (url.includes('vimeo.com/') && !url.includes('player.vimeo.com')) {
    return `https://player.vimeo.com/video/${url.split('/').pop()}`;
  }
  return url;
};

// --------------------------------------------------------------------------- //
// Loading
// --------------------------------------------------------------------------- //
const loadCourse = async () => {
  loading.value = true;
  error.value = null;
  notEnrolled.value = false;
  const courseId = Number(route.params.courseId);
  if (!courseId) {
    error.value = 'Cours introuvable.';
    loading.value = false;
    return;
  }
  try {
    course.value = await getCourseById(courseId);
    try {
      progress.value = await getMyCourseEnrollmentProgress(courseId);
    } catch {
      notEnrolled.value = true;
      error.value = "Vous n'êtes pas inscrit à ce cours.";
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Erreur lors du chargement du cours.';
  } finally {
    loading.value = false;
  }
  await loadQuiz();
};

watch(() => route.params.courseId, (id, oldId) => { if (id && id !== oldId) loadCourse(); });
watch(currentKey, () => loadQuiz());

onMounted(loadCourse);
</script>

<style scoped>
.quiz-question {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 0.25rem;
}
.quiz-results {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
}
.progress-bar {
  background-color: var(--bs-primary);
}

.lesson-content {
  font-size: 1.1rem;
  line-height: 1.8;
}

.lesson-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  display: block;
  overflow-x: auto;
}
.lesson-content :deep(th),
.lesson-content :deep(td) {
  border: 1px solid #cbd5e1;
  padding: 8px 10px;
  vertical-align: top;
}
.lesson-content :deep(th) { background: #f4f7fb; font-weight: 700; text-align: left; }
.lesson-content :deep(td p),
.lesson-content :deep(th p) { margin: 0; }

.lesson-content :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}

.list-group-item.active {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.list-group-item:not(.active):hover {
  background-color: var(--bs-light);
}
</style>
