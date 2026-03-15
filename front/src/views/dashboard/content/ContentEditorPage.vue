<template>
  <div class="content-editor-page">
    <!-- ── Toolbar ── -->
    <header class="editor-toolbar">
      <div class="toolbar-left">
        <button class="btn-back" @click="router.push('/my-content')" title="Retour">
          <i class="bi bi-arrow-left"></i>
        </button>
        <div class="toolbar-info">
          <h1 class="toolbar-title">{{ isEditing ? 'Modifier le contenu' : 'Créer un contenu' }}</h1>
          <!-- Stepper sous le titre -->
          <div class="toolbar-stepper">
            <div class="stepper-step" :class="{ active: currentStep === 1, done: currentStep > 1 }" @click="goToStep(1)">
              <span class="step-num">
                <i v-if="currentStep > 1" class="bi bi-check-lg"></i>
                <span v-else>1</span>
              </span>
              <span class="step-label">Informations</span>
            </div>
            <div class="stepper-line" :class="{ filled: currentStep > 1 }"></div>
            <div class="stepper-step" :class="{ active: currentStep === 2 }" @click="goToStep(2)">
              <span class="step-num">2</span>
              <span class="step-label">Rédaction</span>
            </div>
          </div>
        </div>
      </div>

      <div class="toolbar-actions">
        <span class="type-chip" :class="contentForm.type">
          <i :class="contentForm.type === 'article' ? 'bi bi-file-earmark-richtext' : 'bi bi-mic'"></i>
          {{ contentForm.type === 'article' ? 'Article' : 'Podcast' }}
        </span>
        <span class="status-chip" :class="contentForm.status">
          <i :class="contentForm.status === 'published' ? 'bi bi-globe' : 'bi bi-pencil'"></i>
          {{ contentForm.status === 'published' ? 'Publié' : 'Brouillon' }}
        </span>
      </div>
    </header>

    <!-- ══════════ STEP 1 : Informations ══════════ -->
    <div v-show="currentStep === 1" class="step-content">
      <div class="editor-grid" :class="{ 'with-preview': showPreview }">
        <div class="form-col">

          <!-- Card : Infos principales -->
          <section class="editor-card">
            <div class="card-head">
              <span class="card-icon"><i class="bi bi-pencil-square"></i></span>
              <h2>Informations principales</h2>
            </div>
            <div class="card-inner">

              <!-- ── Section : Identité ── -->
              <div class="form-section">
                <div class="section-label">
                  <i class="bi bi-type"></i>
                  <span>Identité du contenu</span>
                </div>
                <div class="field">
                  <label>Titre <span class="req">*</span></label>
                  <div class="input-icon-wrap">
                    <span class="input-icon"><i class="bi bi-cursor-text"></i></span>
                    <input type="text" v-model="contentForm.title" placeholder="Ex : Les fondamentaux de la comptabilité">
                  </div>
                  <span class="field-hint"><i class="bi bi-lightbulb"></i> Un titre clair et concis améliore la visibilité</span>
                </div>
                <div class="field">
                  <label>Description</label>
                  <textarea v-model="contentForm.description" rows="3" placeholder="Décrivez brièvement le contenu pour donner envie aux lecteurs…"></textarea>
                  <span class="field-hint char-count">{{ contentForm.description?.length || 0 }} / 300 caractères</span>
                </div>
              </div>

              <!-- ── Section : Classification ── -->
              <div class="form-section">
                <div class="section-label">
                  <i class="bi bi-grid-3x3-gap"></i>
                  <span>Classification</span>
                </div>

                <div class="field">
                  <label>Type de contenu</label>
                  <div class="type-cards">
                    <label class="type-card" :class="{ selected: contentForm.type === 'article' }">
                      <input type="radio" name="ctype" value="article" v-model="contentForm.type">
                      <span class="tc-icon article"><i class="bi bi-file-earmark-richtext"></i></span>
                      <span class="tc-info">
                        <strong>Article</strong>
                        <small>Contenu textuel, tutoriel, guide</small>
                      </span>
                      <span class="tc-check"><i class="bi bi-check-circle-fill"></i></span>
                    </label>
                    <label class="type-card" :class="{ selected: contentForm.type === 'podcast' }">
                      <input type="radio" name="ctype" value="podcast" v-model="contentForm.type">
                      <span class="tc-icon podcast"><i class="bi bi-mic"></i></span>
                      <span class="tc-info">
                        <strong>Podcast</strong>
                        <small>Audio, interview, discussion</small>
                      </span>
                      <span class="tc-check"><i class="bi bi-check-circle-fill"></i></span>
                    </label>
                  </div>
                </div>

                <div class="field">
                  <label>Format du média</label>
                  <div class="format-grid">
                    <label class="format-chip" :class="{ selected: contentForm.format === 'text' }">
                      <input type="radio" name="cformat" value="text" v-model="contentForm.format">
                      <i class="bi bi-fonts"></i>
                      <span>Texte</span>
                    </label>
                    <label class="format-chip" :class="{ selected: contentForm.format === 'audio' }">
                      <input type="radio" name="cformat" value="audio" v-model="contentForm.format">
                      <i class="bi bi-soundwave"></i>
                      <span>Audio</span>
                    </label>
                    <label class="format-chip" :class="{ selected: contentForm.format === 'video' }">
                      <input type="radio" name="cformat" value="video" v-model="contentForm.format">
                      <i class="bi bi-camera-video"></i>
                      <span>Vidéo</span>
                    </label>
                    <label class="format-chip" :class="{ selected: contentForm.format === 'pdf' }">
                      <input type="radio" name="cformat" value="pdf" v-model="contentForm.format">
                      <i class="bi bi-file-pdf"></i>
                      <span>PDF</span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- ── Section : Publication ── -->
              <div class="form-section last">
                <div class="section-label">
                  <i class="bi bi-megaphone"></i>
                  <span>Publication</span>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label>Statut</label>
                    <div class="status-selector">
                      <label class="status-opt" :class="{ selected: contentForm.status === 'draft' }">
                        <input type="radio" name="cstatus" value="draft" v-model="contentForm.status">
                        <span class="so-dot draft"></span>
                        <span>Brouillon</span>
                      </label>
                      <label class="status-opt" :class="{ selected: contentForm.status === 'published' }">
                        <input type="radio" name="cstatus" value="published" v-model="contentForm.status">
                        <span class="so-dot published"></span>
                        <span>Publié</span>
                      </label>
                    </div>
                  </div>
                  <div class="field">
                    <label>Tags</label>
                    <div class="tags-input-wrap">
                      <input type="text" v-model="tagsInput" placeholder="Séparez par des virgules, puis Entrée" @keyup.enter="addTag">
                      <button v-if="tagsInput" class="tags-add-btn" @click="addTag" title="Ajouter"><i class="bi bi-plus-lg"></i></button>
                    </div>
                    <span class="field-hint"><i class="bi bi-info-circle"></i> Ajoutez des mots-clés pour faciliter la recherche</span>
                  </div>
                </div>

                <div v-if="contentForm.tags.length > 0" class="tags-list">
                  <span v-for="tag in contentForm.tags" :key="tag" class="tag-pill" @click="removeTag(tag)">
                    {{ tag }} <i class="bi bi-x"></i>
                  </span>
                </div>
              </div>

            </div>
          </section>

          <!-- Card : Monétisation -->
          <section class="editor-card">
            <div class="card-head">
              <span class="card-icon icon-orange"><i class="bi bi-star-fill"></i></span>
              <h2>Monétisation</h2>
            </div>
            <div class="card-inner">
              <label class="cb-label">
                <input type="checkbox" v-model="contentForm.isPremium">
                <span class="cb-box"><i class="bi bi-check"></i></span>
                Contenu premium (accès payant)
              </label>

              <div v-if="contentForm.isPremium" class="field" style="margin-top: 16px;">
                <label>Prix (XOF)</label>
                <div class="price-input-wrap">
                  <span class="currency">XOF</span>
                  <input type="number" v-model="contentForm.price" min="0" step="0.01" placeholder="0">
                </div>
              </div>
            </div>
          </section>

          <!-- Step navigation -->
          <div class="step-nav">
            <div></div>
            <button class="btn-step btn-next" @click="nextStep">
              Suivant : Rédaction <i class="bi bi-arrow-right"></i>
            </button>
          </div>
        </div>

        <!-- ─ Preview column ─ -->
        <aside class="preview-col" v-if="showPreview">
          <div class="preview-panel">
            <div class="preview-head">
              <h2><i class="bi bi-eye"></i> Aperçu</h2>
              <button class="preview-close" @click="showPreview = false"><i class="bi bi-x-lg"></i></button>
            </div>
            <div class="preview-body">
              <div class="preview-tags-row">
                <span class="pv-badge" :class="contentForm.type">
                  <i :class="contentForm.type === 'article' ? 'bi bi-file-earmark-richtext' : 'bi bi-mic'"></i>
                  {{ contentForm.type === 'article' ? 'Article' : 'Podcast' }}
                </span>
                <span class="pv-badge" :class="contentForm.status">
                  {{ contentForm.status === 'published' ? 'Publié' : 'Brouillon' }}
                </span>
                <span class="pv-badge format">{{ contentForm.format }}</span>
              </div>

              <h3 class="preview-title">{{ contentForm.title || 'Titre du contenu' }}</h3>
              <p class="preview-desc">{{ contentForm.description || 'La description apparaîtra ici…' }}</p>

              <div v-if="contentForm.tags.length" class="preview-tags">
                <span v-for="tag in contentForm.tags" :key="tag" class="pv-tag">{{ tag }}</span>
              </div>

              <div v-if="contentForm.isPremium" class="premium-banner">
                <i class="bi bi-star-fill"></i>
                <div>
                  <span class="premium-label">Contenu premium</span>
                  <span class="premium-price">{{ contentForm.price || 0 }} XOF</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <button v-if="!showPreview" class="fab-preview" @click="showPreview = true" title="Afficher l'aperçu">
        <i class="bi bi-eye"></i>
      </button>
    </div>

    <!-- ══════════ STEP 2 : Rédaction ══════════ -->
    <div v-show="currentStep === 2" class="step-content">

      <!-- Writing header -->
      <div class="writing-header">
        <div class="wh-left">
          <span class="wh-icon"><i class="bi bi-pen"></i></span>
          <div>
            <h2 class="wh-title">{{ contentForm.title || 'Sans titre' }}</h2>
            <p class="wh-sub">
              <span class="wh-badge" :class="contentForm.type">
                <i :class="contentForm.type === 'article' ? 'bi bi-file-earmark-richtext' : 'bi bi-mic'"></i>
                {{ contentForm.type === 'article' ? 'Article' : 'Podcast' }}
              </span>
              <span class="wh-badge format">{{ contentForm.format }}</span>
            </p>
          </div>
        </div>
        <button class="btn-save" @click="saveContent" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <i v-else class="bi bi-check-circle"></i>
          <span class="btn-label">{{ contentForm.status === 'draft' ? 'Enregistrer' : 'Publier' }}</span>
        </button>
      </div>

      <!-- Editor area -->
      <div class="writing-area">
        <div v-if="contentForm.format === 'text'">
          <ContentEditor v-model="contentForm.content" />
        </div>

        <div v-else-if="['audio', 'video', 'pdf'].includes(contentForm.format)" class="media-card">
          <div class="media-card-head">
            <span class="media-card-icon">
              <i :class="contentForm.format === 'audio' ? 'bi bi-soundwave' : contentForm.format === 'video' ? 'bi bi-camera-video' : 'bi bi-file-pdf'"></i>
            </span>
            <div>
              <h3>{{ contentForm.format === 'audio' ? 'Fichier Audio' : contentForm.format === 'video' ? 'Fichier Vidéo' : 'Document PDF' }}</h3>
              <p>Ajoutez le lien vers votre média</p>
            </div>
          </div>
          <div class="field">
            <label>URL du média</label>
            <div class="media-input-wrap">
              <span class="media-icon">
                <i :class="contentForm.format === 'audio' ? 'bi bi-soundwave' : contentForm.format === 'video' ? 'bi bi-camera-video' : 'bi bi-file-pdf'"></i>
              </span>
              <input type="url" v-model="contentForm.mediaUrl" placeholder="https://…">
            </div>
            <span class="field-hint">
              <i class="bi bi-info-circle"></i>
              {{ contentForm.format === 'audio' ? 'Lien vers un fichier audio (.mp3, .wav, .ogg)' : contentForm.format === 'video' ? 'YouTube, Vimeo, ou lien direct (.mp4)' : 'Lien vers un fichier PDF' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Step navigation -->
      <div class="step-nav">
        <button class="btn-step btn-prev" @click="prevStep">
          <i class="bi bi-arrow-left"></i> Précédent : Informations
        </button>
        <button class="btn-save" @click="saveContent" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <i v-else class="bi bi-check-circle"></i>
          <span class="btn-label">{{ contentForm.status === 'draft' ? 'Enregistrer' : 'Publier' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useContentStore } from '../../../stores/content'
import ContentEditor from '../../../components/content/ContentEditor.vue'

const route = useRoute()
const router = useRouter()
const contentStore = useContentStore()

const isEditing = computed(() => !!route.params.id)
const loading = computed(() => contentStore.loading)
const showPreview = ref(true)
const currentStep = ref(1)

// Form data
const contentForm = ref({
  title: '',
  description: '',
  content: '',
  type: 'article',
  format: 'text',
  mediaUrl: '',
  isPremium: false,
  price: 0,
  status: 'draft',
  tags: [] as string[]
})

const tagsInput = ref('')

// Step navigation
const validateStep1 = (): boolean => {
  if (!contentForm.value.title.trim()) {
    alert('Le titre est obligatoire.')
    return false
  }
  return true
}

const nextStep = () => {
  if (currentStep.value === 1 && !validateStep1()) return
  currentStep.value = 2
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const prevStep = () => {
  currentStep.value = 1
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goToStep = (step: number) => {
  if (step === 2 && !validateStep1()) return
  currentStep.value = step
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Add tag
const addTag = () => {
  const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag)
  contentForm.value.tags = [...new Set([...contentForm.value.tags, ...tags])]
  tagsInput.value = ''
}

// Remove tag
const removeTag = (tag: string) => {
  contentForm.value.tags = contentForm.value.tags.filter(t => t !== tag)
}

// Load content if editing
onMounted(async () => {
  if (isEditing.value) {
    try {
      const content = await contentStore.getContent(parseInt(route.params.id as string))
      contentForm.value = {
        ...content,
        tags: content.tags || []
      }
    } catch (error) {
      console.error('Error loading content:', error)
    }
  }
})

// Save content
const saveContent = async () => {
  try {
    const payload: any = {
        ...contentForm.value,
        content_body: contentForm.value.content
    };
    await contentStore.saveContent(payload)
    router.push('/my-content')
  } catch (error) {
    console.error('Error saving content:', error)
  }
}
</script>

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
$yellow: #ca8a04;
$yellow-soft: #fefce8;

/* ── Page ── */
.content-editor-page {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 24px 48px;
  position: relative;
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
  gap: 10px;
}
.type-chip, .status-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 13px;
  border-radius: 20px;
  font-size: .76rem;
  font-weight: 600;
  i { font-size: .82rem; }
}
.type-chip {
  background: $primary-soft;
  color: $primary;
  &.podcast { background: $green-soft; color: $green; }
}
.status-chip {
  background: $yellow-soft;
  color: $yellow;
  &.published { background: $green-soft; color: $green; }
}

/* ── Stepper (under title) ── */
.toolbar-stepper {
  display: flex;
  align-items: center;
  gap: 0;
}
.stepper-step {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: .2s;
  padding: 2px 6px;
  border-radius: 6px;
  &:hover { background: rgba($primary-soft, .5); }
}
.step-num {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: grid; place-items: center;
  font-size: .68rem;
  font-weight: 700;
  background: $gray-light;
  color: $gray;
  border: 1.5px solid $border;
  transition: .2s;
}
.step-label {
  font-size: .76rem;
  font-weight: 600;
  color: $gray;
  transition: .2s;
}
.stepper-step.active {
  .step-num {
    background: $primary;
    color: #fff;
    border-color: $primary;
  }
  .step-label { color: $primary; }
}
.stepper-step.done {
  .step-num {
    background: $green-soft;
    color: $green;
    border-color: $green;
  }
  .step-label { color: $green; }
}
.stepper-line {
  flex: 0 0 24px;
  height: 1.5px;
  background: $border;
  border-radius: 2px;
  margin: 0 4px;
  transition: .3s;
  &.filled { background: $green; }
}

/* ── Step navigation ── */
.step-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
}
.btn-step {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 22px;
  border-radius: $radius-sm;
  font-size: .88rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: .2s;
}
.btn-prev {
  background: $gray-light;
  color: $dark;
  border: 1px solid $border;
  &:hover { background: $primary-soft; color: $primary; border-color: $primary; }
}
.btn-next {
  background: $primary;
  color: #fff;
  &:hover { background: $primary-dark; }
}

/* ── Save button ── */
.btn-save {
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

/* ── Writing header (Step 2) ── */
.writing-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  padding: 18px 24px;
  margin-bottom: 20px;
  box-shadow: $shadow;
}
.wh-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.wh-icon {
  width: 42px; height: 42px;
  border-radius: 10px;
  background: $primary-soft;
  color: $primary;
  display: grid; place-items: center;
  font-size: 1.15rem;
}
.wh-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 4px;
}
.wh-sub {
  display: flex;
  gap: 8px;
  margin: 0;
}
.wh-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  background: $primary-soft;
  color: $primary;
  &.podcast { background: $green-soft; color: $green; }
  &.format { background: $gray-light; color: $gray; text-transform: uppercase; }
}

/* ── Writing area ── */
.writing-area {
  margin-bottom: 0;
}

/* ── Media card (non-text formats in Step 2) ── */
.media-card {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;
  padding: 28px;
}
.media-card-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
  h3 {
    font-size: 1rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 2px;
  }
  p {
    font-size: .82rem;
    color: $gray;
    margin: 0;
  }
}
.media-card-icon {
  width: 44px; height: 44px;
  border-radius: 10px;
  background: $purple-soft;
  color: $purple;
  display: grid; place-items: center;
  font-size: 1.2rem;
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
  &.icon-purple { background: $purple-soft; color: $purple; }
  &.icon-orange { background: $orange-soft; color: $orange; }
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
    &::placeholder { color: #b0b8c9; }
  }
  textarea { resize: vertical; }
  select { cursor: pointer; }
}
.field-row {
  display: flex;
  gap: 16px;
  & > .field { flex: 1; }
}
.field-hint {
  display: block;
  font-size: .76rem;
  color: $gray;
  margin-top: 6px;
  i { margin-right: 4px; }
  &.char-count { text-align: right; }
}
.req { color: $red; }

/* ── Form sections ── */
.form-section {
  padding-bottom: 24px;
  margin-bottom: 24px;
  border-bottom: 1px solid $border;
  &.last { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
}
.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding-bottom: 10px;
  i {
    font-size: .88rem;
    color: $primary;
  }
  span {
    font-size: .78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: $gray;
  }
}

/* ── Input with icon ── */
.input-icon-wrap {
  position: relative;
  input {
    width: 100%;
    padding: 12px 14px 12px 42px;
    border: 1px solid $border;
    border-radius: $radius-sm;
    font-size: .92rem;
    font-weight: 500;
    color: $dark;
    background: #fff;
    transition: .2s;
    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 3px rgba($primary, .1);
    }
    &::placeholder { color: #b0b8c9; font-weight: 400; }
  }
}
.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: $gray;
  font-size: .92rem;
  pointer-events: none;
  transition: .2s;
}
.input-icon-wrap:focus-within .input-icon { color: $primary; }

/* ── Type cards (Article / Podcast) ── */
.type-cards {
  display: flex;
  gap: 12px;
}
.type-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid $border;
  border-radius: $radius;
  cursor: pointer;
  transition: .2s;
  position: relative;
  background: #fff;
  input { display: none; }
  &:hover { border-color: rgba($primary, .4); background: rgba($primary-soft, .3); }
  &.selected {
    border-color: $primary;
    background: $primary-soft;
    .tc-check { opacity: 1; color: $primary; }
  }
}
.tc-icon {
  width: 42px; height: 42px;
  border-radius: 10px;
  display: grid; place-items: center;
  font-size: 1.15rem;
  flex-shrink: 0;
  &.article { background: $primary-soft; color: $primary; }
  &.podcast { background: $green-soft; color: $green; }
}
.tc-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  strong {
    font-size: .88rem;
    color: $dark;
  }
  small {
    font-size: .74rem;
    color: $gray;
    line-height: 1.3;
  }
}
.tc-check {
  margin-left: auto;
  opacity: 0;
  font-size: 1.1rem;
  transition: .2s;
}

/* ── Format grid ── */
.format-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.format-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border: 2px solid $border;
  border-radius: $radius;
  font-size: .78rem;
  font-weight: 600;
  color: $gray;
  cursor: pointer;
  transition: .2s;
  background: #fff;
  text-align: center;
  input { display: none; }
  i { font-size: 1.15rem; transition: .2s; }
  &:hover { border-color: rgba($primary, .4); color: $primary; }
  &.selected {
    background: $primary-soft;
    border-color: $primary;
    color: $primary;
    i { transform: scale(1.15); }
  }
}

/* ── Status selector ── */
.status-selector {
  display: flex;
  gap: 10px;
}
.status-opt {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  border: 1px solid $border;
  border-radius: $radius-sm;
  font-size: .85rem;
  font-weight: 600;
  color: $gray;
  cursor: pointer;
  transition: .2s;
  background: #fff;
  input { display: none; }
  &:hover { border-color: $primary; }
  &.selected { border-color: $primary; background: $primary-soft; color: $primary; }
}
.so-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  &.draft { background: $yellow; }
  &.published { background: $green; }
}

/* ── Tags ── */
.tags-input-wrap {
  position: relative;
  input {
    width: 100%;
    padding: 10px 14px;
    padding-right: 40px;
    border: 1px solid $border;
    border-radius: $radius-sm;
    font-size: .88rem;
    color: $dark;
    &:focus { outline: none; border-color: $primary; box-shadow: 0 0 0 3px rgba($primary,.1); }
    &::placeholder { color: #b0b8c9; }
  }
}
.tags-add-btn {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px; height: 28px;
  border-radius: 7px;
  border: none;
  background: $primary;
  color: #fff;
  font-size: .78rem;
  cursor: pointer;
  display: grid; place-items: center;
  transition: .2s;
  &:hover { background: $primary-dark; }
}
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}
.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  background: $primary-soft;
  color: $primary;
  border-radius: 20px;
  font-size: .78rem;
  font-weight: 600;
  cursor: pointer;
  transition: .2s;
  i { font-size: .7rem; }
  &:hover { background: $primary; color: #fff; }
}

/* ── Checkbox ── */
.cb-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: .88rem;
  font-weight: 500;
  color: $dark;
  cursor: pointer;
  input { display: none; }
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

/* ── Media input ── */
.media-input-wrap {
  display: flex;
  border: 1px solid $border;
  border-radius: $radius-sm;
  overflow: hidden;
  transition: .2s;
  &:focus-within { border-color: $primary; box-shadow: 0 0 0 3px rgba($primary,.1); }
  input {
    flex: 1;
    border: none !important;
    box-shadow: none !important;
    padding: 10px 14px;
    font-size: .88rem;
    color: $dark;
    &::placeholder { color: #b0b8c9; }
  }
}
.media-icon {
  display: grid;
  place-items: center;
  width: 44px;
  background: $gray-light;
  color: $primary;
  font-size: 1.1rem;
  border-right: 1px solid $border;
}

/* ── Price input ── */
.price-input-wrap {
  display: flex;
  border: 1px solid $border;
  border-radius: $radius-sm;
  overflow: hidden;
  &:focus-within { border-color: $primary; box-shadow: 0 0 0 3px rgba($primary,.1); }
  input {
    flex: 1;
    border: none !important;
    box-shadow: none !important;
    padding: 10px 14px;
    font-size: .88rem;
    color: $dark;
  }
}
.currency {
  display: grid;
  place-items: center;
  padding: 0 14px;
  background: $orange-soft;
  color: $orange;
  font-size: .78rem;
  font-weight: 700;
  border-right: 1px solid $border;
}

/* ── Preview panel ── */
.preview-col { position: relative; }
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
  padding: 14px 20px;
  border-bottom: 1px solid $border;
  background: $gray-light;
  h2 {
    font-size: .92rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 7px;
    i { color: $primary; }
  }
}
.preview-close {
  width: 28px; height: 28px;
  border-radius: 7px;
  border: 1px solid $border;
  background: #fff;
  color: $gray;
  font-size: .75rem;
  cursor: pointer;
  display: grid; place-items: center;
  transition: .2s;
  &:hover { background: #fef2f2; color: $red; border-color: $red; }
}
.preview-body {
  padding: 20px;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}
.preview-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}
.pv-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  background: $primary-soft;
  color: $primary;
  &.podcast { background: $green-soft; color: $green; }
  &.published { background: $green-soft; color: $green; }
  &.draft { background: $yellow-soft; color: $yellow; }
  &.format { background: $gray-light; color: $gray; text-transform: uppercase; font-size: .68rem; }
}
.preview-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 8px;
}
.preview-desc {
  font-size: .82rem;
  color: $gray;
  line-height: 1.55;
  margin: 0 0 14px;
}
.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}
.pv-tag {
  padding: 4px 10px;
  background: $gray-light;
  border: 1px solid $border;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  color: $dark;
}
.premium-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: linear-gradient(135deg, $orange-soft, #fff);
  border: 1px solid rgba($orange, .25);
  border-radius: $radius-sm;
  margin-bottom: 16px;
  & > i {
    font-size: 1.3rem;
    color: $orange;
  }
}
.premium-label {
  display: block;
  font-size: .78rem;
  font-weight: 600;
  color: $dark;
}
.premium-price {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: $orange;
}

/* ── FAB ── */
.fab-preview {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 50px; height: 50px;
  border-radius: 50%;
  border: none;
  background: $primary;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba($primary, .35);
  display: grid; place-items: center;
  transition: .2s;
  z-index: 100;
  &:hover { background: $primary-dark; transform: scale(1.08); }
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
  .field-row { flex-direction: column; gap: 0; }
  .type-cards { flex-direction: column; }
  .format-grid { grid-template-columns: repeat(2, 1fr); }
  .status-selector { flex-direction: column; }
  .content-editor-page { padding: 0 12px 32px; }
  .card-inner { padding: 16px; }
  .toolbar-stepper { display: none; }
  .stepper-mobile {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    width: 100%;
  }
  .step-label { display: none; }
  .step-nav { flex-direction: column; gap: 12px; }
  .btn-step { width: 100%; justify-content: center; }
  .writing-header { flex-direction: column; align-items: flex-start; }
  .fab-preview { bottom: 16px; right: 16px; width: 44px; height: 44px; }
}
</style>