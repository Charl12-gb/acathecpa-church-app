<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { categories } from '../../../services/utils';
import CourseTestEditor from '../../../components/CourseTestEditor.vue';
import {
  getCourseById,
  createCourse,
  updateCourse,
  deleteCourseSection,
  createCourseSection,
  createCourseLesson,
  updateCourseSection,
  deleteCourseLesson,
  updateCourseLesson
} from '../../../services/api/course';
import type {
  Course,
  CourseSectionCreatePayload,
} from '../../../types/api';
import { CourseStatus } from '../../../types/api';

const route = useRoute();
const router = useRouter();

const isLoading = ref(false);
const error = ref<string | null>(null);
const showPreview = ref(true);
const course_data = ref<Course | null>(null);
const courseSectionId = ref<number | null>(null);
const showTestModal = ref(false);

// ── Step wizard ──
const currentStep = ref(1);
const totalSteps = 3;
const steps = [
  { num: 1, label: 'Informations', icon: 'bi-info-circle-fill' },
  { num: 2, label: 'Objectifs & Prérequis', icon: 'bi-trophy-fill' },
  { num: 3, label: 'Contenu', icon: 'bi-journal-richtext' },
];

const stepErrors = ref<string | null>(null);

const validateStep = (step: number): boolean => {
  stepErrors.value = null;
  errors.value = {};
  if (step === 1) {
    if (!courseForm.value.title) { errors.value.title = 'Le titre est requis.'; }
    if (!courseForm.value.category) { errors.value.category = 'La catégorie est requise.'; }
    if (!courseForm.value.is_free && (!courseForm.value.price || courseForm.value.price <= 0)) {
      errors.value.price = 'Le prix doit être supérieur à 0 pour un cours payant.';
    }
    if (Object.keys(errors.value).length > 0) {
      stepErrors.value = 'Veuillez corriger les erreurs avant de continuer.';
      return false;
    }
  }
  return true;
};

const nextStep = () => {
  if (validateStep(currentStep.value) && currentStep.value < totalSteps) {
    currentStep.value++;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
    stepErrors.value = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const goToStep = (step: number) => {
  if (step < currentStep.value) {
    currentStep.value = step;
    stepErrors.value = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (step > currentStep.value) {
    // validate all intermediate steps
    for (let s = currentStep.value; s < step; s++) {
      if (!validateStep(s)) return;
    }
    currentStep.value = step;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const courseForm = ref<{
  id?: number; 
  title: string;
  description: string;
  category: string;
  level: string;  
  price: number | null;
  is_free: boolean;
  short_description: string | null;
  image_url?: string | null;
  objectives: string[]; 
  prerequisites: string[]; 
  status: CourseStatus;
  sections: any[];
}>({
  title: '',
  description: '',
  category: '',
  level: 'beginner',
  price: null,
  is_free: false, 
  short_description: null, 
  image_url: null, 
  objectives: [''],
  prerequisites: [''],
  status: CourseStatus.DRAFT,
  sections: [
    {
      title: '',
      order: 0,
      content_type: 'text',
      video_url: null,
      text_content: '', 
      test: null,
      lessons: [
        {
          title: '',
          type: 'video',
          duration: '',
          content: '', 
          order: 0,
          is_completed: false,
        },
      ],
    },
  ] as any[],
});

const errors = ref<Record<string, string>>({});

// Computed property for total lessons count
const totalLessons = computed(() => {
  return courseForm.value.sections.reduce((total: number, section: any) => {
    return total + (section.lessons?.length || 0);
  }, 0);
});

onMounted(async () => {
  const courseIdParam = route.params.id;
  if (courseIdParam) {
    isLoading.value = true;
    error.value = null;
    try {
      const courseId = Number(courseIdParam);
      const fetchedCourse = await getCourseById(courseId);
      course_data.value = fetchedCourse;
      courseForm.value = {
        id: fetchedCourse.id,
        title: fetchedCourse.title,
        description: fetchedCourse.description || '',
        price: fetchedCourse.price ?? null,
        is_free: fetchedCourse.is_free ?? false,
        short_description: fetchedCourse.short_description || null,
        image_url: fetchedCourse.image_url || null,
        objectives: fetchedCourse.objectives && fetchedCourse.objectives?.length > 0 ? fetchedCourse.objectives : [''],
        prerequisites: fetchedCourse.prerequisites && fetchedCourse.prerequisites?.length > 0 ? fetchedCourse.prerequisites : [''],
        status: fetchedCourse.status || CourseStatus.DRAFT,
        category: fetchedCourse.category || '',
        level: fetchedCourse.level || 'beginner',
        sections: (fetchedCourse.sections || []).map((s: any) => ({
          id: s.id,
          title: s.title,
          order: s.order,
          content_type: s.content_type || 'text',
          video_url: s.video_url || null,
          text_content: s.text_content || null,
          test: s.test || null, 
          lessons: (s.lessons || []).map((l: any) => ({
            id: l.id,
            title: l.title,
            type: l.type,
            duration: l.duration || '',
            content: l.content_body || '',
            order: l.order,
            is_completed: l.is_completed,
          })),
        })) as any[],
      };
    } catch (err: any) {
      console.error('Error loading course:', err);
      error.value = err.message || 'Failed to load course data.';
    } finally {
      isLoading.value = false;
    }
  }
});

// Add/remove dynamic fields
const addObjective = () => {
  courseForm.value.objectives.push('')
}

const removeObjective = (index: number) => {
  courseForm.value.objectives.splice(index, 1)
}

const addPrerequisite = () => {
  courseForm.value.prerequisites.push('')
}

const removePrerequisite = (index: number) => {
  courseForm.value.prerequisites.splice(index, 1)
}

const addSection = () => {
  courseForm.value.sections.push({
    title: '',
    order: courseForm.value.sections?.length,
    content_type: 'text',
    video_url: null,
    text_content: '',
    test: null,
    lessons: [],
  });
};

const removeSection = (index: number, sectionId: number | null = null) => {
  if (sectionId) {
    // Confirmation dialog
    const confirmed = window.confirm('Are you sure you want to delete this section?');
    if (!confirmed) return;
    deleteCourseSection(sectionId as number);
    courseForm.value.sections.splice(index, 1);
    // Update order for remaining sections
    courseForm.value.sections.forEach((section, i) => {
      section.order = i;
    });
  }else{
    courseForm.value.sections.splice(index, 1);
    // Update order for remaining sections
    courseForm.value.sections.forEach((section, i) => {
      section.order = i;
    });
  }
};

const addLesson = (sectionIndex: number) => {
  console.log(courseForm.value.sections[sectionIndex])
  courseForm.value.sections[sectionIndex].lessons.push({
    title: '',
    type: 'video',
    duration: '',
    content: '',
    order: courseForm.value.sections[sectionIndex].lessons?.length,
    is_completed: false,
  });
};

const removeLesson = (sectionIndex: number, lessonIndex: number, lessonId: number | null = null) => {
  if (lessonId) {
    const confirmed = window.confirm('Are you sure you want to delete this lesson?');
    if (!confirmed) return;
    deleteCourseLesson(lessonId as number);
    courseForm.value.sections[sectionIndex].lessons.splice(lessonIndex, 1);
    courseForm.value.sections[sectionIndex].lessons.forEach((lesson: any, i: number) => {
      lesson.order = i;
    });
  }else{
    courseForm.value.sections[sectionIndex].lessons.splice(lessonIndex, 1);
    courseForm.value.sections[sectionIndex].lessons.forEach((lesson: any, i: number) => {
      lesson.order = i;
    });
  }
};

const openCreateTestModal = (incomingSectionId: number) => {
  console.log('Opening modal with section ID:', incomingSectionId);
  courseSectionId.value = incomingSectionId;
  showTestModal.value = true;
  
  // Attendre le prochain tick pour s'assurer que le composant reçoit la nouvelle valeur
  nextTick(() => {
      const modal = (window as any).$('#testEditorModal');
      if (modal && modal.modal) {
          modal.modal('toggle');
      }
  });
};

// Clear section content when type changes
const onSectionTypeChange = (sectionIndex: number) => {
  const section = courseForm.value.sections[sectionIndex];
  // Clear content based on previous type
  section.video_url = null;
  section.text_content = null;
  section.test = null;
};

const saveCourse = async () => {
  isLoading.value = true;
  error.value = null;
  errors.value = {};

  if (!validateStep(1)) {
    currentStep.value = 1;
    isLoading.value = false;
    return;
  }

  try {
    const payload: any = {
      title: courseForm.value.title,
      description: courseForm.value.description,
      price: courseForm.value.price,
      is_free: courseForm.value.is_free,
      short_description: courseForm.value.short_description,
      image_url: courseForm.value.image_url,
      objectives: courseForm.value.objectives.filter(o => o.trim() !== ''),
      prerequisites: courseForm.value.prerequisites.filter(p => p.trim() !== ''),
      status: courseForm.value.status,
      category: courseForm.value.category,
      level: courseForm.value.level,
    };

    if (courseForm.value.id) {
      // === MISE À JOUR DU COURS EXISTANT ===
      const courseId = courseForm.value.id;
      await updateCourse(courseId, payload);

      // Créer ou mettre à jour les sections
      for (const [sectionIndex, section] of courseForm.value.sections.entries()) {
        const sectionPayload: CourseSectionCreatePayload = {
          title: section.title,
          order: sectionIndex,
          content_type: section.content_type,
          video_url: section.content_type === 'video' ? section.video_url : undefined,
          text_content: section.content_type === 'text' ? section.text_content : undefined,
          test: section.content_type === 'quiz' ? section.test : undefined,
        };

        let sectionId: number;

        if (section.id) {
          await updateCourseSection(section.id, sectionPayload);
          sectionId = section.id;
        } else {
          const newSection = await createCourseSection(courseId, sectionPayload);
          sectionId = newSection.id;
        }

        // Créer ou mettre à jour les leçons
        for (const [lessonIndex, lesson] of (section.lessons || []).entries()) {
          const lessonPayload: any = {
            title: (lesson as any).title,
            type: (lesson as any).type,
            duration: (lesson as any).duration,
            content_body: (lesson as any).content,
            order: lessonIndex,
            section_id: sectionId,
            is_completed: (lesson as any).is_completed ?? false,
          };

          if ((lesson as any).id) {
            await updateCourseLesson((lesson as any).id, lessonPayload);
          } else {
            await createCourseLesson(sectionId, lessonPayload);
          }
        }
      }

      alert('Cours et ses sections/leçons mis à jour avec succès.');
    } else {
      // === CRÉATION D'UN NOUVEAU COURS ===
      const newCourse = await createCourse(payload);
      const newCourseId = newCourse.id;

      for (const [sectionIndex, section] of courseForm.value.sections.entries()) {
        if (!section.title.trim()) continue;

        const sectionPayload: CourseSectionCreatePayload = {
          title: section.title,
          order: sectionIndex,
          content_type: section.content_type,
          video_url: section.content_type === 'video' ? section.video_url : undefined,
          text_content: section.content_type === 'text' ? section.text_content : undefined,
          test: section.content_type === 'quiz' ? section.test : undefined,
        };

        const newSection = await createCourseSection(newCourseId, sectionPayload);
        const sectionId = newSection.id;

        for (const [lessonIndex, lesson] of (section.lessons || []).entries()) {
          if (!(lesson as any).title.trim()) continue;

          const lessonPayload: any = {
            title: (lesson as any).title,
            type: (lesson as any).type,
            duration: (lesson as any).duration,
            content_body: (lesson as any).content,
            order: lessonIndex,
            section_id: sectionId,
            is_completed: false,
          };
          await createCourseLesson(sectionId, lessonPayload);
        }
      }

      alert('Cours créé avec succès.');
    }

    router.push('/manage-courses');
  } catch (err: any) {
    console.error('Erreur lors de l\'enregistrement du cours:', err);
    error.value = err.response?.data?.detail || err.message;
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors;
    }
  } finally {
    isLoading.value = false;
  }
};

// Toggle preview
const togglePreview = () => {
  showPreview.value = !showPreview.value;
};

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement | null;
  if (target) {
    target.style.display = 'none';
  }
};

const previewSections = computed(() => {
  return (courseForm.value.sections || []).filter((section: any) => section?.title?.trim());
});

const previewLessons = (section: any) => {
  return (section?.lessons || []).filter((lesson: any) => lesson?.title?.trim());
};

// Preview course removed as redundant
</script>

<template>
  <div class="editor-page">
    <!-- ── Toolbar ── -->
    <header class="editor-toolbar">
      <div class="toolbar-left">
        <button class="btn-back" @click="router.push('/manage-courses')" title="Retour">
          <i class="bi bi-arrow-left"></i>
        </button>
        <div class="toolbar-info">
          <h1 class="toolbar-title">{{ route.params.id ? 'Modifier le cours' : 'Créer un cours' }}</h1>
          <!-- Stepper sous le titre -->
          <div class="toolbar-stepper">
            <div v-for="step in steps" :key="step.num" class="stepper-item" :class="{ active: currentStep === step.num, done: currentStep > step.num }" @click="goToStep(step.num)">
              <div class="stepper-circle">
                <i v-if="currentStep > step.num" class="bi bi-check-lg"></i>
                <span v-else>{{ step.num }}</span>
              </div>
              <div class="stepper-label">
                <span class="stepper-label-text">{{ step.label }}</span>
              </div>
              <div v-if="step.num < totalSteps" class="stepper-line"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="toolbar-actions">
        <div class="toolbar-stats">
          <span class="stat-chip"><i class="bi bi-layers"></i> {{ courseForm.sections.length }} section(s)</span>
          <span class="stat-chip"><i class="bi bi-play-circle"></i> {{ totalLessons }} leçon(s)</span>
        </div>
        <button class="btn-preview" :class="{ active: showPreview }" @click="togglePreview" :disabled="isLoading">
          <i class="bi bi-eye"></i>
          <span class="btn-label">{{ showPreview ? 'Masquer aperçu' : 'Aperçu' }}</span>
        </button>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="isLoading && route.params.id && !courseForm.id" class="loading-state">
      <div class="spinner-lg"></div>
      <p>Chargement du cours…</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">
      <i class="bi bi-exclamation-triangle"></i>
      <span>{{ error }}</span>
    </div>

    <!-- ── Main layout ── -->
    <div class="editor-grid" :class="{ 'with-preview': showPreview }" v-if="!error && (!(isLoading && route.params.id && !courseForm.id))">

      <!-- ─ Form column ─ -->
      <div class="form-col">

        <!-- Step error -->
        <div v-if="stepErrors" class="step-error-banner">
          <i class="bi bi-exclamation-circle"></i>
          <span>{{ stepErrors }}</span>
        </div>

        <!-- ═══ ÉTAPE 1 : Informations de base ═══ -->
        <div v-show="currentStep === 1">
        <section class="editor-card">
          <div class="card-head">
            <span class="card-icon"><i class="bi bi-info-circle-fill"></i></span>
            <h2>Informations de base</h2>
          </div>
          <div class="card-inner">
            <div class="field">
              <label>Titre du cours <span class="req">*</span></label>
              <input type="text" :class="{ invalid: errors.title }" v-model="courseForm.title" placeholder="Ex : Développement Web Avancé">
              <span v-if="errors.title" class="field-error">{{ errors.title }}</span>
            </div>

            <div class="field">
              <label>Description courte</label>
              <textarea v-model="courseForm.short_description" rows="2" placeholder="Une brève description pour la carte du cours"></textarea>
            </div>

            <div class="field-row">
              <div class="field">
                <label>Catégorie <span class="req">*</span></label>
                <select :class="{ invalid: errors.category }" v-model="courseForm.category">
                  <option value="" disabled>Sélectionner une catégorie</option>
                  <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
                </select>
                <span v-if="errors.category" class="field-error">{{ errors.category }}</span>
              </div>
              <div class="field">
                <label>Niveau</label>
                <select v-model="courseForm.level">
                  <option value="beginner">Débutant</option>
                  <option value="intermediate">Intermédiaire</option>
                  <option value="advanced">Avancé</option>
                </select>
              </div>
            </div>

            <div class="field-row">
              <div class="field checkbox-field">
                <label class="cb-label">
                  <input type="checkbox" v-model="courseForm.is_free" @change="courseForm.price = courseForm.is_free ? null : courseForm.price">
                  <span class="cb-box"><i class="bi bi-check"></i></span>
                  Cours gratuit
                </label>
              </div>
              <div class="field" v-if="!courseForm.is_free">
                <label>Prix (XOF) <span class="req">*</span></label>
                <input type="number" :class="{ invalid: errors.price }" v-model.number="courseForm.price" min="0" step="0.01">
                <span v-if="errors.price" class="field-error">{{ errors.price }}</span>
              </div>
            </div>

            <div class="field">
              <label>URL de l'image du cours</label>
              <input type="url" v-model="courseForm.image_url" placeholder="https://example.com/image.jpg">
            </div>

            <div class="field-row">
              <div class="field">
                <label>Statut du cours</label>
                <select v-model="courseForm.status">
                  <option :value="CourseStatus.DRAFT">Brouillon</option>
                  <option :value="CourseStatus.PUBLISHED">Publié</option>
                </select>
              </div>
              <div class="field" style="flex:2">
                <!-- spacer -->
              </div>
            </div>

            <div class="field">
              <label>Description détaillée</label>
              <textarea v-model="courseForm.description" rows="4" placeholder="Décrivez votre cours en détail"></textarea>
            </div>
          </div>
        </section>
        </div>

        <!-- ═══ ÉTAPE 2 : Objectifs & Prérequis ═══ -->
        <div v-show="currentStep === 2">
        <section class="editor-card">
          <div class="card-head">
            <span class="card-icon icon-green"><i class="bi bi-trophy-fill"></i></span>
            <h2>Objectifs d'apprentissage</h2>
          </div>
          <div class="card-inner">
            <div v-for="(_objective, index) in courseForm.objectives" :key="index" class="list-field">
              <span class="list-num">{{ index + 1 }}</span>
              <input type="text" v-model="courseForm.objectives[index]" placeholder="Ex : Maîtriser les concepts de base">
              <button class="btn-icon danger" @click="removeObjective(Number(index))" :disabled="courseForm.objectives?.length === 1" title="Supprimer">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <button class="btn-add" @click="addObjective"><i class="bi bi-plus-circle"></i> Ajouter un objectif</button>
          </div>
        </section>

        <!-- Card : Prérequis -->
        <section class="editor-card">
          <div class="card-head">
            <span class="card-icon icon-orange"><i class="bi bi-bookmark-check-fill"></i></span>
            <h2>Prérequis</h2>
          </div>
          <div class="card-inner">
            <div v-for="(_prerequisite, index) in courseForm.prerequisites" :key="index" class="list-field">
              <span class="list-num">{{ index + 1 }}</span>
              <input type="text" v-model="courseForm.prerequisites[index]" placeholder="Ex : Connaissances en HTML/CSS">
              <button class="btn-icon danger" @click="removePrerequisite(Number(index))" :disabled="courseForm.prerequisites?.length === 1" title="Supprimer">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <button class="btn-add" @click="addPrerequisite"><i class="bi bi-plus-circle"></i> Ajouter un prérequis</button>
          </div>
        </section>
        </div>

        <!-- ═══ ÉTAPE 3 : Contenu du cours ═══ -->
        <div v-show="currentStep === 3">
        <section class="editor-card">
          <div class="card-head">
            <span class="card-icon icon-purple"><i class="bi bi-journal-richtext"></i></span>
            <h2>Contenu du cours</h2>
          </div>
          <div class="card-inner">

            <div v-for="(section, sectionIndex) in courseForm.sections" :key="sectionIndex" class="section-block">
              <!-- Section header -->
              <div class="section-head">
                <div class="section-head-left">
                  <span class="section-badge">{{ sectionIndex + 1 }}</span>
                  <span class="section-title-label">Section {{ sectionIndex + 1 }}</span>
                </div>
                <div class="section-head-right">
                  <button v-if="section?.id" class="btn-quiz" @click="openCreateTestModal(section?.id)">
                    <i class="bi bi-patch-question"></i> Quiz
                  </button>
                  <button class="btn-icon danger" @click="removeSection(Number(sectionIndex), section?.id)" :disabled="courseForm.sections?.length === 1" title="Supprimer la section">
                    <i class="bi bi-trash3"></i>
                  </button>
                </div>
              </div>

              <!-- Section body -->
              <div class="section-body">
                <div class="field">
                  <label>Titre de la section</label>
                  <input type="text" v-model="section.title" placeholder="Ex : Introduction aux concepts de base">
                </div>

                <div class="field">
                  <label>Type de contenu</label>
                  <div class="type-selector">
                    <label class="type-option" :class="{ selected: section.content_type === 'text' }">
                      <input type="radio" :name="'stype'+sectionIndex" value="text" v-model="section.content_type" @change="onSectionTypeChange(sectionIndex)">
                      <i class="bi bi-file-earmark-text"></i> Texte
                    </label>
                    <label class="type-option" :class="{ selected: section.content_type === 'video' }">
                      <input type="radio" :name="'stype'+sectionIndex" value="video" v-model="section.content_type" @change="onSectionTypeChange(sectionIndex)">
                      <i class="bi bi-camera-video"></i> Vidéo
                    </label>
                    <label class="type-option" :class="{ selected: section.content_type === 'quiz' }">
                      <input type="radio" :name="'stype'+sectionIndex" value="quiz" v-model="section.content_type" @change="onSectionTypeChange(sectionIndex)">
                      <i class="bi bi-ui-checks"></i> Quiz
                    </label>
                  </div>
                </div>

                <!-- Text content -->
                <div v-if="section.content_type === 'text'" class="field">
                  <label>Contenu Texte</label>
                  <textarea v-model="section.text_content" rows="6" placeholder="Saisissez le contenu texte de cette section…"></textarea>
                  <span class="field-hint"><i class="bi bi-info-circle"></i> HTML basique supporté : &lt;p&gt;, &lt;strong&gt;, &lt;em&gt;, &lt;ul&gt;, &lt;ol&gt;</span>
                </div>

                <!-- Video content -->
                <div v-else-if="section.content_type === 'video'" class="field">
                  <label>URL de la Vidéo</label>
                  <input type="url" v-model="section.video_url" placeholder="https://www.youtube.com/watch?v=…">
                  <span class="field-hint"><i class="bi bi-info-circle"></i> YouTube, Vimeo, liens directs (.mp4, .webm, .ogg)</span>
                </div>

                <!-- Quiz content -->
                <div v-else-if="section.content_type === 'quiz'" class="quiz-config">
                  <div class="quiz-config-head">
                    <h3>Configuration du Quiz</h3>
                    <button class="btn-outline-sm"><i class="bi bi-pencil-square"></i> Éditeur Avancé</button>
                  </div>
                  <div class="field-row">
                    <div class="field">
                      <label>Nombre de questions</label>
                      <input type="number" min="1" placeholder="Ex : 5">
                    </div>
                    <div class="field">
                      <label>Durée limite (min)</label>
                      <input type="number" min="1" placeholder="Ex : 15">
                    </div>
                  </div>
                  <label class="cb-label small">
                    <input type="checkbox" id="randomQuestions">
                    <span class="cb-box"><i class="bi bi-check"></i></span>
                    Ordre aléatoire des questions
                  </label>
                  <div class="quiz-hint">
                    <i class="bi bi-lightbulb"></i> La création détaillée des questions se fait dans l'éditeur avancé.
                  </div>
                </div>

                <!-- Lessons -->
                <div class="lessons-zone">
                  <div class="lessons-head">
                    <span class="lessons-title"><i class="bi bi-collection-play"></i> Leçons complémentaires</span>
                    <span class="lessons-count">{{ section.lessons?.length }} leçon(s)</span>
                  </div>

                  <div v-if="section.lessons?.length === 0" class="lessons-empty">
                    <i class="bi bi-plus-circle-dotted"></i>
                    <p>Aucune leçon complémentaire</p>
                    <button class="btn-add small" @click="addLesson(Number(sectionIndex))">Ajouter la première leçon</button>
                  </div>

                  <div v-else class="lessons-list">
                    <div v-for="(lesson, lessonIndex) in section.lessons" :key="lessonIndex" class="lesson-card">
                      <div class="lesson-card-head">
                        <span class="lesson-num">{{ Number(lessonIndex) + 1 }}</span>
                        <span class="lesson-label">Leçon {{ Number(lessonIndex) + 1 }}</span>
                        <button class="btn-icon danger small" @click="removeLesson(Number(sectionIndex), Number(lessonIndex), lesson?.id)" title="Supprimer">
                          <i class="bi bi-x-lg"></i>
                        </button>
                      </div>
                      <div class="lesson-card-body">
                        <div class="field-row triple">
                          <div class="field" style="flex:3">
                            <input type="text" v-model="lesson.title" placeholder="Titre de la leçon">
                          </div>
                          <div class="field" style="flex:1">
                            <select v-model="lesson.type">
                              <option value="video">Vidéo</option>
                              <option value="text">Texte</option>
                            </select>
                          </div>
                          <div class="field" style="flex:1">
                            <input type="text" v-model="lesson.duration" placeholder="10min">
                          </div>
                        </div>
                        <div class="field">
                          <textarea v-model="lesson.content" rows="2" :placeholder="lesson.type === 'video' ? 'URL de la vidéo' : 'Contenu texte de la leçon'"></textarea>
                        </div>
                      </div>
                    </div>

                    <button class="btn-add small" @click="addLesson(Number(sectionIndex))">
                      <i class="bi bi-plus-circle"></i> Ajouter une leçon
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <button class="btn-add-section" @click="addSection">
              <i class="bi bi-plus-circle"></i> Ajouter une section
            </button>
          </div>
        </section>
        </div>

        <!-- ── Navigation buttons ── -->
        <div class="step-nav">
          <button v-if="currentStep > 1" class="btn-step-prev" @click="prevStep">
            <i class="bi bi-arrow-left"></i> Précédent
          </button>
          <div v-else></div>
          <button v-if="currentStep < totalSteps" class="btn-step-next" @click="nextStep">
            Suivant <i class="bi bi-arrow-right"></i>
          </button>
          <button v-else class="btn-save" @click="saveCourse" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <i v-else class="bi bi-check-circle"></i>
            {{ isLoading ? 'Enregistrement…' : 'Enregistrer le cours' }}
          </button>
        </div>
      </div>

      <!-- ─ Preview column ─ -->
      <aside v-if="showPreview" class="preview-col">
        <div class="preview-panel">
          <div class="preview-head">
            <h2>Aperçu du cours</h2>
            <span class="pill">{{ totalLessons }} leçon(s)</span>
          </div>

          <div class="preview-body">
            <!-- Image -->
            <div class="preview-img-wrap">
              <img v-if="courseForm.image_url" :src="courseForm.image_url" @error="handleImageError" alt="Aperçu">
              <div v-else class="preview-img-empty"><i class="bi bi-image"></i><span>Aucune image</span></div>
            </div>

            <h3 class="preview-title">{{ courseForm.title || 'Titre du cours' }}</h3>

            <div class="preview-tags">
              <span class="tag blue">{{ courseForm.category || 'Catégorie' }}</span>
              <span class="tag">{{ courseForm.level === 'beginner' ? 'Débutant' : courseForm.level === 'intermediate' ? 'Intermédiaire' : 'Avancé' }}</span>
              <span v-if="courseForm.is_free" class="tag green">Gratuit</span>
              <span v-else-if="courseForm.price" class="tag orange">{{ courseForm.price }} XOF</span>
            </div>

            <p v-if="courseForm.short_description" class="preview-desc">{{ courseForm.short_description }}</p>

            <!-- Objectives -->
            <div v-if="courseForm.objectives.some(o => o.trim())" class="preview-block">
              <h4><i class="bi bi-trophy"></i> Ce que vous apprendrez</h4>
              <ul>
                <li v-for="(obj, i) in courseForm.objectives.filter(o => o.trim())" :key="i">
                  <i class="bi bi-check2-circle"></i> {{ obj }}
                </li>
              </ul>
            </div>

            <!-- Prerequisites -->
            <div v-if="courseForm.prerequisites.some(r => r.trim())" class="preview-block">
              <h4><i class="bi bi-bookmark-check"></i> Prérequis</h4>
              <ul>
                <li v-for="(req, i) in courseForm.prerequisites.filter(r => r.trim())" :key="i">
                  <i class="bi bi-dot"></i> {{ req }}
                </li>
              </ul>
            </div>

            <!-- Sections -->
            <div class="preview-block">
              <h4><i class="bi bi-journal-richtext"></i> Contenu</h4>
              <div v-for="(section, index) in previewSections" :key="index" class="pv-section">
                <div class="pv-section-head">
                  <i :class="section.content_type === 'video' ? 'bi bi-play-circle-fill' : section.content_type === 'quiz' ? 'bi bi-patch-question-fill' : 'bi bi-file-earmark-text-fill'"></i>
                  <div>
                    <span class="pv-section-title">{{ section.title }}</span>
                    <span class="pv-section-meta">{{ section.lessons?.length }} leçon(s)</span>
                  </div>
                </div>
                <div v-if="previewLessons(section).length" class="pv-lessons">
                  <div v-for="(lesson, li) in previewLessons(section)" :key="li" class="pv-lesson">
                    <i class="bi bi-play-btn"></i>
                    <span>{{ lesson.title }}</span>
                    <span class="pv-dur">{{ lesson.duration }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Status -->
            <div class="preview-block">
              <h4><i class="bi bi-flag"></i> Statut</h4>
              <span class="tag" :class="courseForm.status === 'published' ? 'green' : 'yellow'">
                {{ courseForm.status === 'published' ? 'Publié' : 'Brouillon' }}
              </span>
            </div>

            <!-- Description -->
            <div v-if="courseForm.description" class="preview-block">
              <h4><i class="bi bi-card-text"></i> Description</h4>
              <p class="preview-full-desc">{{ courseForm.description }}</p>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <CourseTestEditor
      v-if="courseSectionId !== null && showTestModal"
      ref="testEditorModal"
      :section-id="courseSectionId"
      modal-id="testEditorModal"
    />
  </div>
</template>

<style scoped lang="scss">
/* ── Palette ── */
$primary: #2453a7;
$primary-dark: #1a3f8a;
$primary-soft: #eaf2ff;
$dark: #1a2332;
$gray: #6b7280;
$gray-light: #f4f7fb;
$border: #dfe8f6;
$radius: 14px;
$radius-sm: 10px;
$shadow: 0 2px 12px rgba(36,83,167,.07);
$green: #16a34a;
$green-soft: #ecfdf5;
$orange: #ea580c;
$orange-soft: #fff7ed;
$purple: #7c3aed;
$purple-soft: #f3f0ff;
$red: #dc2626;
$red-soft: #fef2f2;
$yellow: #ca8a04;
$yellow-soft: #fefce8;

/* ── Page ── */
.editor-page {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

/* ── Toolbar ── */
.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 16px 24px;
  margin-bottom: 28px;
  box-shadow: $shadow;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.toolbar-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.btn-back {
  width: 40px; height: 40px;
  border-radius: 10px;
  border: 1px solid $border;
  background: $gray-light;
  color: $dark;
  font-size: 1.1rem;
  cursor: pointer;
  display: grid; place-items: center;
  transition: .2s;
  &:hover { background: $primary-soft; color: $primary; border-color: $primary; }
}
.toolbar-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: $dark;
  margin: 0;
  line-height: 1.2;
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.toolbar-stats {
  display: flex;
  gap: 8px;
}
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: $primary-soft;
  color: $primary;
  font-size: .78rem;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  i { font-size: .85rem; }
}
.btn-preview, .btn-save {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 18px;
  border-radius: $radius-sm;
  font-size: .85rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: .2s;
}
.btn-preview {
  background: $gray-light;
  color: $gray;
  border: 1px solid $border;
  &:hover, &.active { background: $primary-soft; color: $primary; border-color: $primary; }
}
.btn-save {
  background: $primary;
  color: #fff;
  &:hover { background: $primary-dark; }
  &:disabled { opacity: .6; cursor: not-allowed; }
}
.btn-label { white-space: nowrap; }
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Loading / Error ── */
.loading-state {
  text-align: center;
  padding: 80px 0;
  color: $gray;
  .spinner-lg {
    width: 40px; height: 40px;
    border: 3px solid $border;
    border-top-color: $primary;
    border-radius: 50%;
    animation: spin .7s linear infinite;
    margin: 0 auto 16px;
  }
}
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: $red-soft;
  color: $red;
  border: 1px solid $red;
  border-radius: $radius-sm;
  padding: 12px 18px;
  margin-bottom: 20px;
  font-size: .9rem;
  font-weight: 500;
}

/* ── Grid ── */
.editor-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
  &.with-preview {
    grid-template-columns: 1fr 380px;
  }
}

/* ── Editor card ── */
.editor-card {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;
  margin-bottom: 24px;
  overflow: hidden;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 24px;
  border-bottom: 1px solid $border;
  background: $gray-light;
  h2 {
    font-size: 1rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}
.card-icon {
  width: 34px; height: 34px;
  border-radius: 9px;
  display: grid; place-items: center;
  font-size: 1rem;
  background: $primary-soft;
  color: $primary;
  &.icon-green { background: $green-soft; color: $green; }
  &.icon-orange { background: $orange-soft; color: $orange; }
  &.icon-purple { background: $purple-soft; color: $purple; }
}
.card-inner {
  padding: 24px;
}

/* ── Fields ── */
.field {
  margin-bottom: 18px;
  &:last-child { margin-bottom: 0; }
  label {
    display: block;
    font-size: .82rem;
    font-weight: 600;
    color: $dark;
    margin-bottom: 6px;
  }
  input[type="text"], input[type="url"], input[type="number"],
  textarea, select {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid $border;
    border-radius: $radius-sm;
    font-size: .88rem;
    color: $dark;
    background: #fff;
    transition: .2s;
    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, .1);
    }
    &.invalid {
      border-color: $red;
      &:focus { box-shadow: 0 0 0 3px rgba($red, .1); }
    }
    &::placeholder { color: #b0b8c9; }
  }
  textarea { resize: vertical; }
  select { cursor: pointer; }
}
.field-row {
  display: flex;
  gap: 16px;
  & > .field { flex: 1; }
  &.triple { gap: 12px; }
}
.field-error {
  display: block;
  font-size: .78rem;
  color: $red;
  margin-top: 4px;
}
.field-hint {
  display: block;
  font-size: .76rem;
  color: $gray;
  margin-top: 6px;
  i { margin-right: 4px; }
}
.req { color: $red; }

/* ── Checkbox ── */
.checkbox-field { display: flex; align-items: flex-end; }
.cb-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: .88rem;
  font-weight: 500;
  color: $dark;
  cursor: pointer;
  input { display: none; }
  &.small { font-size: .82rem; }
}
.cb-box {
  width: 20px; height: 20px;
  border: 2px solid $border;
  border-radius: 5px;
  display: grid; place-items: center;
  font-size: .7rem;
  color: transparent;
  transition: .2s;
}
.cb-label input:checked + .cb-box {
  background: $primary;
  border-color: $primary;
  color: #fff;
}

/* ── List fields (objectives / prerequisites) ── */
.list-field {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid $border;
    border-radius: $radius-sm;
    font-size: .88rem;
    color: $dark;
    transition: .2s;
    &:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 3px rgba($primary,.1); }
    &::placeholder { color: #b0b8c9; }
  }
}
.list-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: $primary-soft;
  color: $primary;
  font-size: .75rem;
  font-weight: 700;
  display: grid; place-items: center;
  flex-shrink: 0;
}

/* ── Icon buttons ── */
.btn-icon {
  width: 34px; height: 34px;
  border-radius: 8px;
  border: 1px solid $border;
  background: #fff;
  color: $gray;
  font-size: .85rem;
  cursor: pointer;
  display: grid; place-items: center;
  transition: .2s;
  flex-shrink: 0;
  &.danger:hover { background: $red-soft; color: $red; border-color: $red; }
  &.small { width: 28px; height: 28px; font-size: .7rem; border-radius: 6px; }
  &:disabled { opacity: .35; cursor: not-allowed; }
}

/* ── Add buttons ── */
.btn-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: $primary-soft;
  color: $primary;
  border: 1px dashed $primary;
  border-radius: $radius-sm;
  font-size: .82rem;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
  &:hover { background: $primary; color: #fff; }
  &.small { padding: 6px 12px; font-size: .78rem; }
}
.btn-add-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: $primary-soft;
  color: $primary;
  border: 2px dashed rgba($primary, .35);
  border-radius: $radius;
  font-size: .9rem;
  font-weight: 700;
  cursor: pointer;
  transition: .2s;
  &:hover { background: $primary; color: #fff; border-color: $primary; }
}

/* ── Section block ── */
.section-block {
  border: 1px solid $border;
  border-radius: $radius;
  margin-bottom: 20px;
  overflow: hidden;
  background: #fff;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: linear-gradient(135deg, $primary-soft, #f0f4ff);
  border-bottom: 1px solid $border;
}
.section-head-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-badge {
  width: 30px; height: 30px;
  border-radius: 8px;
  background: $primary;
  color: #fff;
  font-size: .82rem;
  font-weight: 700;
  display: grid; place-items: center;
}
.section-title-label {
  font-size: .9rem;
  font-weight: 700;
  color: $dark;
}
.section-head-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-quiz {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 8px;
  background: $purple-soft;
  color: $purple;
  border: 1px solid rgba($purple, .3);
  font-size: .78rem;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
  &:hover { background: $purple; color: #fff; }
}
.section-body {
  padding: 20px;
}

/* ── Type selector (radio cards) ── */
.type-selector {
  display: flex;
  gap: 10px;
}
.type-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 14px;
  border: 1px solid $border;
  border-radius: $radius-sm;
  font-size: .82rem;
  font-weight: 600;
  color: $gray;
  cursor: pointer;
  transition: .2s;
  input { display: none; }
  i { font-size: 1rem; }
  &:hover { border-color: $primary; color: $primary; }
  &.selected {
    background: $primary-soft;
    border-color: $primary;
    color: $primary;
  }
}

/* ── Quiz config ── */
.quiz-config {
  background: $gray-light;
  border: 1px solid $border;
  border-radius: $radius-sm;
  padding: 18px;
  margin-bottom: 18px;
}
.quiz-config-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  h3 {
    font-size: .9rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}
.btn-outline-sm {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid $primary;
  border-radius: 7px;
  background: transparent;
  color: $primary;
  font-size: .76rem;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
  &:hover { background: $primary; color: #fff; }
}
.quiz-hint {
  margin-top: 14px;
  padding: 10px 14px;
  background: $primary-soft;
  border-radius: 8px;
  font-size: .78rem;
  color: $primary-dark;
  i { margin-right: 6px; }
}

/* ── Lessons ── */
.lessons-zone {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px dashed $border;
}
.lessons-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.lessons-title {
  font-size: .88rem;
  font-weight: 700;
  color: $dark;
  i { margin-right: 6px; color: $primary; }
}
.lessons-count {
  font-size: .76rem;
  color: $gray;
  background: $gray-light;
  padding: 3px 10px;
  border-radius: 12px;
}
.lessons-empty {
  text-align: center;
  padding: 24px;
  color: $gray;
  i { font-size: 2rem; display: block; margin-bottom: 8px; opacity: .4; }
  p { font-size: .82rem; margin: 0 0 10px; }
}
.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.lesson-card {
  border: 1px solid $border;
  border-radius: $radius-sm;
  overflow: hidden;
  background: #fff;
}
.lesson-card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: $gray-light;
  border-bottom: 1px solid $border;
}
.lesson-num {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: $primary-soft;
  color: $primary;
  font-size: .68rem;
  font-weight: 700;
  display: grid; place-items: center;
}
.lesson-label {
  flex: 1;
  font-size: .8rem;
  font-weight: 600;
  color: $dark;
}
.lesson-card-body {
  padding: 12px 14px;
}

/* ── Preview panel ── */
.preview-col {
  position: relative;
}
.preview-panel {
  position: sticky;
  top: 20px;
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;
  overflow: hidden;
}
.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid $border;
  background: $gray-light;
  h2 {
    font-size: .95rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}
.pill {
  background: $primary-soft;
  color: $primary;
  font-size: .72rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}
.preview-body {
  padding: 20px;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}
.preview-img-wrap {
  border-radius: $radius-sm;
  overflow: hidden;
  margin-bottom: 16px;
  img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    display: block;
  }
}
.preview-img-empty {
  height: 160px;
  background: $gray-light;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #b0b8c9;
  border-radius: $radius-sm;
  i { font-size: 2rem; }
  span { font-size: .8rem; }
}
.preview-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 10px;
}
.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}
.tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  background: $gray-light;
  color: $gray;
  &.blue { background: $primary-soft; color: $primary; }
  &.green { background: $green-soft; color: $green; }
  &.orange { background: $orange-soft; color: $orange; }
  &.yellow { background: $yellow-soft; color: $yellow; }
}
.preview-desc {
  font-size: .82rem;
  color: $gray;
  margin: 0 0 16px;
  line-height: 1.5;
}
.preview-block {
  margin-bottom: 18px;
  h4 {
    font-size: .82rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 10px;
    display: flex;
    align-items: center;
    gap: 6px;
    i { color: $primary; font-size: .9rem; }
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    li {
      font-size: .8rem;
      color: $gray;
      padding: 3px 0;
      display: flex;
      align-items: center;
      gap: 6px;
      i { color: $green; font-size: .85rem; }
    }
  }
}
.preview-full-desc {
  font-size: .8rem;
  color: $gray;
  line-height: 1.55;
  max-height: 140px;
  overflow-y: auto;
  margin: 0;
}

/* Preview sections */
.pv-section {
  border: 1px solid $border;
  border-radius: $radius-sm;
  margin-bottom: 10px;
  overflow: hidden;
}
.pv-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: $gray-light;
  i { color: $primary; font-size: .95rem; }
}
.pv-section-title {
  display: block;
  font-size: .8rem;
  font-weight: 600;
  color: $dark;
}
.pv-section-meta {
  display: block;
  font-size: .7rem;
  color: $gray;
}
.pv-lessons {
  padding: 8px 14px;
}
.pv-lesson {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  font-size: .76rem;
  color: $gray;
  border-bottom: 1px solid $border;
  &:last-child { border-bottom: none; }
  i { font-size: .75rem; color: $primary; }
  span:first-of-type { flex: 1; }
}
.pv-dur {
  font-size: .7rem;
  color: #b0b8c9;
}

/* ── Stepper (under title) ── */
.toolbar-stepper {
  display: flex;
  align-items: center;
  gap: 0;
}
.stepper-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  flex-shrink: 0;
  padding: 2px 6px;
  border-radius: 6px;
  transition: .2s;
  &:hover { background: rgba($primary-soft, .5); }
}
.stepper-circle {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: grid; place-items: center;
  font-size: .68rem;
  font-weight: 700;
  border: 1.5px solid $border;
  background: $gray-light;
  color: $gray;
  transition: .3s;
  span { line-height: 1; }
}
.stepper-label {
  display: flex;
  flex-direction: column;
}
.stepper-label-text {
  font-size: .74rem;
  font-weight: 600;
  color: $gray;
  transition: .3s;
}
.stepper-line {
  flex: 0 0 20px;
  height: 1.5px;
  background: $border;
  margin: 0 4px;
  transition: .3s;
}
.stepper-item.active {
  .stepper-circle {
    background: $primary;
    border-color: $primary;
    color: #fff;
    box-shadow: 0 0 0 2px rgba($primary, .1);
  }
  .stepper-label-text { color: $primary; font-weight: 700; }
}
.stepper-item.done {
  .stepper-circle {
    background: $green;
    border-color: $green;
    color: #fff;
  }
  .stepper-label-text { color: $green; }
  & + .stepper-item .stepper-line,
  .stepper-line {
    background: $green;
  }
}
.stepper-item.done .stepper-line {
  background: $green;
}

/* ── Step navigation ── */
.step-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding: 0 2px;
}
.btn-step-prev, .btn-step-next {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: $radius-sm;
  font-size: .88rem;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
  border: none;
}
.btn-step-prev {
  background: $gray-light;
  color: $gray;
  border: 1px solid $border;
  &:hover { background: $primary-soft; color: $primary; border-color: $primary; }
}
.btn-step-next {
  background: $primary;
  color: #fff;
  &:hover { background: $primary-dark; }
}

/* ── Step error banner ── */
.step-error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: $orange-soft;
  color: $orange;
  border: 1px solid rgba($orange, .3);
  border-radius: $radius-sm;
  padding: 12px 18px;
  margin-bottom: 20px;
  font-size: .85rem;
  font-weight: 500;
  i { font-size: 1.1rem; }
}

/* ── Responsive ── */
@media (max-width: 1100px) {
  .editor-grid.with-preview {
    grid-template-columns: 1fr;
  }
  .preview-panel {
    position: relative;
    top: auto;
  }
}
@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .toolbar-actions {
    flex-wrap: wrap;
    width: 100%;
  }
  .toolbar-stats { order: 2; width: 100%; }
  .field-row { flex-direction: column; gap: 0; }
  .field-row.triple { flex-direction: column; gap: 0; }
  .type-selector { flex-direction: column; }
  .editor-page { padding: 0 12px 32px; }
  .card-inner { padding: 16px; }
  .section-body { padding: 14px; }
  .btn-label { display: none; }
  .toolbar-stepper { display: none; }
  .stepper-line { flex: 0 0 20px; margin: 0 4px; }
  .stepper-label-text { font-size: .72rem; }
  .stepper-circle { width: 28px; height: 28px; font-size: .72rem; }
  .step-nav { gap: 12px; }
  .btn-step-prev, .btn-step-next { padding: 10px 20px; font-size: .82rem; }
}
</style>