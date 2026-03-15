<template>
  <div class="container-fluid py-5">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <template v-else-if="course && currentLesson">
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
                    <div class="progress-bar" role="progressbar" :style="{ width: course.progress + '%' }"
                      :aria-valuenow="course.progress" aria-valuemin="0" aria-valuemax="100"></div>
                  </div>
                  <small class="text-muted">{{ course.progress }}% complété</small>
                </div>

                <div class="btn-group">
                  <button class="btn btn-outline-primary" @click="previousLesson" :disabled="!hasPreviousLesson">
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button class="btn btn-outline-primary" @click="nextLesson" :disabled="!hasNextLesson">
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </div>
              </div>
            </div>
          </nav>
        </div>
      </div>

      <div class="row">
        <!-- Lesson Content -->
        <div class="col-lg-9">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body">
              <h2 class="mb-4">{{ currentSection?.title || currentLesson.title }}</h2>

              <!-- Display Section Content Based on currentSection.content_type -->
              <template v-if="currentSection">
                <!-- Video Content from Section -->
                <div v-if="currentSection.content_type === 'video'">
                  <div class="ratio ratio-16x9 mb-4" v-if="currentSection.video_url">
                    <iframe :src="embedVideoUrl(currentSection.video_url)" width="100%" height="500" allowfullscreen
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
                  </div>
                  <p v-else class="text-muted">Contenu vidéo de la section non disponible.</p>
                </div>

                <!-- Text Content from Section -->
                <div v-else-if="currentSection.content_type === 'text'">
                  <div class="lesson-content" v-if="currentSection.text_content" v-html="currentSection.text_content"></div>
                  <p v-else class="text-muted">Contenu texte de la section non disponible.</p>
                </div>

                <!-- Quiz Content from Section -->
                <div v-else-if="currentSection.content_type === 'quiz' && currentSection.test">
                  <h4>Quiz: {{ currentSection.test.title }}</h4>
                  <p v-if="currentSection.test.description">{{ currentSection.test.description }}</p>

                  <!-- Quiz Area -->
                  <div v-if="isLoadingQuiz" class="text-center py-3">
                    <div class="spinner-border spinner-border-sm" role="status">
                      <span class="visually-hidden">Chargement du quiz...</span>
                    </div>
                  </div>

                  <div v-else-if="currentQuizData">
                    <!-- Start Quiz Button -->
                    <button v-if="!quizInProgress && !quizSubmitted" @click="startQuiz(currentSection.test.id)" class="btn btn-primary mt-3">
                      <i class="bi bi-play-circle me-2"></i>Commencer le Quiz
                    </button>

                    <!-- Quiz Questions -->
                    <div v-if="quizInProgress" class="mt-4">
                      <div v-for="question in currentQuizData.questions" :key="question.id" class="quiz-question mb-4 p-3 border rounded">
                        <p><strong>{{ question.question_text }}</strong> ({{ question.points }} points)</p>

                        <!-- Multiple Choice - Single Answer (Radio) -->
                        <div v-if="question.question_type === QuestionType.MULTIPLE_CHOICE && question.options" class="quiz-options">
                          <div v-for="(option, optIndex) in question.options" :key="optIndex" class="form-check">
                            <input class="form-check-input" type="radio" :name="`question-${question.id}`" :id="`option-${question.id}-${optIndex}`" :value="option.text" v-model="userAnswers[question.id]">
                            <label class="form-check-label" :for="`option-${question.id}-${optIndex}`">{{ option.text }}</label>
                          </div>
                        </div>
                        <!-- Add more v-else-if for other question types like MULTIPLE_CHOICE_MULTIPLE_ANSWERS (checkboxes), TEXT_INPUT, etc. -->
                        <p v-else class="text-muted small">Type de question non supporté pour l'affichage.</p>
                      </div>
                      <button @click="handleQuizSubmit" class="btn btn-success mt-3" :disabled="isSubmittingQuiz">
                        <span v-if="isSubmittingQuiz" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Soumettre le Quiz
                      </button>
                    </div>

                    <!-- Quiz Results -->
                    <div v-if="quizSubmitted && lastQuizAttemptResult" class="mt-4 quiz-results p-3 border rounded">
                      <h5>Résultats de votre tentative</h5>
                      <p>Score: {{ lastQuizAttemptResult.score?.toFixed(2) ?? 'N/A' }}%</p>
                      <p :class="lastQuizAttemptResult.passed ? 'text-success fw-bold' : 'text-danger fw-bold'">
                        Résultat: {{ lastQuizAttemptResult.passed ? 'Réussi' : 'Échoué' }}
                      </p>
                      <button
                        v-if="currentQuizData && (currentQuizData.max_attempts === null || (lastQuizAttemptResult.attempt_number || 1) < (currentQuizData.max_attempts ?? 3))"
                        @click="startQuiz(currentSection.test.id)"
                        class="btn btn-outline-secondary mt-2">
                        Reprendre le Quiz
                      </button>
                      <p v-else-if="currentQuizData && currentQuizData.max_attempts !== null && (lastQuizAttemptResult.attempt_number || 1) >= (currentQuizData.max_attempts ?? 3)" class="text-muted mt-2">
                        Nombre maximum de tentatives atteint.
                      </p>
                    </div>
                  </div>
                  <div v-else-if="!isLoadingQuiz && currentSection.test">
                     <p class="text-warning">Impossible de charger les détails du quiz pour le moment.</p>
                  </div>
                </div>
                <div v-else-if="currentSection.content_type === 'quiz'">
                  <p class="text-muted">Quiz non disponible pour cette section.</p>
                </div>

                <!-- Fallback/Default: Display current lesson details if section type is not specific -->
                <!-- This could be for sections that are just containers for lessons, or if content_type is new/unhandled -->
                <template v-else>
                    <p class="text-muted fst-italic">
                        Cette section contient des leçons individuelles. Le contenu principal de la leçon "{{currentLesson.title}}" est affiché ci-dessous.
                    </p>
                    <hr class="my-4">
                    <h5>Contenu de la leçon: {{ currentLesson.title }}</h5>
                    <div v-if="currentLesson.type === 'video' && currentLesson.video_url" class="ratio ratio-16x9 mb-4">
                         <iframe :src="embedVideoUrl(currentLesson.video_url)" allowfullscreen></iframe>
                    </div>
                    <div v-else-if="currentLesson.type === 'video'">
                        <p class="text-muted">Vidéo de la leçon non disponible.</p>
                    </div>
                    <div v-else-if="currentLesson.type === 'text' && currentLesson.content_body" class="lesson-content" v-html="currentLesson.content_body"></div>
                    <div v-else-if="currentLesson.type === 'text'">
                        <p class="text-muted">Contenu texte de la leçon non disponible.</p>
                    </div>
                    <div v-else-if="currentLesson.type === 'quiz'">
                        <p>Cette leçon est un quiz. Les détails du quiz de la leçon seraient affichés ici.</p>
                        <!-- Placeholder for lesson-specific quiz content if different from section quiz -->
                    </div>
                     <p v-else class="text-muted">Type de contenu de leçon non supporté ou contenu manquant.</p>
                </template>
              </template>
              <template v-else-if="!loading"> <!-- Only show if not loading and currentSection is null -->
                 <p class="text-danger">Impossible de déterminer la section actuelle pour cette leçon.</p>
              </template>


              <!-- Complete Lesson Button (still tied to the individual lesson) -->
              <div class="mt-5 pt-4 border-top text-center">
                <button v-if="!currentLesson.is_completed" class="btn btn-primary btn-lg" @click="completeLesson">
                  Marquer la leçon comme terminée et continuer
                </button>
                <button v-else class="btn btn-success btn-lg" disabled>
                  <i class="bi bi-check-circle me-2"></i>Leçon terminée
                </button>
              </div>
            </div>
          </div>

          <!-- Notes Section (for the individual lesson) -->
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">Mes notes pour cette leçon</h5>
              <textarea class="form-control mb-3" v-model="lessonNotes" rows="4"
                placeholder="Prenez des notes..."></textarea>
              <button class="btn btn-primary" @click="saveNotes">
                Enregistrer les notes
              </button>
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
                <div v-for="section in course.sections" :key="section.id">
                  <div class="list-group-item bg-light">
                    <strong>{{ section.title }}</strong>
                    <small class="text-muted d-block">
                      {{ getCompletedLessonsCount(section) }}/{{ section.lessons.length }} leçons
                    </small>
                  </div>
                  <div v-for="lesson in section.lessons" :key="lesson.id" class="list-group-item"
                    :class="{ active: currentLesson.id === lesson.id }" style="cursor: pointer;"
                    @click="switchLesson(section.id, lesson.id)">
                    <div class="d-flex align-items-center">
                      <i class="bi me-2" :class="[
                        lesson.is_completed ? 'bi-check-circle-fill' : 'bi-circle', // Changed from lesson.completed
                        lesson.type === 'video' ? 'bi-play-circle' :
                          lesson.type === 'quiz' ? 'bi-question-circle' : 'bi-file-text'
                      ]"></i>
                      <div>
                        <div class="small">{{ lesson.title }}</div>
                        <small class="text-muted">{{ lesson.duration }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
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
    markStudentSectionCompleted,
    getMyCourseEnrollmentProgress,
} from '../../../services/api/course';
import type {
    Course, CourseSection, CourseLesson as ApiCourseLesson,
    CourseTest,
    EnrollmentProgress, TestSubmissionWithScoreSchema, TestQuestionAttemptSummaryInputSchema
} from '../../../types/api';
import { QuestionType } from '../../../types/api/courseTypes';

const route = useRoute();
const router = useRouter();

// State
const course = ref<Course | null>(null);
const currentLesson = ref<ApiCourseLesson | null>(null);
const currentSection = computed(() => {
  if (!course.value || !currentLesson.value) return null;
  return course.value.sections.find(section =>
    section.lessons.some(lesson => lesson.id === currentLesson.value!.id)
  );
});
const loading = ref(true);
const error = ref<string | null>(null);
const lessonNotes = ref('');

// Quiz specific state
const currentQuizData = ref<CourseTest | null>(null);
const userAnswers = ref<Record<number, any>>({}); // Stores { questionId: answer }
const quizInProgress = ref(false);
const quizSubmitted = ref(false);
const lastQuizAttemptResult = ref<any>(null); // To store parts of test_attempts from EnrollmentProgress
const isSubmittingQuiz = ref(false);
const isLoadingQuiz = ref(false);

// Store for overall progress potentially
const enrollmentProgressFromApi = ref<EnrollmentProgress | null>(null);

// Load course and lesson data
const loadCourseAndLesson = async () => {
  loading.value = true;
  error.value = null;
  currentLesson.value = null;
  currentQuizData.value = null; // Reset quiz data
  quizInProgress.value = false;
  quizSubmitted.value = false;
  lastQuizAttemptResult.value = null;
  userAnswers.value = {};

  try {
    const courseIdStr = route.params.courseId as string;
    const lessonIdStr = route.params.lessonId as string;

    if (!courseIdStr || !lessonIdStr) {
      error.value = "Course ID ou Lesson ID manquant dans l'URL.";
      loading.value = false;
      return;
    }

    const courseId = parseInt(courseIdStr);
    const lessonId = parseInt(lessonIdStr);

    if (isNaN(courseId) || isNaN(lessonId)) {
      error.value = "Course ID ou Lesson ID invalide.";
      loading.value = false;
      return;
    }

    // Fetch the full course structure
    // If course is already loaded and matches courseId, we might optimize to not refetch it.
    // For simplicity now, always fetch.
    const fetchedCourse = await getCourseById(courseId);
    course.value = fetchedCourse;

    // Find and set current lesson from the fetched course
    if (course.value) {
      findAndSetCurrentLesson(lessonId); // This will also update currentSection
      if (!currentLesson.value) {
        error.value = `Leçon avec ID ${lessonId} non trouvée dans le cours.`;
      } else {
        // Load per-student enrollment progress and update is_completed flags
        try {
          const progress = await getMyCourseEnrollmentProgress(courseId);
          enrollmentProgressFromApi.value = progress;
        } catch (progressErr: any) {
          console.warn('Could not load enrollment progress:', progressErr.message);
        }
        // If current section is a quiz, load its data
        await loadQuizDataIfNeeded();
      }
    } else {
      error.value = "Cours non trouvé.";
    }

  } catch (err: any) {
    console.error('Failed to load course, lesson or quiz:', err);
    error.value = err.message || 'Erreur lors du chargement des données.';
  } finally {
    loading.value = false;
  }
};

// Helper functions
const findAndSetCurrentLesson = (lessonId: number) => { // Renamed from findAndSetCurrentLesson
  if (!course.value) return;

  for (const section of course.value.sections) {
    const lesson = section.lessons.find(l => l.id === lessonId);
    if (lesson) {
      currentLesson.value = lesson;
      // currentSection will update automatically via computed property
      return; // Exit once found
    }
  }

  // Fallback if lessonId not found (e.g., direct navigation to viewer without valid lessonId)
  // Or if course structure is unexpected.
  if (course.value.sections.length > 0 && course.value.sections[0].lessons.length > 0) {
    currentLesson.value = course.value.sections[0].lessons[0];
    // error.value = `Leçon avec ID ${lessonId} non trouvée. Affichage de la première leçon.`;
  } else {
    error.value = "Aucune leçon disponible dans ce cours.";
    currentLesson.value = null;
  }
};

// Added Helper method for embedding video URLs
const embedVideoUrl = (url: string | null): string => {
  if (!url) return '';
  // Basic YouTube embed URL conversion
  if (url.includes('youtube.com/watch?v=')) {
    const videoId = url.split('v=')[1].split('&')[0];
    return `https://www.youtube.com/embed/${videoId}`;
  }
  // Basic Vimeo embed URL conversion
  if (url.includes('vimeo.com/')) {
    const videoId = url.split('/').pop();
    return `https://player.vimeo.com/video/${videoId}`;
  }
  // Return original URL if not YouTube/Vimeo or if it's already an embed link
  return url;
};

// Added Placeholder method for starting a quiz
const startQuiz = (testId: number | undefined) => {
  if (testId === undefined) {
    alert("Quiz ID non disponible.");
    return;
  }
  // Placeholder for navigation or modal
  alert(`Navigation vers le Quiz ID: ${testId}`);
  // Example: router.push(`/quiz-player/${testId}`); // This would be a separate quiz player view
  // For inline quiz:
  if (!currentQuizData.value || currentQuizData.value.id !== testId) {
      console.warn("Quiz data not loaded or mismatch for testId:", testId);
      // Attempt to load it now if section context is right
      if (currentSection.value?.test?.id === testId) {
          loadQuizDataIfNeeded(true); // Force load even if already loading quiz
      } else {
          alert("Impossible de démarrer le quiz : données du quiz non trouvées pour cette section.");
          return;
      }
  }
  quizInProgress.value = true;
  quizSubmitted.value = false;
  userAnswers.value = {}; // Reset answers
  lastQuizAttemptResult.value = null;
};

const loadQuizDataIfNeeded = async (forceLoad: boolean = false) => {
  if (!currentSection.value || currentSection.value.content_type !== 'quiz' || !currentSection.value.test?.id) {
    currentQuizData.value = null; // Clear quiz data if not a quiz section
    return;
  }
  // Avoid reloading if quiz data for the current test is already loaded, unless forced
  if (currentQuizData.value?.id === currentSection.value.test.id && !forceLoad) {
    return;
  }

  isLoadingQuiz.value = true;
  try {
    currentQuizData.value = await fetchFullCourseTest(currentSection.value.test.id);
  } catch (err: any) {
    console.error('Failed to load quiz data:', err);
    error.value = err.message || 'Erreur lors du chargement du quiz.';
    currentQuizData.value = null;
  } finally {
    isLoadingQuiz.value = false;
  }
};


const getCompletedLessonsCount = (section: CourseSection) => {
  // Use enrollmentProgressFromApi if available for most up-to-date info
  if (enrollmentProgressFromApi.value && course.value) {
    const courseProgress = enrollmentProgressFromApi.value;
    // This is tricky because enrollmentProgressFromApi.completed_lessons is flat.
    // We need to check which of this section's lessons are in that flat list.
    let count = 0;
    for (const lesson of section.lessons) {
        if (courseProgress.completed_lessons.includes(lesson.id)) {
            count++;
        }
    }
    return count;
  }
  // Fallback to initial data from course prop
  return section.lessons.filter(lesson => lesson.is_completed).length;
}

const handleQuizSubmit = async () => {
  if (!currentQuizData.value || !course.value) return;
  isSubmittingQuiz.value = true;

  // 1. Client-side scoring (Simplified - A real app might need more robust logic or pure backend scoring)
  let score = 0;
  // let totalPointsPossible = 0; // If calculating points
  const questionsSummary: TestQuestionAttemptSummaryInputSchema[] = [];

  currentQuizData.value.questions.forEach(question => {
    // totalPointsPossible += question.points || 0;
    // const userAnswer = userAnswers.value[question.id];
    // Actual scoring logic is complex and depends on question.correct_answer_data or options.
    // For this example, we'll assume a simple pass/fail or dummy score calculation.
    // Let's assume each question is worth (100 / num_questions) points for simplicity of percentage score.
    // And correctness is hard to determine reliably on client without full answer key processing.

    // This part needs robust logic based on how correct_answer_data is structured for each question_type
    // For MCQs, one would iterate question.options, find the one where opt.is_correct is true, and compare its id with userAnswer.
    // This is a placeholder.
        // let isCorrectThisQuestion = false; // Dummy value
        // if (userAnswer !== undefined) { // Example: give points if answered
        // score += (100 / (currentQuizData.value?.questions.length || 1)); // Simplified score contribution
        // }

    questionsSummary.push({
      question_id: question.id,
    });
  });

  const numQuestions = currentQuizData.value.questions.length || 1;
  const answeredCount = Object.values(userAnswers.value).filter(ans => ans !== undefined && ans !== null && ans !== '').length;
  score = (answeredCount / numQuestions) * 100;
  score = parseFloat(score.toFixed(2));

  const passed = score >= (currentQuizData.value.passing_score || 70); // Default passing score

  const submissionData: TestSubmissionWithScoreSchema = {
    score: score,
    passed: passed,
    questions_summary: questionsSummary,
  };

  try {
    if (!course.value?.id || currentQuizData.value?.id === undefined) {
        throw new Error("Course ID or Test ID is missing for submission.");
    }
    const result = await submitStudentTestAttempt(course.value.id, currentQuizData.value.id, submissionData);
    enrollmentProgressFromApi.value = result;
    if (result.test_attempts && result.test_attempts.length > 0) {
        const attemptsForThisTest = result.test_attempts.filter(a => a.test_id === currentQuizData.value?.id);
        if (attemptsForThisTest.length > 0) {
            lastQuizAttemptResult.value = attemptsForThisTest.sort((a,b) => new Date(b.attempted_at).getTime() - new Date(a.attempted_at).getTime())[0];
            if (lastQuizAttemptResult.value && lastQuizAttemptResult.value.attempt_number === undefined) {
                 lastQuizAttemptResult.value.attempt_number = attemptsForThisTest.length;
            }
        } else {
            lastQuizAttemptResult.value = { score, passed, attempt_number: 1 }; // Fallback if not found in list
        }
    } else {
         lastQuizAttemptResult.value = { score, passed, attempt_number: 1 }; // Fallback if no attempts in response
    }

    quizInProgress.value = false;
    quizSubmitted.value = true;

    // If quiz passed and it's a section-level quiz, mark section as completed
    if (passed && currentSection.value?.id && currentSection.value?.content_type === 'quiz') {
        await handleMarkSectionCompleted(currentSection.value.id);
    }

  } catch (err: any) {
    console.error('Failed to submit test attempt:', err);
    error.value = err.message || 'Erreur lors de la soumission du quiz.';
  } finally {
    isSubmittingQuiz.value = false;
  }
};

// Navigation
const findCurrentLessonIndex = () => {
  if (!course.value || !currentLesson.value) return { sectionIndex: -1, lessonIndex: -1 }

  for (let i = 0; i < course.value.sections.length; i++) {
    const section = course.value.sections[i]
    const lessonIndex = section.lessons.findIndex(l => l.id === currentLesson.value?.id)
    if (lessonIndex !== -1) {
      return { sectionIndex: i, lessonIndex }
    }
  }

  return { sectionIndex: -1, lessonIndex: -1 }
}

const hasPreviousLesson = computed(() => {
  const { sectionIndex, lessonIndex } = findCurrentLessonIndex()
  if (sectionIndex === -1) return false

  return lessonIndex > 0 || sectionIndex > 0
})

const hasNextLesson = computed(() => {
  const { sectionIndex, lessonIndex } = findCurrentLessonIndex()
  if (sectionIndex === -1 || !course.value) return false

  const currentSection = course.value.sections[sectionIndex]
  return lessonIndex < currentSection.lessons.length - 1 ||
    sectionIndex < course.value.sections.length - 1
})

const previousLesson = () => {
  if (!course.value || !hasPreviousLesson.value) return

  const { sectionIndex, lessonIndex } = findCurrentLessonIndex()
  if (lessonIndex > 0) {
    // Previous lesson in same section
    const lesson = course.value.sections[sectionIndex].lessons[lessonIndex - 1]
    router.push(`/lesson/${course.value.id}/${lesson.id}`)
  } else if (sectionIndex > 0) {
    // Last lesson of previous section
    const previousSection = course.value.sections[sectionIndex - 1]
    const lesson = previousSection.lessons[previousSection.lessons.length - 1]
    router.push(`/lesson/${course.value.id}/${lesson.id}`)
  }
}

const nextLesson = () => {
  if (!course.value || !hasNextLesson.value) return

  const { sectionIndex, lessonIndex } = findCurrentLessonIndex()
  const currentSection = course.value.sections[sectionIndex]

  if (lessonIndex < currentSection.lessons.length - 1) {
    // Next lesson in same section
    const lesson = currentSection.lessons[lessonIndex + 1]
    router.push(`/lesson/${course.value.id}/${lesson.id}`)
  } else if (sectionIndex < course.value.sections.length - 1) {
    // First lesson of next section
    const lesson = course.value.sections[sectionIndex + 1].lessons[0]
    router.push(`/lesson/${course.value.id}/${lesson.id}`)
  }
}

const switchLesson = (_sectionId: number, lessonId: number) => {
  router.push(`/lesson/${course.value?.id}/${lessonId}`)
}

// Actions
const completeLesson = async () => {
  if (!course.value || !currentLesson.value || currentLesson.value.is_completed) return;

  try {
    // Use per-student enrollment endpoint instead of global lesson update
    const updatedProgress = await markStudentLessonCompleted(course.value.id, currentLesson.value.id);
    enrollmentProgressFromApi.value = updatedProgress;
    currentLesson.value.is_completed = true;

    // Auto-check if all lessons of current section are completed, then mark section completed
    if (currentSection.value) {
      const allLessonsInSection = currentSection.value.lessons;
      const allCompleted = allLessonsInSection.every(l => 
        updatedProgress.completed_lessons.includes(l.id)
      );
      if (allCompleted) {
        await handleMarkSectionCompleted(currentSection.value.id);
      }
    }

    if (hasNextLesson.value) {
      nextLesson();
    }
  } catch (err: any) {
    console.error('Failed to complete lesson:', err);
    error.value = err.message || 'Failed to complete lesson';
  }
};

const handleMarkSectionCompleted = async (sectionId: number) => {
    if (!course.value) return;
    try {
        const updatedProgress = await markStudentSectionCompleted(course.value.id, sectionId);
        enrollmentProgressFromApi.value = updatedProgress;
    } catch (err: any) {
        console.error('Failed to complete section:', err);
    }
};

const saveNotes = () => {
  // TODO: Implement notes saving
  console.log('Saving notes:', lessonNotes.value)
  // Show success message or notification here
}

// Watch for route changes to update current lesson
watch(
  () => route.params.lessonId,
  async (newLessonIdStr) => { // Make watcher async for await inside
    if (newLessonIdStr && course.value) {
      const newLessonId = parseInt(newLessonIdStr as string);
      if (!isNaN(newLessonId)) {
        findAndSetCurrentLesson(newLessonId); // This sets currentLesson.value
        // currentSection will update via computed. Then the watch on currentSection will trigger.
      }
    } else if (newLessonIdStr) {
        await loadCourseAndLesson(); // Reload all if course context might have changed
    }
  }
);

watch( // Watch for courseId changes too
    () => route.params.courseId,
    async (newCourseIdStr) => { // Make watcher async
        if (newCourseIdStr) {
            await loadCourseAndLesson();
        }
    }
);

// Watch currentSection to load quiz data when section changes
watch(currentSection, async (newSection, oldSection) => {
    // Only proceed if newSection is defined and is a quiz section
    if (newSection?.content_type === 'quiz' && newSection.test?.id) {
        // If the section itself hasn't changed, but maybe its content reloaded, or force reload
        if (newSection.id === oldSection?.id && currentQuizData.value?.id === newSection.test.id) {
            // Quiz for this section already loaded or being loaded, do nothing unless forced
        } else {
            await loadQuizDataIfNeeded();
        }
    } else if (newSection) { // If it's not a quiz section, clear quiz data
        currentQuizData.value = null;
        quizInProgress.value = false;
        quizSubmitted.value = false;
        lastQuizAttemptResult.value = null;
    }
    // If newSection is null (e.g. course unloaded), do nothing, other watchers handle course loading
});


// Watch enrollmentProgressFromApi to update reactive course data
watch(enrollmentProgressFromApi, (newProgress) => {
    if (newProgress && course.value) {
        // Update overall course progress percentage
        if (course.value.progress !== newProgress.progress_percentage) {
             course.value.progress = newProgress.progress_percentage;
        }

        // Update is_completed status for all lessons in the course structure
        for (const section of course.value.sections) {
            for (const lesson of section.lessons) {
                const isNowCompleted = newProgress.completed_lessons.includes(lesson.id);
                if (lesson.is_completed !== isNowCompleted) {
                    lesson.is_completed = isNowCompleted;
                }
            }
        }
        // If currentLesson is affected, ensure its own reactive copy is updated
        if (currentLesson.value && newProgress.completed_lessons.includes(currentLesson.value.id) && !currentLesson.value.is_completed) {
            currentLesson.value.is_completed = true;
        } else if (currentLesson.value && !newProgress.completed_lessons.includes(currentLesson.value.id) && currentLesson.value.is_completed) {
            currentLesson.value.is_completed = false;
        }

        // TODO: Consider how to update section completion status if you have such a visual indicator
        // For example, based on newProgress.completed_sections
    }
}, { deep: true });


// Load course and lesson on mount
onMounted(async () => { // Make onMounted async
  await loadCourseAndLesson();
});
</script>

<style scoped>
/* Add styles for quiz questions if needed */
.quiz-question {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 0.25rem;
}
.quiz-options label {
  margin-right: 1rem;
}
.quiz-results {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  margin-top: 1rem;
}
.progress-bar {
  background-color: var(--bs-primary);
}

.lesson-content {
  font-size: 1.1rem;
  line-height: 1.8;
}

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