<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useProfessorStore } from '../../../stores/professor';
import { storeToRefs } from 'pinia';
import { specializations } from '../../../services/utils';
import { UserRole } from '../../../types/api/userTypes';
import {
  Professor,
  ProfessorProfile,
  EducationEntry,
  ExperienceEntry,
} from '../../../types/api/professorTypes';

const route = useRoute();
const router = useRouter();
const professorStore = useProfessorStore();

const {
  currentProfessor,
  isLoadingItem,
  errorItem
} = storeToRefs(professorStore);

const {
  fetchProfessor,
  updateProfile,
  actionCreateProfessorUserAndProfile,
  clearCurrentProfessor,
} = professorStore;

const professorData = ref<Partial<Professor> & { password?: string }>({
  id: undefined,
  name: '',
  email: '',
  password: '', 
  phone: '',
  is_active: true,
  role: UserRole.PROFESSOR,
  professor_profile: null 
});

const defaultProfessorProfileData: ProfessorProfile = {
  id: 0, 
  user_id: 0,
  specialization: '',
  bio: '',
  education: [],
  experience: [],
  skills: [],
  social_links: { linkedin: '', twitter: '', github: '', website: '', orcid: '', google_scholar: '' }
};

const localProfessorId = ref<number | null>(null);
const isEditMode = computed(() => !!localProfessorId.value);

const saving = ref(false);
const localErrors = ref<Record<string, string>>({});
const showEditForm = ref(true); 

watch(currentProfessor, (newVal) => {
  if (newVal && isEditMode.value) { 
    professorData.value = {
      ...JSON.parse(JSON.stringify(newVal)),
      password: '', 
    };
    if (!professorData.value.professor_profile) {
      professorData.value.professor_profile = {
        ...defaultProfessorProfileData,
        user_id: newVal.id || 0 
      };
    }
  } else if (!isEditMode.value) {
    professorData.value = {
      id: undefined, name: '', email: '', password: '', phone: '',
      is_active: true, role: UserRole.PROFESSOR,
      professor_profile: { ...defaultProfessorProfileData, user_id: 0 }
    };
  }
}, { deep: true, immediate: true });


onMounted(() => {
  const idFromRoute = route.params.id;
  clearCurrentProfessor(); 

  if (idFromRoute) {
    localProfessorId.value = Number(idFromRoute);
    fetchProfessor(localProfessorId.value);
    showEditForm.value = false;
  } else { // Creation mode
    localProfessorId.value = null;
    professorData.value = { 
      id: undefined, name: '', email: '', password: '', phone: '',
      is_active: true, role: UserRole.PROFESSOR,
      professor_profile: { ...defaultProfessorProfileData, user_id: 0 }
    };
    showEditForm.value = true;
  }
});

const toggleEditForm = () => {
  if (isEditMode.value) { 
    showEditForm.value = !showEditForm.value;
  }
};

const defaultNewEducationEntry: EducationEntry = { institution: '', degree: '', field_of_study: '', start_year: null, end_year: null, description: '' };
const defaultNewExperienceEntry: ExperienceEntry = { company: '', role: '', start_date: '', end_date: '', description: '' };
const addEducation = () => { if (professorData.value.professor_profile) { if (!professorData.value.professor_profile.education) { (professorData.value.professor_profile as any).education = []; } (professorData.value.professor_profile as any).education.push({ ...defaultNewEducationEntry }); } };
const removeEducation = (index: number) => { (professorData.value.professor_profile as any)?.education?.splice(index, 1); };
const addExperience = () => { if (professorData.value.professor_profile) { if (!professorData.value.professor_profile.experience) { (professorData.value.professor_profile as any).experience = []; } (professorData.value.professor_profile as any).experience.push({ ...defaultNewExperienceEntry }); } };
const removeExperience = (index: number) => { (professorData.value.professor_profile as any)?.experience?.splice(index, 1); };
const addSkill = () => { if (professorData.value.professor_profile) { if (!professorData.value.professor_profile.skills) { (professorData.value.professor_profile as any).skills = []; } (professorData.value.professor_profile as any).skills.push(''); } };
const removeSkill = (index: number) => { (professorData.value.professor_profile as any)?.skills?.splice(index, 1); };

const saveProfessor = async () => {
  saving.value = true;
  localErrors.value = {};
  if (professorStore.errorItem) professorStore.errorItem = null;

  if (!professorData.value.email) localErrors.value.email = 'Email requis.';
  if (!isEditMode.value && !professorData.value.password) {
    localErrors.value.password = 'Mot de passe requis pour le nouveau professeur.';
  }
  if (!professorData.value.professor_profile?.specialization) {
    localErrors.value.specialization = 'Spécialisation requise.';
  }

  if (Object.keys(localErrors.value).length > 0) {
    saving.value = false;
    return;
  }

  try {
    if (isEditMode.value && localProfessorId.value) {
      if (!professorData.value.professor_profile) {
        localErrors.value.general = "Données de profil manquantes pour la mise à jour.";
        saving.value = false;
        return;
      }
      const profileUpdatePayload: any = {
        specialization: professorData.value.professor_profile.specialization,
        bio: professorData.value.professor_profile.bio,
        education: professorData.value.professor_profile.education?.filter(e => e.institution?.trim() && e.degree?.trim()),
        experience: professorData.value.professor_profile.experience?.filter(e => e.company?.trim() && e.role?.trim()),
        skills: professorData.value.professor_profile.skills?.filter(s => s && s.trim() !== ''),
        social_links: professorData.value.professor_profile.social_links,
      };
      await updateProfile(localProfessorId.value, profileUpdatePayload);

    } else {
      if (!professorData.value.professor_profile) { 
        localErrors.value.general = "Structure de profil manquante.";
        saving.value = false;
        return;
      }
      const createPayload: any = {
        name: professorData.value.name,
        email: professorData.value.email,
        password: professorData.value.password,
        phone: professorData.value.phone,
        country: professorData.value.country,
        birthdate: professorData.value.birthdate,
        is_active: professorData.value.is_active,

        specialization: professorData.value.professor_profile.specialization,
        bio: professorData.value.professor_profile.bio,
        education: professorData.value.professor_profile.education?.filter(e => e.institution?.trim() && e.degree?.trim()),
        experience: professorData.value.professor_profile.experience?.filter(e => e.company?.trim() && e.role?.trim()),
        skills: professorData.value.professor_profile.skills?.filter(s => s && s.trim() !== ''),
        social_links: professorData.value.professor_profile.social_links,
      };
      await actionCreateProfessorUserAndProfile(createPayload);
    }
    router.push({ name: 'manage-professors' }); // Navigate after successful save

  } catch (error: any) {
    console.error('Error saving professor from component:', error);
    if (error.response && error.response.data && error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
             localErrors.value.general = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) { // FastAPI validation errors
            error.response.data.detail.forEach((err: any) => {
                if (err.loc && err.loc.length > 1) {
                    localErrors.value[err.loc[1]] = err.msg;
                } else {
                    localErrors.value.general = err.msg;
                }
            });
        } else {
             localErrors.value.general = "Une erreur est survenue lors de l'enregistrement.";
        }
    } else if (error.message) {
        localErrors.value.general = error.message;
    } else {
        localErrors.value.general = "Une erreur inconnue est survenue.";
    }
    // Keep errorItem from store in sync if it's set by the store action
    if (professorStore.errorItem && !localErrors.value.general) {
        localErrors.value.general = typeof professorStore.errorItem === 'string' ? professorStore.errorItem : JSON.stringify(professorStore.errorItem);
    }
  } finally {
    saving.value = false;
  }
};

const getError = (field: string): string | undefined => localErrors.value[field];
const clearError = (field: string) => { if (localErrors.value[field]) { localErrors.value[field] = ''; }};

const pageTitle = computed(() => {
    return isEditMode.value ?
        (showEditForm.value ? 'Modifier le profil du professeur' : 'Aperçu du Profil du Professeur') :
        'Créer un profil de professeur';
});
// ... (pageSubtitle, hasSocialLinks computed properties remain similar)
const pageSubtitle = computed(() => {
    if (isEditMode.value) {
        return showEditForm.value ? 'Modifiez les informations du profil.' : 'Consultez les informations du profil. Cliquez sur "Passer en Mode Édition" pour modifier.';
    }
    return 'Créez un nouvel utilisateur professeur et son profil associé.';
 });
const hasSocialLinks = computed(() => {
  const sl = professorData.value.professor_profile?.social_links;
  return sl && Object.values(sl).some(link => !!link);
});

</script>

<template>
  <div class="container py-5">
    <!-- Header Section (Title, Subtitle, Buttons) -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-1">{{ pageTitle }}</h1>
            <p class="text-muted mb-0">{{ pageSubtitle }}</p>
          </div>
          <div class="d-flex align-items-center">
            <button v-if="isEditMode && !isLoadingItem"
              type="button" class="btn btn-outline-secondary me-2" @click="toggleEditForm">
              <i :class="showEditForm ? 'bi bi-eye-fill' : 'bi bi-pencil-square'"></i>
              {{ showEditForm ? 'Mode Aperçu' : 'Mode Édition' }}
            </button>
            <button class="btn btn-primary" @click="saveProfessor" :disabled="isLoadingItem || saving || (isEditMode && !showEditForm)">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              <i v-else class="bi bi-check-circle me-2"></i>
              {{ saving ? 'Enregistrement...' : (isEditMode ? 'Mettre à jour Profil' : 'Créer Professeur') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isLoadingItem && isEditMode" class="text-center py-5"> <!-- Show loading only for edit mode fetch -->
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>
      <p class="mt-2">Chargement des données du professeur...</p>
    </div>

    <!-- Error Display -->
    <div v-if="localErrors.general && (!isEditMode || showEditForm)" class="alert alert-danger mt-3 small">
        {{ localErrors.general }}
    </div>
    <div v-if="errorItem && (!isEditMode || showEditForm) && !localErrors.general" class="alert alert-danger">
        Erreur Store: {{ typeof errorItem === 'object' ? JSON.stringify(errorItem) : errorItem }}
    </div>

    <!-- Form Area -->
    <div class="row" v-if="(!isEditMode || (isEditMode && currentProfessor)) && professorData.professor_profile">
      <div v-if="showEditForm || !isEditMode" class="col-lg-8">
        <form @submit.prevent="saveProfessor">
          <!-- User Information Card -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3"><h5 class="mb-0">Informations Utilisateur</h5></div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Nom complet</label>
                  <input type="text" class="form-control" v-model="professorData.name"
                         placeholder="Nom du professeur"
                         :class="{'is-invalid': getError('name')}" @input="clearError('name')"
                         :readonly="isEditMode"> <!-- Readonly if editing existing user -->
                  <div v-if="getError('name')" class="invalid-feedback">{{ getError('name') }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email <span v-if="!isEditMode" class="text-danger">*</span></label>
                  <input type="email" class="form-control" v-model="professorData.email"
                         placeholder="Email du professeur"
                         :class="{'is-invalid': getError('email')}" @input="clearError('email')"
                         :readonly="isEditMode"> <!-- Readonly if editing existing user -->
                  <div v-if="getError('email')" class="invalid-feedback">{{ getError('email') }}</div>
                </div>
                <!-- Password Field - Only for new user creation -->
                <div class="col-md-6" v-if="!isEditMode">
                  <label class="form-label">Mot de passe <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="professorData.password"
                         placeholder="Mot de passe"
                         :class="{'is-invalid': getError('password')}" @input="clearError('password')">
                  <div v-if="getError('password')" class="invalid-feedback">{{ getError('password') }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Téléphone</label>
                  <input type="tel" class="form-control" v-model="professorData.phone"
                         placeholder="Téléphone du professeur"
                         :readonly="isEditMode"> <!-- Readonly if editing existing user -->
                </div>
                 <div class="col-md-6" v-if="isEditMode"> <!-- Status only relevant/editable for existing users via user mgmt -->
                    <label class="form-label">Statut</label>
                    <select class="form-select" v-model="professorData.is_active" :disabled="true">
                        <option :value="true">Actif</option>
                        <option :value="false">Inactif</option>
                    </select>
                </div>
              </div>
               <p v-if="isEditMode" class="mt-3 mb-0 small text-muted">
                 Les informations utilisateur (nom, email, téléphone, statut) sont gérées via l'interface d'administration des utilisateurs si des modifications sont nécessaires.
                 Le mot de passe n'est pas affiché ni modifiable ici pour un utilisateur existant.
               </p>
            </div>
          </div>

          <!-- Professor Profile Card (Specialization, Bio) -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3"><h5 class="mb-0">Profil du Professeur</h5></div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-12">
                  <label class="form-label">Spécialisation <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="professorData.professor_profile.specialization"
                          :class="{'is-invalid': getError('specialization')}" @change="clearError('specialization')">
                    <option value="" disabled>Sélectionner une spécialisation</option>
                    <option v-for="spec in specializations" :key="spec" :value="spec">{{ spec }}</option>
                  </select>
                  <div v-if="getError('specialization')" class="invalid-feedback">{{ getError('specialization') }}</div>
                </div>
                <div class="col-12">
                  <label class="form-label">Biographie</label>
                  <textarea class="form-control" v-model="professorData.professor_profile.bio" rows="4"
                            placeholder="Décrivez l'expérience et l'expertise du professeur"></textarea>
                </div>
              </div>
            </div>
          </div>

          <!-- Education Card -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Formation</h5>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="addEducation"><i class="bi bi-plus-circle me-1"></i>Ajouter</button>
            </div>
            <div class="card-body">
              <div v-for="(edu, index) in professorData.professor_profile.education" :key="index" class="mb-3 p-3 border rounded">
                <div class="row g-2">
                  <div class="col-md-6"><label class="form-label-sm">Institution <span class="text-danger">*</span></label><input type="text" class="form-control form-control-sm" v-model="edu.institution" placeholder="Nom de l'institution"></div>
                  <div class="col-md-6"><label class="form-label-sm">Diplôme <span class="text-danger">*</span></label><input type="text" class="form-control form-control-sm" v-model="edu.degree" placeholder="Ex: Master, PhD"></div>
                  <div class="col-md-6"><label class="form-label-sm">Domaine d'études</label><input type="text" class="form-control form-control-sm" v-model="edu.field_of_study" placeholder="Ex: Informatique"></div>
                  <div class="col-md-3"><label class="form-label-sm">Année de début</label><input type="number" class="form-control form-control-sm" v-model.number="edu.start_year" placeholder="YYYY"></div>
                  <div class="col-md-3"><label class="form-label-sm">Année de fin</label><input type="number" class="form-control form-control-sm" v-model.number="edu.end_year" placeholder="YYYY"></div>
                  <div class="col-12"><label class="form-label-sm">Description</label><textarea class="form-control form-control-sm" v-model="edu.description" rows="2" placeholder="Description (optionnel)"></textarea></div>
                </div>
                <button class="btn btn-outline-danger btn-sm mt-2" type="button" @click="removeEducation(index)"><i class="bi bi-trash"></i> Supprimer</button>
              </div>
              <div v-if="!professorData.professor_profile.education || professorData.professor_profile.education.length === 0" class="text-muted text-center py-3">Aucune formation ajoutée.</div>
            </div>
          </div>

          <!-- Experience Card -->
           <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Expérience professionnelle</h5>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="addExperience"><i class="bi bi-plus-circle me-1"></i>Ajouter</button>
            </div>
            <div class="card-body">
              <div v-for="(exp, index) in professorData.professor_profile.experience" :key="index" class="mb-3 p-3 border rounded">
                 <div class="row g-2">
                  <div class="col-md-6"><label class="form-label-sm">Entreprise/Organisation <span class="text-danger">*</span></label><input type="text" class="form-control form-control-sm" v-model="exp.company" placeholder="Nom de l'entreprise"></div>
                  <div class="col-md-6"><label class="form-label-sm">Rôle/Poste <span class="text-danger">*</span></label><input type="text" class="form-control form-control-sm" v-model="exp.role" placeholder="Ex: Développeur Senior"></div>
                  <div class="col-md-6"><label class="form-label-sm">Date de début</label><input type="text" class="form-control form-control-sm" v-model="exp.start_date" placeholder="Ex: MM-AAAA ou Jan 2020"></div>
                  <div class="col-md-6"><label class="form-label-sm">Date de fin</label><input type="text" class="form-control form-control-sm" v-model="exp.end_date" placeholder="Ex: MM-AAAA ou Présent"></div>
                  <div class="col-12"><label class="form-label-sm">Description</label><textarea class="form-control form-control-sm" v-model="exp.description" rows="2" placeholder="Responsabilités, projets (optionnel)"></textarea></div>
                </div>
                <button class="btn btn-outline-danger btn-sm mt-2" type="button" @click="removeExperience(index)"><i class="bi bi-trash"></i> Supprimer</button>
              </div>
               <div v-if="!professorData.professor_profile.experience || professorData.professor_profile.experience.length === 0" class="text-muted text-center py-3">Aucune expérience ajoutée.</div>
            </div>
          </div>

          <!-- Skills Card -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Compétences</h5>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="addSkill"><i class="bi bi-plus-circle me-1"></i>Ajouter</button>
            </div>
            <div class="card-body">
              <div v-for="(_, index) in professorData.professor_profile.skills" :key="index" class="mb-2">
                <div class="input-group input-group-sm">
                  <input type="text" class="form-control form-control-sm" v-model="professorData.professor_profile.skills![index]" placeholder="Ex: JavaScript">
                  <button class="btn btn-outline-danger" type="button" @click="removeSkill(index)"><i class="bi bi-trash"></i></button>
                </div>
              </div>
              <div v-if="!professorData.professor_profile.skills || professorData.professor_profile.skills.length === 0" class="text-muted text-center py-3">Aucune compétence ajoutée.</div>
            </div>
          </div>

          <!-- Social Links Card -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white py-3"><h5 class="mb-0">Réseaux sociaux</h5></div>
            <div class="card-body">
              <div class="row g-3" v-if="professorData.professor_profile.social_links">
                <div class="col-md-6"><label class="form-label">LinkedIn</label><div class="input-group"><span class="input-group-text"><i class="bi bi-linkedin"></i></span><input type="url" class="form-control" v-model="professorData.professor_profile.social_links.linkedin" placeholder="https://linkedin.com/in/username"></div></div>
                <div class="col-md-6"><label class="form-label">Twitter / X</label><div class="input-group"><span class="input-group-text"><i class="bi bi-twitter-x"></i></span><input type="url" class="form-control" v-model="professorData.professor_profile.social_links.twitter" placeholder="https://x.com/username"></div></div>
                <div class="col-md-6"><label class="form-label">GitHub</label><div class="input-group"><span class="input-group-text"><i class="bi bi-github"></i></span><input type="url" class="form-control" v-model="professorData.professor_profile.social_links.github" placeholder="https://github.com/username"></div></div>
                <div class="col-md-6"><label class="form-label">Site web personnel/Labo</label><div class="input-group"><span class="input-group-text"><i class="bi bi-globe"></i></span><input type="url" class="form-control" v-model="professorData.professor_profile.social_links.website" placeholder="https://example.com"></div></div>
                <div class="col-md-6"><label class="form-label">ORCID</label><div class="input-group"><span class="input-group-text"><i class="bi bi-person-badge"></i></span> <input type="url" class="form-control" v-model="professorData.professor_profile.social_links.orcid" placeholder="https://orcid.org/xxxx-xxxx-xxxx-xxxx"></div></div>
                <div class="col-md-6"><label class="form-label">Google Scholar</label><div class="input-group"><span class="input-group-text"><i class="bi bi-mortarboard-fill"></i></span><input type="url" class="form-control" v-model="professorData.professor_profile.social_links.google_scholar" placeholder="Lien vers profil Google Scholar"></div></div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Right Panel: Profile Preview -->
      <div :class="showEditForm || !isEditMode ? 'col-lg-4' : 'col-lg-8 offset-lg-2'">
        <div class="card border-0 shadow-sm sticky-top" style="top: 2rem;">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Aperçu du Profil</h5>
            <i class="bi bi-person-video3 fs-5 text-primary"></i>
          </div>
          <div class="card-body" v-if="professorData.professor_profile">
            <div class="text-center mb-4">
              <div class="avatar-placeholder rounded-circle bg-primary text-white mx-auto mb-3 d-flex align-items-center justify-content-center">
                <span class="fs-1 fw-bold">{{ professorData.name ? professorData.name.charAt(0).toUpperCase() : 'P' }}</span>
              </div>
              <h5 class="mb-1">{{ professorData.name || 'Nom du professeur' }}</h5>
              <p class="text-muted mb-0">{{ professorData.professor_profile.specialization || 'Spécialisation non définie' }}</p>
            </div>
            <hr>
            <div class="mb-3"><small class="text-muted d-block mb-1"><i class="bi bi-envelope-fill me-2"></i>Email</small><span class="text-body-secondary">{{ professorData.email || 'Non défini' }}</span></div>
            <div class="mb-3"><small class="text-muted d-block mb-1"><i class="bi bi-telephone-fill me-2"></i>Téléphone</small><span class="text-body-secondary">{{ professorData.phone || 'Non défini' }}</span></div>
            <div v-if="professorData.professor_profile.bio" class="mb-3"><small class="text-muted d-block mb-1"><i class="bi bi-file-person-fill me-2"></i>Biographie</small><p class="text-body-secondary small" style="white-space: pre-wrap;">{{ professorData.professor_profile.bio }}</p></div>
            <div class="mb-3" v-if="professorData.professor_profile.skills && professorData.professor_profile.skills.filter(s => s && s.trim() !== '').length > 0">
              <small class="text-muted d-block mb-1"><i class="bi bi-tools me-2"></i>Compétences Clés</small>
              <div class="d-flex flex-wrap gap-1 mt-1">
                  <span v-for="skill in professorData.professor_profile.skills.filter(s => s && s.trim() !== '').slice(0, 7)" :key="skill" class="badge bg-secondary bg-opacity-25 text-dark-emphasis">{{ skill }}</span>
                  <span v-if="professorData.professor_profile.skills.filter(s => s && s.trim() !== '').length > 7" class="badge bg-light text-muted">+{{ professorData.professor_profile.skills.filter(s => s && s.trim() !== '').length - 7 }}</span>
              </div>
            </div>
            <div class="mb-3" v-if="professorData.professor_profile.education && professorData.professor_profile.education.length > 0">
                <small class="text-muted d-block mb-1"><i class="bi bi-mortarboard-fill me-2"></i>Formation</small>
                <ul class="list-unstyled mt-1 small">
                    <li v-for="(edu, index) in professorData.professor_profile.education.slice(0, 3)" :key="'edu-preview-' + index" class="mb-2 p-2 border-start border-2"><strong >{{ edu.degree }}</strong> <span v-if="edu.field_of_study">en {{ edu.field_of_study }}</span><br><span class="text-body-secondary">{{ edu.institution }}</span><br><small v-if="edu.start_year || edu.end_year" class="text-muted">{{ edu.start_year }}{{ edu.end_year && edu.start_year ? ' - ' : '' }}{{ edu.end_year }}</small></li>
                    <li v-if="professorData.professor_profile.education.length > 3" class="text-muted mt-1"><small>+{{ professorData.professor_profile.education.length - 3 }} autre(s)</small></li>
                </ul>
            </div>
            <div class="mb-3" v-if="professorData.professor_profile.experience && professorData.professor_profile.experience.length > 0">
                <small class="text-muted d-block mb-1"><i class="bi bi-briefcase-fill me-2"></i>Expérience Professionnelle</small>
                <ul class="list-unstyled mt-1 small">
                    <li v-for="(exp, index) in professorData.professor_profile.experience.slice(0, 3)" :key="'exp-preview-' + index" class="mb-2 p-2 border-start border-2"><strong>{{ exp.role }}</strong><br><span class="text-body-secondary">{{ exp.company }}</span><br><small v-if="exp.start_date || exp.end_date" class="text-muted">{{ exp.start_date }}{{ exp.end_date && exp.start_date ? ' - ' : '' }}{{ exp.end_date }}</small></li>
                    <li v-if="professorData.professor_profile.experience.length > 3" class="text-muted mt-1"><small>+{{ professorData.professor_profile.experience.length - 3 }} autre(s)</small></li>
                </ul>
            </div>
            <div class="mb-3" v-if="hasSocialLinks && professorData.professor_profile.social_links">
                <small class="text-muted d-block mb-1"><i class="bi bi-share-fill me-2"></i>Réseaux Sociaux</small>
                <div class="mt-2 d-flex flex-wrap gap-2">
                    <a v-if="professorData.professor_profile.social_links.linkedin" :href="professorData.professor_profile.social_links.linkedin!" target="_blank" class="btn btn-sm btn-outline-primary" aria-label="LinkedIn"><i class="bi bi-linkedin"></i></a>
                    <a v-if="professorData.professor_profile.social_links.twitter" :href="professorData.professor_profile.social_links.twitter!" target="_blank" class="btn btn-sm btn-outline-info" aria-label="Twitter X"><i class="bi bi-twitter-x"></i></a>
                    <a v-if="professorData.professor_profile.social_links.github" :href="professorData.professor_profile.social_links.github!" target="_blank" class="btn btn-sm btn-outline-dark" aria-label="GitHub"><i class="bi bi-github"></i></a>
                    <a v-if="professorData.professor_profile.social_links.website" :href="professorData.professor_profile.social_links.website!" target="_blank" class="btn btn-sm btn-outline-secondary" aria-label="Site Web"><i class="bi bi-globe"></i></a>
                    <a v-if="professorData.professor_profile.social_links.orcid" :href="professorData.professor_profile.social_links.orcid!" target="_blank" class="btn btn-sm btn-outline-success" aria-label="ORCID"><i class="bi bi-person-badge"></i></a>
                    <a v-if="professorData.professor_profile.social_links.google_scholar" :href="professorData.professor_profile.social_links.google_scholar!" target="_blank" class="btn btn-sm btn-outline-danger" aria-label="Google Scholar"><i class="bi bi-mortarboard"></i></a>
                </div>
            </div>
          </div>
           <div v-else class="card-body text-muted text-center py-5">
              <i class="bi bi-person-bounding-box fs-1"></i>
              <p class="mt-2">Les informations du profil sont en cours de chargement ou non disponibles.</p>
          </div>
        </div>
      </div>
    </div>
    <div v-if="isLoadingItem && !isEditMode" class="text-center py-5"> <!-- For creation loading, if any, separate from edit mode fetch -->
        <p>Préparation du formulaire de création...</p>
    </div>
     <div v-if="!isLoadingItem && (!currentProfessor && isEditMode)" class="alert alert-warning">
        Profil du professeur non trouvé ou impossible à charger pour la modification.
    </div>
  </div>
</template>

<style scoped>
/* Styles remain the same as original file */
.avatar-placeholder { width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.sticky-top { z-index: 1000; }
.form-label-sm { font-size: 0.875em; margin-bottom: 0.25rem; }
.invalid-feedback { display: block; }
.form-control:read-only { background-color: #e9ecef; opacity: 0.8; cursor: not-allowed; }
.border-start.border-2 { border-left-width: 2px !important; border-color: var(--bs-primary-border-subtle) !important; padding-left: 0.75rem !important; }
</style>