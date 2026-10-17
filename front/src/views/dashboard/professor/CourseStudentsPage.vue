<template>
  <div class="container-fluid py-4">
    <RouterLink to="/manage-courses" class="small text-decoration-none">
      <i class="bi bi-arrow-left me-1"></i>Mes cours
    </RouterLink>
    <h2 class="mt-2 mb-1">Étudiants{{ course ? ` · ${course.title}` : '' }}</h2>
    <p class="text-muted mb-4">Progression, résultats aux quiz et certificats de chaque inscrit.</p>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="!students.length" class="alert alert-info">Aucun étudiant inscrit à ce cours pour le moment.</div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div v-for="tile in tiles" :key="tile.label" class="col-6 col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-muted small">{{ tile.label }}</div>
              <div class="fs-4 fw-semibold">{{ tile.value }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2 align-items-center mb-3">
        <label for="student-search" class="visually-hidden">Rechercher un étudiant</label>
        <input id="student-search" v-model.trim="search" class="form-control" style="max-width: 280px"
          placeholder="Rechercher un nom ou un email">
        <select id="student-filter" v-model="status" class="form-select" style="max-width: 220px" aria-label="Filtrer par état">
          <option value="all">Tous les étudiants</option>
          <option value="not_started">Pas encore commencé</option>
          <option value="in_progress">En cours</option>
          <option value="completed">Terminé</option>
        </select>
      </div>

      <div class="table-responsive card border-0 shadow-sm">
        <table class="table align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>Étudiant</th>
              <th>Inscrit le</th>
              <th style="min-width: 160px">Progression</th>
              <th v-for="q in quizTitles" :key="q.id">{{ q.title }}</th>
              <th>Dernière activité</th>
              <th>Certificat</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in visible" :key="s.user_id">
              <td>
                <div class="fw-semibold">{{ s.name }}</div>
                <small class="text-muted">{{ s.email }}</small>
              </td>
              <td class="text-nowrap">{{ formatDate(s.enrolled_at) }}</td>
              <td>
                <div class="progress" style="height: 8px" role="progressbar" :aria-valuenow="s.progress_percentage" aria-valuemin="0" aria-valuemax="100">
                  <div class="progress-bar" :class="s.progress_percentage >= 100 ? 'bg-success' : ''" :style="{ width: s.progress_percentage + '%' }"></div>
                </div>
                <small class="text-muted">{{ Math.round(s.progress_percentage) }} % · {{ s.completed_lessons }} leçon(s)</small>
              </td>
              <td v-for="q in s.quizzes" :key="q.test_id" class="text-nowrap">
                <span v-if="!q.attempts" class="text-muted">—</span>
                <span v-else :class="q.passed ? 'text-success' : 'text-danger'">
                  {{ q.best_score }} % <small class="text-muted">({{ q.attempts }} essai{{ q.attempts > 1 ? 's' : '' }})</small>
                </span>
              </td>
              <td class="text-nowrap">{{ formatDate(s.last_activity) }}</td>
              <td>
                <RouterLink v-if="s.certificate_code" :to="`/certificates/verify/${s.certificate_code}`" class="small">
                  <i class="bi bi-patch-check-fill text-success me-1"></i>{{ s.certificate_code }}
                </RouterLink>
                <span v-else class="text-muted small">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="!visible.length" class="text-muted mt-3">Aucun étudiant ne correspond à ces critères.</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { getCourseById, getCourseStudents } from '../../../services/api/course';
import type { Course, CourseStudentRow } from '../../../types/api';

const route = useRoute();
const courseId = Number(route.params.id);

const course = ref<Course | null>(null);
const students = ref<CourseStudentRow[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const search = ref('');
const status = ref<'all' | 'not_started' | 'in_progress' | 'completed'>('all');

const stateOf = (s: CourseStudentRow) =>
  s.completed_at ? 'completed' : s.progress_percentage > 0 ? 'in_progress' : 'not_started';

const visible = computed(() => {
  const q = search.value.toLowerCase();
  return students.value.filter(s =>
    (status.value === 'all' || stateOf(s) === status.value)
    && (!q || s.name.toLowerCase().includes(q) || s.email.toLowerCase().includes(q)));
});

const quizTitles = computed(() =>
  (students.value[0]?.quizzes ?? []).map(q => ({ id: q.test_id, title: q.title })));

const tiles = computed(() => {
  const n = students.value.length;
  const avg = n ? students.value.reduce((t, s) => t + s.progress_percentage, 0) / n : 0;
  return [
    { label: 'Inscrits', value: n },
    { label: 'Progression moyenne', value: `${Math.round(avg)} %` },
    { label: 'Ont terminé', value: students.value.filter(s => s.completed_at).length },
    { label: 'Certificats', value: students.value.filter(s => s.certificate_code).length },
  ];
});

const formatDate = (iso: string) => new Date(iso).toLocaleDateString('fr-FR', { dateStyle: 'medium' });

onMounted(async () => {
  try {
    [course.value, students.value] = await Promise.all([getCourseById(courseId), getCourseStudents(courseId)]);
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Impossible de charger les étudiants de ce cours.';
  } finally {
    loading.value = false;
  }
});
</script>
