<template>
  <div class="modal fade" :id="modalId" tabindex="-1" aria-labelledby="testModalLabel" aria-hidden="true" ref="modalElement">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="testModalLabel">
            {{ test.id ? 'Modifier le Test' : 'Créer un Test' }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
          <div v-if="isLoading && !test.id" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Chargement du test...</span>
            </div>
            <p>Chargement du test...</p>
          </div>

          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>

          <div class="row" v-if="(!(isLoading && !test.id))">
            <div class="col-lg-4">
              <div class="card border-0 shadow-sm">
                <div class="card-header bg-white py-3">
                  <h6 class="mb-0">Paramètres du test</h6>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label">Titre du test</label>
                    <input type="text" class="form-control" v-model="test.title" placeholder="Ex: Examen final" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Description</label>
                    <textarea class="form-control" v-model="test.description" rows="3" placeholder="Instructions et description du test"></textarea>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Durée (minutes)</label>
                    <input type="number" class="form-control" v-model.number="test.duration_minutes" min="1" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Score minimum (%)</label>
                    <input type="number" class="form-control" v-model.number="test.passing_score" min="0" max="100" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Nombre de tentatives maximum</label>
                    <input type="number" class="form-control" v-model.number="test.max_attempts" min="1" required>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-lg-8">
              <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-white py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Questions</h6>
                    <div class="dropdown">
                      <button class="btn btn-outline-primary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" :disabled="isLoading">
                        <i class="bi bi-plus-circle me-2"></i>Ajouter une question
                      </button>
                      <ul class="dropdown-menu">
                        <li><button class="dropdown-item" @click="addQuestion('multiple_choice')"><i class="bi bi-list-check me-2"></i>Choix multiple</button></li>
                        <li><button class="dropdown-item" @click="addQuestion('true-false')"><i class="bi bi-check2-circle me-2"></i>Vrai/Faux</button></li>
                        <li><button class="dropdown-item" @click="addQuestion('essay')"><i class="bi bi-text-paragraph me-2"></i>Question ouverte</button></li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div class="card-body">
                  <div v-if="test.questions?.length === 0" class="text-center text-muted py-3">
                    Aucune question ajoutée pour le moment.
                  </div>
                  
                  <div v-for="(question, index) in test.questions" :key="question.id || `new-${index}`" class="mb-4 p-3 border rounded">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                      <h6 class="mb-0">Question {{ index + 1 }} ({{ getQuestionTypeLabel(question.question_type) }})</h6>
                      <button class="btn btn-outline-danger btn-sm" @click="removeQuestion(index, question?.id)" :disabled="isLoading">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                    
                    <div class="mb-3">
                      <label class="form-label">Texte de la question</label>
                      <textarea class="form-control" v-model="question.question_text" rows="2" placeholder="Saisissez votre question" required></textarea>
                    </div>

                    <!-- Multiple Choice Options -->
                    <div v-if="question.question_type === 'multiple_choice'" class="mb-3">
                      <label class="form-label d-block mb-2">Options de réponse :</label>
                      <div v-for="(option, optIndex) in question.options" :key="optIndex" class="d-flex align-items-center mb-2">
                        <input 
                          type="text" 
                          class="form-control me-2" 
                          v-model="option.text" 
                          :placeholder="'Option ' + (optIndex + 1)"
                          required
                        >
                        <div class="form-check me-2">
                          <input 
                            class="form-check-input" 
                            type="checkbox" 
                            v-model="option.is_correct" 
                            :id="`q_${index}_opt_${optIndex}_correct`"
                          >
                          <label class="form-check-label" :for="`q_${index}_opt_${optIndex}_correct`">
                            Correcte
                          </label>
                        </div>
                        <button 
                          class="btn btn-outline-danger btn-sm" 
                          @click="removeOptionFromQuestion(index, optIndex)" 
                          :disabled="isLoading || (question.options && question.options.length <= 2)"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                      <button class="btn btn-sm btn-outline-secondary mt-2" @click="addOptionToQuestion(index)" :disabled="isLoading">
                        Ajouter une option
                      </button>
                    </div>

                    <!-- True/False Options -->
                    <div v-if="question.question_type === 'true-false'" class="mb-3">
                      <label class="form-label d-block mb-2">Réponse correcte :</label>
                      <div class="form-check mb-2">
                        <input 
                          class="form-check-input" 
                          type="radio" 
                          :name="`true_false_${index}`" 
                          :id="`q_${index}_true`"
                          :value="true"
                          v-model="question.correct_answer"
                        >
                        <label class="form-check-label" :for="`q_${index}_true`">
                          Vrai
                        </label>
                      </div>
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="radio" 
                          :name="`true_false_${index}`" 
                          :id="`q_${index}_false`"
                          :value="false"
                          v-model="question.correct_answer"
                        >
                        <label class="form-check-label" :for="`q_${index}_false`">
                          Faux
                        </label>
                      </div>
                    </div>

                    <!-- Essay Question Info -->
                    <div v-if="question.question_type === 'essay'" class="mb-3">
                      <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Cette question sera évaluée manuellement par l'enseignant.
                      </div>
                    </div>

                    <div class="row g-3">
                      <div class="col-md-6">
                        <label class="form-label">Points</label>
                        <input type="number" class="form-control" v-model.number="question.points" min="1" required>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" :disabled="isLoading">
            Annuler
          </button>
          <button type="button" class="btn btn-primary" @click="saveTest" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-save me-2"></i>
            {{ isLoading ? 'Enregistrement...' : (test.id ? 'Mettre à jour' : 'Enregistrer') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue';
import {
  getCourseTestBySectionId,
  createCourseTest,
  updateCourseTest,
  createTestQuestion,
  updateTestQuestion,
  deleteTestQuestion
} from '../services/api/course';
import type {
  CourseTest,
  TestQuestion,
  CourseTestCreatePayload,
} from '../types/api';
import { QuestionType } from '../types/api';

// Props
interface Props {
  sectionId: number | null;
  modalId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modalId: 'testEditorModal'
});

// Reactive state
const isLoading = ref(false);
const error = ref<string | null>(null);
const modalElement = ref<HTMLElement>();

interface FormTestQuestion {
  id?: number;
  question_text: string;
  question_type: 'multiple_choice' | 'true-false' | 'essay';
  options?: Array<{ text: string; is_correct: boolean }>;
  points: number;
  correct_answer?: boolean;
}

const test = ref<{
  id?: number;
  title: string;
  description: string;
  duration_minutes: number;
  passing_score: number;
  max_attempts: number;
  questions: FormTestQuestion[];
}>({
  title: 'Nouveau Quiz',
  description: '',
  duration_minutes: 60,
  passing_score: 70,
  max_attempts: 3,
  questions: [],
});

const isFormValid = computed(() => {
  if (!test.value.title.trim()) return false;
  if (test.value.questions.length === 0) return false;
  
  return test.value.questions.every(question => {
    if (!question.question_text.trim()) return false;
    if (question.points < 1) return false;
    
    if (question.question_type === 'multiple_choice') {
      if (!question.options || question.options.length < 2) return false;
      if (!question.options.some(opt => opt.is_correct)) return false;
      if (!question.options.every(opt => opt.text.trim())) return false;
    }
    
    if (question.question_type === 'true-false') {
      if (question.correct_answer === undefined) return false;
    }
    
    return true;
  });
});

const loadTest = async () => {
  if (!props.sectionId) return;
  isLoading.value = true;
  error.value = null;
  
  try {
    const fetchedTest: CourseTest = await getCourseTestBySectionId(props.sectionId);

    if (!fetchedTest || !fetchedTest.id) {
      test.value = {
        title: 'Nouveau Quiz',
        description: '',
        duration_minutes: 60,
        passing_score: 70,
        max_attempts: 3,
        questions: [],
      };
      return;
    }
    
    test.value = {
      id: fetchedTest.id,
      title: fetchedTest.title,
      description: fetchedTest.description ?? '',
      duration_minutes: fetchedTest.duration_minutes || 60,
      passing_score: fetchedTest.passing_score || 70,
      max_attempts: fetchedTest.max_attempts || 3,
      questions: (fetchedTest.questions || []).map((q: TestQuestion) => {
        const formQuestion: FormTestQuestion = {
          id: q.id,
          question_text: q.question_text,
          question_type: q.question_type === QuestionType.MULTIPLE_CHOICE ? 'multiple_choice' : 'essay',
          points: q.points || 1,
        };
        
        if (formQuestion.question_type === 'multiple_choice') {
          formQuestion.options = q.options && q.options.length > 0
            ? q.options.map(opt => ({ text: opt.text, is_correct: opt.is_correct }))
            : [{ text: '', is_correct: false }, { text: '', is_correct: false }];
        } else if (formQuestion.question_type === 'true-false') {
          const trueOption = q.options?.find(opt => opt.text.toLowerCase() === 'vrai' || opt.text.toLowerCase() === 'true');
          formQuestion.correct_answer = trueOption?.is_correct || false;
        }
        
        return formQuestion;
      }),
    };
  } catch (err: any) {
    console.error('Error loading test:', err);
    error.value = err?.message || 'Failed to load test data.';
  } finally {
    isLoading.value = false;
  }
};

// Watch pour surveiller les changements de sectionId
watch(() => props.sectionId, (newSectionId) => {
  console.log('sectionId changed to:', newSectionId);
  loadTest();
}, { immediate: true });

const getQuestionTypeLabel = (type: string) => {
  const labels = {
    'multiple_choice': 'Choix multiple',
    'true-false': 'Vrai/Faux',
    'essay': 'Question ouverte'
  };
  return labels[type as keyof typeof labels] || type;
};

const addQuestion = (type: 'multiple_choice' | 'true-false' | 'essay') => {
  const newQuestion: FormTestQuestion = {
    question_text: '',
    question_type: type,
    points: 1,
  };
  
  if (type === 'multiple_choice') {
    newQuestion.options = [
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ];
  } else if (type === 'true-false') {
    newQuestion.correct_answer = true;
  }
  
  test.value.questions.push(newQuestion);
};

const removeQuestion = (index: number, questionId: number | null = null) => {
  if (questionId) {
    // Confirmation de suppression
    const confirmed = confirm('Êtes-vous sûr de vouloir supprimer cette question ?');
    if (!confirmed) {
      return;
    }

    // Suppression
    test.value.questions.splice(index, 1);
    deleteTestQuestion(questionId as number);
  }else{
    test.value.questions.splice(index, 1);
  }
};

const addOptionToQuestion = (questionIndex: number) => {
  const question = test.value.questions[questionIndex];
  if (question.question_type === 'multiple_choice') {
    if (!question.options) {
      question.options = [];
    }
    question.options.push({ text: '', is_correct: false });
  }
};

const removeOptionFromQuestion = (questionIndex: number, optionIndex: number) => {
  const question = test.value.questions[questionIndex];
  if (question.options && question.options.length > 2) {
    question.options.splice(optionIndex, 1);
  }
};

const prepareQuestionForAPI = (question: FormTestQuestion) => {
  const baseQuestion = {
    question_text: question.question_text,
    points: question.points,
  };
  
  if (question.question_type === 'true-false') {
    return {
      ...baseQuestion,
      question_type: QuestionType.MULTIPLE_CHOICE,
      options: [
        { text: 'Vrai', is_correct: question.correct_answer === true },
        { text: 'Faux', is_correct: question.correct_answer === false }
      ]
    };
  } else if (question.question_type === 'multiple_choice') {
    return {
      ...baseQuestion,
      question_type: QuestionType.MULTIPLE_CHOICE,
      options: question.options || []
    };
  } else {
    return {
      ...baseQuestion,
      question_type: QuestionType.ESSAY,
      options: []
    };
  }
};

const saveTest = async () => {
  if (!props.sectionId) {
    error.value = 'Section ID manquant';
    return;
  }

  if (!isFormValid.value) {
    error.value = 'Veuillez remplir tous les champs requis.';
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    let savedTest: CourseTest;

    if (test.value.id) {
      const testPayload: any = {
        title: test.value.title,
        description: test.value.description as string | undefined,
        duration_minutes: test.value.duration_minutes,
        passing_score: test.value.passing_score,
        max_attempts: test.value.max_attempts,
      };

      savedTest = await updateCourseTest(test.value.id, testPayload);

      for (const [index, q] of test.value.questions.entries()) {
        const questionPayload = prepareQuestionForAPI(q);

        if (q.id) {
          await updateTestQuestion(q.id, questionPayload as any);
        } else {
          const newQ = await createTestQuestion(test.value.id!, {
            ...questionPayload,
            test_id: test.value.id!,
          } as any);
          test.value.questions[index].id = newQ.id;
        }
      }

    } else {
      const testPayload: CourseTestCreatePayload = {
        title: test.value.title,
        description: test.value.description || undefined,
        duration_minutes: test.value.duration_minutes,
        passing_score: test.value.passing_score,
        max_attempts: test.value.max_attempts,
        section_id: props.sectionId,
        questions: [], 
      };

      savedTest = await createCourseTest(props.sectionId, testPayload);
      test.value.id = savedTest.id;

      // Crée les questions
      for (const [index, q] of test.value.questions.entries()) {
        const questionPayload = prepareQuestionForAPI(q);
        const newQ = await createTestQuestion(savedTest.id!, {
          ...questionPayload,
          test_id: savedTest.id!,
        } as any);
        test.value.questions[index].id = newQ.id;
      }
    }

    (window as any).$('#testEditorModal').modal('toggle');

  } catch (err: any) {
    console.error('Error saving test:', err);
    error.value = err.message || "Erreur lors de l'enregistrement du test.";
  } finally {
    isLoading.value = false;
  }
};

// Initialize modal when component is mounted
onMounted(async () => {
  console.log('Component mounted with sectionId:', props.sectionId);
  
  // Initialize Bootstrap modal
  await nextTick();
});
</script>

<style scoped>
.modal-xl {
  max-width: 1200px;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.alert {
  border-radius: 0.375rem;
}
</style>