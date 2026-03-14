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
  CourseLessonCreatePayload,
  LessonType,
  ContentType,
} from '../../../types/api';
import { CourseStatus } from '../../../types/api';

const route = useRoute();
const router = useRouter();

const isLoading = ref(false);
const error = ref<string | null>(null);
const showPreview = ref(true); // Add preview toggle state
const course_data = ref<Course | null>(null);
const courseSectionId = ref<number | null>(null);
const showTestModal = ref(false);

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
  sections: Array<{ 
    id?: number;
    title: string;
    order: number;
    content_type: ContentType;
    video_url: string | null;
    text_content: string | null;
    test: any | null;
    lessons: Array<{
      id?: number; 
      title: string;
      type: LessonType;
      duration: string;
      content: string; 
      order: number;
      is_completed: boolean; 
    }>;
  }>;
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
      content_type: 'text' as ContentType,
      video_url: null,
      text_content: '', 
      test: null,
      lessons: [
        {
          title: '',
          type: 'video' as LessonType,
          duration: '',
          content: '', 
          order: 0,
          is_completed: false,
        },
      ],
    },
  ],
});

const errors = ref<Record<string, string>>({});

// Computed property for total lessons count
const totalLessons = computed(() => {
  return courseForm.value.sections.reduce((total, section) => {
    return total + section.lessons?.length;
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
        sections: fetchedCourse.sections?.map(s => ({
          id: s.id,
          title: s.title,
          order: s.order,
          content_type: s.content_type || ('text' as ContentType),
          video_url: s.video_url || null,
          text_content: s.text_content || null,
          test: s.test || null, 
          lessons: s.lessons?.map(l => ({
            id: l.id,
            title: l.title,
            type: l.type as LessonType,
            duration: l.duration || '',
            content: l.content_body || '',
            order: l.order,
            is_completed: l.is_completed,
          })),
        })),
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
    content_type: 'text' as ContentType,
    video_url: null,
    text_content: '',
    test: null,
    lessons: [],
  });
};

const removeSection = (index: number, sectionId = null) => {
  if (sectionId) {
    // Confirmation dialog
    const confirm = window.confirm('Are you sure you want to delete this section?');
    if (!confirm) return;
    deleteCourseSection(sectionId);
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
    type: 'video' as LessonType,
    duration: '',
    content: '',
    order: courseForm.value.sections[sectionIndex].lessons?.length,
    is_completed: false,
  });
};

const removeLesson = (sectionIndex: number, lessonIndex: number, lessonId = null) => {
  if (lessonId) {
    const confirm = window.confirm('Are you sure you want to delete this lesson?');
    if (!confirm) return;
    deleteCourseLesson(lessonId);
    courseForm.value.sections[sectionIndex].lessons.splice(lessonIndex, 1);
    courseForm.value.sections[sectionIndex].lessons.forEach((lesson, i) => {
      lesson.order = i;
    });
  }else{
    courseForm.value.sections[sectionIndex].lessons.splice(lessonIndex, 1);
    courseForm.value.sections[sectionIndex].lessons.forEach((lesson, i) => {
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
    window.$('#testEditorModal').modal('toggle');
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

  if (!courseForm.value.title) errors.value.title = 'Le titre est requis.';
  if (!courseForm.value.category) errors.value.category = 'La catégorie est requise.';
  if (!courseForm.value.is_free && (!courseForm.value.price || courseForm.value.price <= 0)) {
    errors.value.price = 'Le prix doit être supérieur à 0 pour un cours payant.';
  }

  if (Object.keys(errors.value).length > 0) {
    isLoading.value = false;
    return;
  }

  try {
    const payload = {
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
          const lessonPayload: CourseLessonCreatePayload = {
            title: lesson.title,
            type: lesson.type,
            duration: lesson.duration,
            content_body: lesson.content,
            order: lessonIndex,
            section_id: sectionId,
            is_completed: lesson.is_completed ?? false,
          };

          if (lesson.id) {
            await updateCourseLesson(lesson.id, lessonPayload);
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
          if (!lesson.title.trim()) continue;

          const lessonPayload: CourseLessonCreatePayload = {
            title: lesson.title,
            type: lesson.type,
            duration: lesson.duration,
            content_body: lesson.content,
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

// Preview course
const previewCourse = () => {
  togglePreview();
};
</script>

<template>
  <div class="container py-5">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">{{ route.params.id ? 'Modifier le cours' : 'Créer un cours' }}</h1>
            <p class="text-muted mb-0">{{ route.params.id ? 'Modifiez les détails de votre cours' : 'Créez un nouveau cours' }}</p>
          </div>
          <div class="d-flex gap-2">
            <button 
              class="btn" 
              :class="showPreview ? 'btn-secondary' : 'btn-outline-primary'"
              @click="togglePreview" 
              :disabled="isLoading"
            >
              <i class="bi bi-eye me-2"></i>
              {{ showPreview ? 'Masquer l\'aperçu' : 'Afficher l\'aperçu' }}
            </button>
            <button class="btn btn-primary" @click="saveCourse" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              <i v-else class="bi bi-check-circle me-2"></i>
              {{ isLoading ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State for existing course -->
    <div v-if="isLoading && route.params.id && !courseForm.id" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement du cours...</span>
      </div>
      <p>Chargement du cours...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <!-- Main Content -->
    <div class="row" v-if="!error && (!(isLoading && route.params.id && !courseForm.id))">
      <!-- Form Section -->
      <div :class="showPreview ? 'col-lg-8' : 'col-12'">
        <!-- Basic Information -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Informations de base</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Titre du cours <span class="text-danger">*</span></label>
              <input 
                type="text" 
                class="form-control"
                :class="{ 'is-invalid': errors.title }"
                v-model="courseForm.title"
                placeholder="Ex: Développement Web Avancé"
              >
              <div v-if="errors.title" class="invalid-feedback">{{ errors.title }}</div>
            </div>

            <div class="mb-3">
              <label class="form-label">Description courte</label>
              <textarea
                class="form-control"
                v-model="courseForm.short_description"
                rows="2"
                placeholder="Une brève description pour la carte du cours"
              ></textarea>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Catégorie <span class="text-danger">*</span></label>
                <select 
                  class="form-select"
                  :class="{ 'is-invalid': errors.category }"
                  v-model="courseForm.category"
                >
                  <option value="" disabled>Sélectionner une catégorie</option>
                  <option v-for="category in categories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
                <div v-if="errors.category" class="invalid-feedback">{{ errors.category }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">Niveau</label>
                <select class="form-select" v-model="courseForm.level">
                  <option value="beginner">Débutant</option>
                  <option value="intermediate">Intermédiaire</option>
                  <option value="advanced">Avancé</option>
                </select>
              </div>

              <div class="col-md-6">
                <div class="form-check mt-4">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="courseForm.is_free"
                    id="isFreeCheckbox"
                    @change="courseForm.price = courseForm.is_free ? null : courseForm.price"
                  >
                  <label class="form-check-label" for="isFreeCheckbox">
                    Cours gratuit
                  </label>
                </div>
              </div>

              <div class="col-md-6" v-if="!courseForm.is_free">
                <label class="form-label">Prix (XOF) <span class="text-danger">*</span></label>
                <input
                  type="number"
                  class="form-control"
                  :class="{ 'is-invalid': errors.price }"
                  v-model.number="courseForm.price"
                  min="0"
                  step="0.01"
                >
                <div v-if="errors.price" class="invalid-feedback">{{ errors.price }}</div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">URL de l'image du cours</label>
              <input 
                type="url" 
                class="form-control" 
                v-model="courseForm.image_url"
                placeholder="https://example.com/image.jpg"
              >
            </div>

            <div class="mb-3">
              <label class="form-label">Statut du cours</label>
              <select class="form-select" v-model="courseForm.status">
                <option :value="CourseStatus.DRAFT">Brouillon</option>
                <option :value="CourseStatus.PUBLISHED">Publié</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea 
                class="form-control" 
                v-model="courseForm.description"
                rows="4"
                placeholder="Décrivez votre cours en détail"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Objectives -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Objectifs d'apprentissage</h5>
          </div>
          <div class="card-body">
            <div v-for="(objective, index) in courseForm.objectives" :key="index" class="mb-3">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="courseForm.objectives[index]"
                  placeholder="Ex: Maîtriser les concepts de base"
                >
                <button 
                  class="btn btn-outline-danger" 
                  type="button"
                  @click="removeObjective(index)"
                  :disabled="courseForm.objectives?.length === 1"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
            <button class="btn btn-outline-primary" @click="addObjective">
              <i class="bi bi-plus-circle me-2"></i>Ajouter un objectif
            </button>
          </div>
        </div>

        <!-- Prerequisites -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Prérequis</h5>
          </div>
          <div class="card-body">
            <div v-for="(prerequisite, index) in courseForm.prerequisites" :key="index" class="mb-3">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="courseForm.prerequisites[index]"
                  placeholder="Ex: Connaissances en HTML/CSS"
                >
                <button 
                  class="btn btn-outline-danger" 
                  type="button"
                  @click="removePrerequisite(index)"
                  :disabled="courseForm.prerequisites?.length === 1"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
            <button class="btn btn-outline-primary" @click="addPrerequisite">
              <i class="bi bi-plus-circle me-2"></i>Ajouter un prérequis
            </button>
          </div>
        </div>

        <!-- Course Content -->
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Contenu du cours</h5>
          </div>
          <div class="card-body">
            <div v-for="(section, sectionIndex) in courseForm.sections" :key="sectionIndex" class="mb-4">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">Section {{ sectionIndex + 1 }}</h6>
                <div class="d-flex align-items-center">
                  <button v-if="section?.id"
                    class="btn btn-primary btn-sm me-2"
                    @click="openCreateTestModal(section?.id)"
                  >
                    <i class="bi bi-book"></i>
                    Quiz / Exercice
                  </button>
                  <button 
                    class="btn btn-outline-danger btn-sm"
                    @click="removeSection(sectionIndex, section?.id)"
                    :disabled="courseForm.sections?.length === 1"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>

              <div class="card bg-light border">
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label">Titre de la section</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="section.title"
                      placeholder="Ex: Introduction aux concepts de base"
                    >
                  </div>

                  <!-- Section Content Type Selector -->
                  <div class="mb-3">
                    <label class="form-label">Type de contenu de la section</label>
                    <select 
                      class="form-select" 
                      v-model="section.content_type"
                      @change="onSectionTypeChange(sectionIndex)"
                    >
                      <option value="text">Contenu Texte</option>
                      <option value="video">Contenu Vidéo</option>
                      <option value="quiz">Quiz/Test</option>
                    </select>
                  </div>

                  <!-- Content Fields Based on Type -->
                  <div v-if="section.content_type === 'text'" class="mb-3">
                    <label class="form-label">Contenu Texte</label>
                    <textarea
                      class="form-control"
                      v-model="section.text_content"
                      rows="6"
                      placeholder="Saisissez le contenu texte de cette section. Vous pouvez utiliser du HTML basique pour la mise en forme."
                    ></textarea>
                    <div class="form-text">
                      <i class="bi bi-info-circle me-1"></i>
                      Vous pouvez utiliser des balises HTML basiques comme &lt;p&gt;, &lt;strong&gt;, &lt;em&gt;, &lt;ul&gt;, &lt;ol&gt;, etc.
                    </div>
                  </div>

                  <div v-else-if="section.content_type === 'video'" class="mb-3">
                    <label class="form-label">URL de la Vidéo</label>
                    <input
                      type="url"
                      class="form-control"
                      v-model="section.video_url"
                      placeholder="https://www.youtube.com/watch?v=... ou https://vimeo.com/..."
                    >
                    <div class="form-text">
                      <i class="bi bi-info-circle me-1"></i>
                      Formats supportés: YouTube, Vimeo, liens directs vers fichiers vidéo (.mp4, .webm, .ogg)
                    </div>
                  </div>

                  <div v-else-if="section.content_type === 'quiz'" class="mb-3">
                    <div class="border rounded p-3 bg-white">
                      <div class="d-flex align-items-center justify-content-between mb-3">
                        <h6 class="mb-0">Configuration du Quiz</h6>
                        <button class="btn btn-outline-primary btn-sm">
                          <i class="bi bi-pencil-square me-1"></i>Éditeur Avancé
                        </button>
                      </div>
                      <div class="row g-3">
                        <div class="col-md-6">
                          <label class="form-label-sm">Nombre de questions</label>
                          <input 
                            type="number" 
                            class="form-control form-control-sm" 
                            min="1" 
                            placeholder="Ex: 5"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label-sm">Durée limite (minutes)</label>
                          <input 
                            type="number" 
                            class="form-control form-control-sm" 
                            min="1" 
                            placeholder="Ex: 15"
                          >
                        </div>
                        <div class="col-12">
                          <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="randomQuestions">
                            <label class="form-check-label" for="randomQuestions">
                              Ordre aléatoire des questions
                            </label>
                          </div>
                        </div>
                      </div>
                      <div class="alert alert-info mt-3 mb-0">
                        <i class="bi bi-lightbulb me-2"></i>
                        <small>La création détaillée des questions se fait dans l'éditeur avancé.</small>
                      </div>
                    </div>
                  </div>

                  <!-- Lessons Section (Optional supplementary content) -->
                  <div class="mt-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <h6 class="mb-0">Leçons complémentaires (optionnel)</h6>
                      <small class="text-muted">{{ section.lessons?.length }} leçon(s)</small>
                    </div>
                    
                    <div v-if="section.lessons?.length === 0" class="text-center py-3 text-muted">
                      <i class="bi bi-plus-circle-dotted fs-1"></i>
                      <p class="mt-2 mb-0">Aucune leçon complémentaire</p>
                      <button 
                        class="btn btn-outline-primary btn-sm mt-2"
                        @click="addLesson(sectionIndex)"
                      >
                        Ajouter la première leçon
                      </button>
                    </div>

                    <div v-else>
                      <div v-for="(lesson, lessonIndex) in section.lessons" :key="lessonIndex" class="mb-3">
                        <div class="card border">
                          <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                              <small class="text-muted fw-bold">Leçon {{ lessonIndex + 1 }}</small>
                              <button 
                                class="btn btn-outline-danger btn-sm"
                                @click="removeLesson(sectionIndex, lessonIndex, lesson?.id)"
                              >
                                <i class="bi bi-trash"></i>
                              </button>
                            </div>
                            
                            <div class="row g-2">
                              <div class="col-md-6">
                                <input 
                                  type="text" 
                                  class="form-control form-control-sm" 
                                  v-model="lesson.title"
                                  placeholder="Titre de la leçon"
                                >
                              </div>
                              <div class="col-md-3">
                                <select class="form-select form-select-sm" v-model="lesson.type">
                                  <option value="video">Vidéo</option>
                                  <option value="text">Texte</option>
                                </select>
                              </div>
                              <div class="col-md-3">
                                <input 
                                  type="text" 
                                  class="form-control form-control-sm"
                                  v-model="lesson.duration"
                                  placeholder="Ex: 10min"
                                >
                              </div>
                              <div class="col-12">
                                <textarea 
                                  class="form-control form-control-sm"
                                  v-model="lesson.content"
                                  rows="2"
                                  :placeholder="lesson.type === 'video' ? 'URL de la vidéo' : 'Contenu texte de la leçon'"
                                ></textarea>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <button 
                        class="btn btn-outline-primary btn-sm"
                        @click="addLesson(sectionIndex)"
                      >
                        <i class="bi bi-plus-circle me-1"></i>Ajouter une leçon
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button class="btn btn-outline-primary" @click="addSection">
              <i class="bi bi-plus-circle me-2"></i>Ajouter une section
            </button>
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div v-if="showPreview" class="col-lg-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 2rem;">
          <div class="card-header bg-white py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Aperçu du cours</h5>
              <span class="badge bg-secondary">{{ totalLessons }} leçon(s)</span>
            </div>
          </div>
          <div class="card-body">
            <!-- Course Image Preview -->
            <div class="mb-3">
              <div v-if="courseForm.image_url" class="position-relative">
                <img 
                  :src="courseForm.image_url" 
                  class="img-fluid rounded"
                  style="width: 100%; height: 200px; object-fit: cover;"
                  @error="$event.target.style.display='none'"
                  alt="Aperçu du cours"
                >
              </div>
              <div v-else class="bg-light rounded d-flex align-items-center justify-content-center" style="height: 200px;">
                <div class="text-center text-muted">
                  <i class="bi bi-image fs-1"></i>
                  <p class="mt-2 mb-0">Aucune image</p>
                </div>
              </div>
            </div>

            <!-- Course Title -->
            <h4 class="fw-bold mb-2">
              {{ courseForm.title || 'Titre du cours' }}
            </h4>

            <!-- Course Meta -->
            <div class="d-flex align-items-center gap-2 mb-3">
              <span class="badge bg-primary">{{ courseForm.category || 'Catégorie' }}</span>
              <span class="badge bg-secondary">{{ courseForm.level === 'beginner' ? 'Débutant' : courseForm.level === 'intermediate' ? 'Intermédiaire' : 'Avancé' }}</span>
              <span v-if="courseForm.is_free" class="badge bg-success">Gratuit</span>
              <span v-else-if="courseForm.price" class="badge bg-info">{{ courseForm.price }}XOF</span>
            </div>

            <!-- Short Description -->
            <p v-if="courseForm.short_description" class="text-muted mb-3">
              {{ courseForm.short_description }}
            </p>

            <!-- Objectives Preview -->
            <div v-if="courseForm.objectives.some(obj => obj.trim())" class="mb-3">
              <h6 class="fw-bold mb-2">Ce que vous apprendrez :</h6>
              <ul class="list-unstyled">
                <li v-for="(objective, index) in courseForm.objectives.filter(obj => obj.trim())" :key="index" class="mb-1">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <small>{{ objective }}</small>
                </li>
              </ul>
            </div>

            <!-- Prerequisites Preview -->
            <div v-if="courseForm.prerequisites.some(req => req.trim())" class="mb-3">
              <h6 class="fw-bold mb-2">Prérequis :</h6>
              <ul class="list-unstyled">
                <li v-for="(prerequisite, index) in courseForm.prerequisites.filter(req => req.trim())" :key="index" class="mb-1">
                  <i class="bi bi-info-circle text-info me-2"></i>
                  <small>{{ prerequisite }}</small>
                </li>
              </ul>
            </div>

            <!-- Course Content Preview -->
            <div class="mb-3">
              <h6 class="fw-bold mb-2">Contenu du cours :</h6>
              <div class="accordion accordion-flush" id="previewAccordion">
                <div v-for="(section, index) in courseForm.sections.filter(s => s.title.trim())" :key="index" class="accordion-item">
                  <h2 class="accordion-header">
                    <button 
                      class="accordion-button collapsed py-2" 
                      type="button" 
                      :data-bs-toggle="`collapse`"
                      :data-bs-target="`#collapse${index}`"
                      :aria-expanded="false"
                    >
                      <div class="d-flex align-items-center w-100">
                        <div class="me-2">
                          <i v-if="section.content_type === 'video'" class="bi bi-play-circle text-primary"></i>
                          <i v-else-if="section.content_type === 'quiz'" class="bi bi-question-circle text-warning"></i>
                          <i v-else class="bi bi-file-text text-secondary"></i>
                        </div>
                        <div class="flex-grow-1">
                          <small class="fw-semibold">{{ section.title }}</small>
                          <br>
                          <small class="text-muted">{{ section.lessons?.length }} leçon(s) complémentaire(s)</small>
                        </div>
                      </div>
                    </button>
                  </h2>
                  <div :id="`collapse${index}`" class="accordion-collapse collapse" :data-bs-parent="`#previewAccordion`">
                    <div class="accordion-body py-2">
                      <div v-if="section.lessons?.length > 0">
                        <div v-for="(lesson, lessonIndex) in section.lessons.filter(l => l.title.trim())" :key="lessonIndex" class="d-flex align-items-center mb-2">
                          <i class="bi bi-play-btn text-muted me-2" style="font-size: 0.8rem;"></i>
                          <small class="flex-grow-1">{{ lesson.title }}</small>
                          <small class="text-muted">{{ lesson.duration }}</small>
                        </div>
                      </div>
                      <div v-else class="text-muted">
                        <small>Contenu principal de la section</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Status Preview -->
            <div class="mb-3">
              <h6 class="fw-bold mb-2">Statut :</h6>
              <span 
                class="badge" 
                :class="courseForm.status === 'published' ? 'bg-success' : 'bg-warning'"
              >
                {{ courseForm.status === 'published' ? 'Publié' : 'Brouillon' }}
              </span>
            </div>

            <!-- Description Preview -->
            <div v-if="courseForm.description">
              <h6 class="fw-bold mb-2">Description :</h6>
              <div class="text-muted" style="max-height: 150px; overflow-y: auto;">
                <small>{{ courseForm.description }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <CourseTestEditor
      v-if="courseSectionId !== null && showTestModal"
      ref="testEditorModal"
      :section-id="courseSectionId"
      modal-id="testEditorModal"
    />
  </div>
</template>

<style scoped>
.accordion-button:not(.collapsed) {
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  border-color: var(--bs-primary);
}

.accordion-button:focus {
  box-shadow: none;
  border-color: var(--bs-primary);
}

.sticky-top {
  z-index: 1020;
}

.form-label-sm {
  font-size: 0.875rem;
  font-weight: 500;
}

@media (max-width: 991.98px) {
  .sticky-top {
    position: relative !important;
    top: auto !important;
  }
}
</style>