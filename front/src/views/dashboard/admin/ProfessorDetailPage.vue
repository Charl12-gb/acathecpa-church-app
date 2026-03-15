<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { getProfessor } from '../../../services/api/professor'
import { fetchAdminProfessors, fetchAdminProfessorCourses } from '../../../services/api/adminDashboardService'
import type { Course } from '../../../types/api/courseTypes'

const route = useRoute()
const isLoading = ref(false)
const error = ref('')
const professor = ref<any>(null)
const insight = ref<any>(null)
const courses = ref<Course[]>([])

const professorId = computed(() => Number(route.params.id))

const socialEntries = computed(() => {
  const links = (professor.value?.professor_profile?.social_links || {}) as Record<string, string | null | undefined>
  return Object.entries(links)
    .filter(([, value]) => !!value)
    .map(([key, value]) => ({ key, value: value as string }))
})

const normalizeUrl = (url: string) => {
  return /^https?:\/\//i.test(url) ? url : `https://${url}`
}

const socialIconMap: Record<string, string> = {
  linkedin: 'bi bi-linkedin',
  twitter: 'bi bi-twitter-x',
  facebook: 'bi bi-facebook',
  instagram: 'bi bi-instagram',
  youtube: 'bi bi-youtube',
  github: 'bi bi-github',
  website: 'bi bi-globe2',
}
const socialIcon = (key: string) => socialIconMap[key.toLowerCase()] || 'bi bi-link-45deg'

const loadProfessorDetails = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const [profData, insights] = await Promise.all([
      getProfessor(professorId.value),
      fetchAdminProfessors(),
    ])

    professor.value = profData
    insight.value = insights.find((p) => p.id === professorId.value) || null
    courses.value = await fetchAdminProfessorCourses(professorId.value)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || 'Erreur lors du chargement du professeur.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadProfessorDetails)
</script>

<template>
  <div class="prof-detail-page">
    <!-- Top navigation bar -->
    <div class="top-bar">
      <RouterLink :to="{ name: 'manage-professors' }" class="back-link">
        <i class="bi bi-arrow-left"></i> Retour à la liste
      </RouterLink>
      <div class="d-flex gap-2">
        <RouterLink :to="{ name: 'professor-form', params: { id: professorId } }" class="btn btn-sm btn-primary px-3">
          <i class="bi bi-pencil-square me-1"></i> Modifier
        </RouterLink>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 mb-0 text-muted">Chargement du profil…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger mx-4 mt-4">{{ error }}</div>

    <!-- Content -->
    <template v-else-if="professor">
      <!-- ===== HERO BANNER ===== -->
      <div class="profile-banner">
        <div class="banner-bg"></div>
        <div class="banner-content">
          <div class="profile-avatar">
            <span>{{ professor.name ? professor.name.charAt(0).toUpperCase() : 'P' }}</span>
          </div>
          <div class="profile-identity">
            <h2 class="profile-name">{{ professor.name || 'N/A' }}</h2>
            <p class="profile-spec">
              {{ insight?.specialization || professor.professor_profile?.specialization || 'Spécialisation non définie' }}
            </p>
            <div class="profile-badges">
              <span :class="['status-pill', professor.is_active ? 'status-active' : 'status-inactive']">
                <i :class="['bi me-1', professor.is_active ? 'bi-check-circle-fill' : 'bi-pause-circle-fill']"></i>
                {{ professor.is_active ? 'Actif' : 'Inactif' }}
              </span>
              <span class="info-pill" v-if="professor.country">
                <i class="bi bi-geo-alt me-1"></i>{{ professor.country }}
              </span>
              <span class="info-pill">
                <i class="bi bi-calendar3 me-1"></i>Inscrit le {{ professor.created_at ? new Date(professor.created_at).toLocaleDateString() : 'N/A' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== METRIC CARDS ===== -->
      <div class="metrics-strip">
        <div class="metric-card">
          <div class="metric-icon" style="background: #eff5ff; color: #2453a7;">
            <i class="bi bi-journal-bookmark-fill"></i>
          </div>
          <div>
            <div class="metric-value">{{ insight?.published_courses_count ?? 0 }}</div>
            <div class="metric-label">Cours publiés</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon" style="background: #f0faf4; color: #18794e;">
            <i class="bi bi-collection-fill"></i>
          </div>
          <div>
            <div class="metric-value">{{ insight?.courses_count ?? 0 }}</div>
            <div class="metric-label">Total cours</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon" style="background: #fff8eb; color: #b45309;">
            <i class="bi bi-people-fill"></i>
          </div>
          <div>
            <div class="metric-value">{{ insight?.active_students_count ?? 0 }}</div>
            <div class="metric-label">Étudiants actifs</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon" style="background: #fdf2f8; color: #be185d;">
            <i class="bi bi-person-check-fill"></i>
          </div>
          <div>
            <div class="metric-value">{{ insight?.students_count ?? 0 }}</div>
            <div class="metric-label">Étudiants inscrits</div>
          </div>
        </div>
      </div>

      <!-- ===== MAIN GRID ===== -->
      <div class="content-grid">
        <!-- LEFT COLUMN -->
        <div class="left-col">
          <!-- Contact card -->
          <div class="detail-card">
            <div class="card-section-title">
              <i class="bi bi-person-lines-fill"></i> Informations de contact
            </div>
            <div class="info-row">
              <div class="info-row-icon"><i class="bi bi-envelope"></i></div>
              <div>
                <div class="info-row-label">Email</div>
                <div class="info-row-value">{{ professor.email }}</div>
              </div>
            </div>
            <div class="info-row">
              <div class="info-row-icon"><i class="bi bi-telephone"></i></div>
              <div>
                <div class="info-row-label">Téléphone</div>
                <div class="info-row-value">{{ professor.phone || 'Non renseigné' }}</div>
              </div>
            </div>
            <div class="info-row">
              <div class="info-row-icon"><i class="bi bi-calendar-heart"></i></div>
              <div>
                <div class="info-row-label">Date de naissance</div>
                <div class="info-row-value">{{ professor.birthdate || 'Non renseignée' }}</div>
              </div>
            </div>
            <div class="info-row" v-if="insight?.latest_course_published_at">
              <div class="info-row-icon"><i class="bi bi-clock-history"></i></div>
              <div>
                <div class="info-row-label">Dernière publication</div>
                <div class="info-row-value">{{ new Date(insight.latest_course_published_at).toLocaleString() }}</div>
              </div>
            </div>
          </div>

          <!-- Bio card -->
          <div class="detail-card" v-if="professor.professor_profile?.bio">
            <div class="card-section-title">
              <i class="bi bi-card-text"></i> Biographie
            </div>
            <p class="bio-text">{{ professor.professor_profile.bio }}</p>
          </div>

          <!-- Skills card -->
          <div class="detail-card" v-if="professor.professor_profile?.skills?.length">
            <div class="card-section-title">
              <i class="bi bi-stars"></i> Compétences
            </div>
            <div class="d-flex flex-wrap gap-2">
              <span v-for="skill in professor.professor_profile.skills" :key="skill" class="skill-tag">
                {{ skill }}
              </span>
            </div>
          </div>

          <!-- Social links card -->
          <div class="detail-card" v-if="socialEntries.length">
            <div class="card-section-title">
              <i class="bi bi-share"></i> Réseaux sociaux
            </div>
            <div class="social-list">
              <a
                v-for="entry in socialEntries"
                :key="entry.key"
                class="social-link"
                :href="normalizeUrl(entry.value)"
                target="_blank"
                rel="noopener noreferrer"
              >
                <i :class="socialIcon(entry.key)"></i>
                <span>{{ entry.key }}</span>
                <i class="bi bi-box-arrow-up-right ms-auto"></i>
              </a>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="right-col">
          <!-- Courses table -->
          <div class="detail-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div class="card-section-title mb-0">
                <i class="bi bi-book"></i> Cours du professeur
              </div>
              <span class="result-pill">{{ courses.length }} cours</span>
            </div>

            <div v-if="courses.length === 0" class="empty-state">
              <i class="bi bi-journal-x"></i>
              <p>Aucun cours créé pour le moment.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-sm align-middle prof-courses-table mb-0">
                <thead>
                  <tr>
                    <th>Titre</th>
                    <th>Catégorie</th>
                    <th>Statut</th>
                    <th>Créé le</th>
                    <th>Maj le</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in courses" :key="course.id">
                    <td>
                      <div class="fw-semibold text-dark">{{ course.title }}</div>
                      <small class="text-muted">{{ course.short_description || course.description || 'Sans description' }}</small>
                    </td>
                    <td><span class="spec-pill-sm">{{ course.category || 'N/A' }}</span></td>
                    <td>
                      <span :class="['status-pill-sm', course.status === 'published' ? 'status-active' : 'status-inactive']">
                        {{ course.status === 'published' ? 'Publié' : 'Brouillon' }}
                      </span>
                    </td>
                    <td class="text-nowrap">{{ new Date(course.created_at).toLocaleDateString() }}</td>
                    <td class="text-nowrap">{{ new Date(course.updated_at).toLocaleDateString() }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Education & Experience -->
          <div class="detail-card" v-if="professor.professor_profile?.education?.length || professor.professor_profile?.experience?.length">
            <div class="card-section-title mb-3">
              <i class="bi bi-mortarboard"></i> Parcours
            </div>
            <div class="row g-4">
              <!-- Education timeline -->
              <div :class="professor.professor_profile?.experience?.length ? 'col-md-6' : 'col-12'" v-if="professor.professor_profile?.education?.length">
                <h6 class="timeline-heading"><i class="bi bi-book me-1"></i> Éducation</h6>
                <div class="timeline">
                  <div v-for="(edu, idx) in professor.professor_profile.education" :key="`edu-${idx}`" class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <div class="fw-semibold">{{ edu.degree }}</div>
                      <div class="text-primary-emphasis small">{{ edu.institution }}</div>
                      <div class="text-muted small">{{ edu.field_of_study || 'Domaine non spécifié' }} · {{ edu.start_year || '…' }} – {{ edu.end_year || '…' }}</div>
                      <p v-if="edu.description" class="mb-0 small text-muted mt-1">{{ edu.description }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Experience timeline -->
              <div :class="professor.professor_profile?.education?.length ? 'col-md-6' : 'col-12'" v-if="professor.professor_profile?.experience?.length">
                <h6 class="timeline-heading"><i class="bi bi-briefcase me-1"></i> Expérience</h6>
                <div class="timeline">
                  <div v-for="(exp, idx) in professor.professor_profile.experience" :key="`exp-${idx}`" class="timeline-item">
                    <div class="timeline-dot timeline-dot-alt"></div>
                    <div class="timeline-content">
                      <div class="fw-semibold">{{ exp.role }}</div>
                      <div class="text-primary-emphasis small">{{ exp.company }}</div>
                      <div class="text-muted small">{{ exp.start_date || '…' }} – {{ exp.end_date || '…' }}</div>
                      <p v-if="exp.description" class="mb-0 small text-muted mt-1">{{ exp.description }}</p>
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

<style scoped>
/* ============================
   PAGE LAYOUT
   ============================ */
.prof-detail-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* ============================
   TOP BAR
   ============================ */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: #5b6b84;
  text-decoration: none;
  transition: color 0.15s;
}
.back-link:hover {
  color: #2453a7;
}

/* ============================
   HERO BANNER
   ============================ */
.profile-banner {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.banner-bg {
  height: 160px;
  background: linear-gradient(135deg, #2453a7 0%, #3a7bd5 50%, #5b9be6 100%);
}

.banner-content {
  display: flex;
  align-items: flex-end;
  gap: 1.25rem;
  padding: 0 2rem 1.5rem;
  margin-top: -100px;
  position: relative;
  z-index: 1;
}

.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: #fff;
  border: 4px solid #fff;
  box-shadow: 0 4px 16px rgba(36, 83, 167, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(145deg, #2453a7, #3a7bd5);
}
.profile-avatar span {
  font-size: 2.2rem;
  font-weight: 700;
  color: #fff;
}

.profile-identity {
  padding-bottom: 0.25rem;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.15rem;
  text-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

.profile-spec {
  color: rgba(255,255,255,0.85);
  font-size: 0.92rem;
  margin-bottom: 0.6rem;
}

.profile-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}
.status-active {
  color: #fff;
  background: rgba(24, 121, 78, 0.7);
  border: 1px solid rgba(199, 239, 217, 0.4);
}
.status-inactive {
  color: #fff;
  background: rgba(176, 42, 55, 0.7);
  border: 1px solid rgba(248, 198, 205, 0.4);
}

.info-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 500;
  color: #fff;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.3);
  backdrop-filter: blur(4px);
}

/* ============================
   METRICS STRIP
   ============================ */
.metrics-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.15rem;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e7edf5;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s, transform 0.2s;
}
.metric-card:hover {
  box-shadow: 0 4px 14px rgba(36, 83, 167, 0.08);
  transform: translateY(-1px);
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.metric-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1a2332;
  line-height: 1.2;
}

.metric-label {
  font-size: 0.76rem;
  color: #5b6b84;
  font-weight: 500;
}

/* ============================
   CONTENT GRID (2 columns)
   ============================ */
.content-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 1.5rem;
  align-items: start;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.right-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ============================
   CARDS
   ============================ */
.detail-card {
  background: #fff;
  border: 1px solid #e7edf5;
  border-radius: 14px;
  padding: 1.25rem 1.35rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.card-section-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #2c3e55;
  letter-spacing: 0.01em;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.card-section-title i {
  color: #2453a7;
  font-size: 1rem;
}

/* ============================
   INFO ROWS (Contact card)
   ============================ */
.info-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid #f0f3f8;
}
.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-row-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f4f7fc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2453a7;
  font-size: 0.88rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.info-row-label {
  font-size: 0.72rem;
  color: #8895a7;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-weight: 600;
}

.info-row-value {
  font-size: 0.9rem;
  color: #1a2332;
  font-weight: 500;
}

/* ============================
   BIO
   ============================ */
.bio-text {
  color: #43536b;
  font-size: 0.9rem;
  line-height: 1.65;
  margin: 0;
}

/* ============================
   SKILLS
   ============================ */
.skill-tag {
  display: inline-block;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  border: 1px solid #d7e4ff;
  background: #eff5ff;
  color: #2453a7;
  font-size: 0.78rem;
  font-weight: 600;
}

/* ============================
   SOCIAL LINKS
   ============================ */
.social-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.social-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.75rem;
  border-radius: 10px;
  text-decoration: none;
  color: #2c3e55;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
  border: 1px solid transparent;
  transition: all 0.15s;
}
.social-link:hover {
  background: #f4f7fc;
  border-color: #dae4f2;
  color: #2453a7;
}
.social-link i:first-child {
  font-size: 1.05rem;
  color: #2453a7;
  width: 20px;
  text-align: center;
}
.social-link .bi-box-arrow-up-right {
  font-size: 0.7rem;
  color: #a0aec0;
}

/* ============================
   TABLE
   ============================ */
.prof-courses-table thead th {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #5b6b84;
  background: #f8fafc;
  border-bottom: 1px solid #e7edf5;
  font-weight: 700;
  white-space: nowrap;
  padding: 0.6rem 0.75rem;
}

.prof-courses-table tbody td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #f0f3f8;
  font-size: 0.88rem;
}

.prof-courses-table tbody tr:hover {
  background: #f8faff;
}

.spec-pill-sm {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  border: 1px solid #e6ebf3;
  background: #f6f8fc;
  color: #43536b;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-pill-sm {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.result-pill {
  padding: 0.28rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  background: #f6f8fc;
  border: 1px solid #e6ebf3;
  color: #43536b;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #8895a7;
}
.empty-state i {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}
.empty-state p {
  margin: 0;
  font-size: 0.88rem;
}

/* ============================
   TIMELINE
   ============================ */
.timeline-heading {
  font-size: 0.82rem;
  font-weight: 700;
  color: #43536b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #eff5ff;
}

.timeline {
  position: relative;
  padding-left: 1.5rem;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 4px;
  bottom: 4px;
  width: 2px;
  background: #e0e7f1;
  border-radius: 2px;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.15rem;
}
.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -1.5rem;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #2453a7;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #d7e4ff;
  margin-left: -1px;
}

.timeline-dot-alt {
  background: #18794e;
  box-shadow: 0 0 0 2px #c7efd9;
}

.timeline-content {
  padding-top: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .metrics-strip {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 576px) {
  .metrics-strip {
    grid-template-columns: 1fr;
  }
  .banner-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0 1rem 1.25rem;
  }
  .profile-badges {
    justify-content: center;
  }
}
</style>
