<template>
  <div class="file-uploader" :class="{ 'has-file': !!modelValue, 'is-uploading': uploading, 'has-error': !!error }">
    <input
      ref="inputRef"
      type="file"
      class="file-uploader__input"
      :accept="accept"
      @change="onFileSelected"
    />

    <!-- Empty state -->
    <div v-if="!modelValue && !uploading" class="file-uploader__drop" @click="triggerInput">
      <i class="bi" :class="iconClass"></i>
      <div class="file-uploader__label">
        <strong>Cliquer pour téléverser</strong>
        <span>{{ helpText }}</span>
      </div>
    </div>

    <!-- Uploading -->
    <div v-else-if="uploading" class="file-uploader__progress">
      <div class="spinner"></div>
      <div class="file-uploader__progress-info">
        <strong>Téléversement en cours…</strong>
        <div class="progress-bar"><div class="progress-bar__fill" :style="{ width: progress + '%' }"></div></div>
        <span>{{ progress }}%</span>
      </div>
    </div>

    <!-- File present -->
    <div v-else class="file-uploader__preview">
      <!-- Image preview -->
      <img v-if="isImage" :src="resolvedUrl" alt="Aperçu" class="file-uploader__thumb" />
      <!-- Audio preview -->
      <audio v-else-if="isAudio" :src="resolvedUrl" controls class="file-uploader__media"></audio>
      <!-- Video preview -->
      <video v-else-if="isVideo" :src="resolvedUrl" controls class="file-uploader__media"></video>
      <!-- Other (PDF / doc) -->
      <div v-else class="file-uploader__file-card">
        <i class="bi bi-file-earmark-fill"></i>
        <a :href="resolvedUrl" target="_blank" rel="noopener" class="file-uploader__filename">
          {{ filename }}
        </a>
      </div>

      <div class="file-uploader__actions">
        <button type="button" class="btn-replace" @click="triggerInput">
          <i class="bi bi-arrow-repeat"></i> Remplacer
        </button>
        <button type="button" class="btn-remove" @click="clearFile">
          <i class="bi bi-trash3"></i> Supprimer
        </button>
      </div>
    </div>

    <span v-if="error" class="file-uploader__error">
      <i class="bi bi-exclamation-triangle-fill"></i> {{ error }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { uploadFile, resolveMediaUrl, type UploadCategory } from '../services/api/upload';

interface Props {
  modelValue: string | null | undefined;
  category?: UploadCategory;     // image | video | audio | document
  accept?: string;               // attribut HTML accept
  helpText?: string;
}

const props = withDefaults(defineProps<Props>(), {
  category: undefined,
  accept: '*/*',
  helpText: 'PNG, JPG, MP4, MP3, PDF…',
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void;
  (e: 'uploaded', value: { url: string; filename: string }): void;
  (e: 'error', message: string): void;
}>();

const inputRef = ref<HTMLInputElement | null>(null);
const uploading = ref(false);
const progress = ref(0);
const error = ref<string | null>(null);

const resolvedUrl = computed(() => resolveMediaUrl(props.modelValue));

const filename = computed(() => {
  const url = props.modelValue || '';
  return url.split('/').pop() || url;
});

const isImage = computed(() => {
  if (props.category === 'image') return true;
  return /\.(png|jpe?g|gif|webp|svg|avif)$/i.test(props.modelValue || '');
});
const isAudio = computed(() => {
  if (props.category === 'audio') return true;
  return /\.(mp3|wav|ogg|m4a|aac|flac)$/i.test(props.modelValue || '');
});
const isVideo = computed(() => {
  if (props.category === 'video') return true;
  return /\.(mp4|webm|mov|m4v|avi)$/i.test(props.modelValue || '');
});

const iconClass = computed(() => {
  switch (props.category) {
    case 'image': return 'bi-image';
    case 'audio': return 'bi-music-note-beamed';
    case 'video': return 'bi-camera-video';
    case 'document': return 'bi-file-earmark-pdf';
    default: return 'bi-cloud-arrow-up';
  }
});

const triggerInput = () => inputRef.value?.click();

const onFileSelected = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  error.value = null;
  uploading.value = true;
  progress.value = 0;

  try {
    const result = await uploadFile(file, props.category, (p) => (progress.value = p));
    emit('update:modelValue', result.url);
    emit('uploaded', { url: result.url, filename: result.filename });
  } catch (err: any) {
    const message =
      err?.response?.data?.detail ||
      err?.message ||
      'Échec du téléversement.';
    error.value = message;
    emit('error', message);
  } finally {
    uploading.value = false;
    if (inputRef.value) inputRef.value.value = '';
  }
};

const clearFile = () => {
  emit('update:modelValue', null);
  error.value = null;
};
</script>

<style scoped>
.file-uploader { width: 100%; }
.file-uploader__input { display: none; }

.file-uploader__drop {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border: 2px dashed #d6d2c5;
  border-radius: 12px;
  background: #fafaf6;
  cursor: pointer;
  transition: border-color .2s, background .2s;
}
.file-uploader__drop:hover { border-color: #C14428; background: #fff6f1; }
.file-uploader__drop i { font-size: 1.8rem; color: #C14428; }
.file-uploader__label { display: flex; flex-direction: column; line-height: 1.3; }
.file-uploader__label strong { color: #2c3142; font-size: .95rem; }
.file-uploader__label span { color: #7b8094; font-size: .82rem; }

.file-uploader__progress {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #fffaf2;
  border: 1px solid #f0d9b5;
  border-radius: 10px;
}
.spinner {
  width: 22px; height: 22px; border-radius: 50%;
  border: 3px solid #f0d9b5; border-top-color: #C14428;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.file-uploader__progress-info { flex: 1; display: flex; flex-direction: column; gap: 4px; font-size: .85rem; }
.progress-bar { height: 6px; background: #f0e4d3; border-radius: 4px; overflow: hidden; }
.progress-bar__fill { height: 100%; background: linear-gradient(90deg, #FFD86B, #C14428); transition: width .2s; }

.file-uploader__preview {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  border: 1px solid #e6e1d3;
  border-radius: 10px;
  background: #fff;
}
.file-uploader__thumb {
  width: 84px; height: 84px; object-fit: cover;
  border-radius: 8px;
  background: #f4f1ea;
}
.file-uploader__media { flex: 1; max-height: 100px; }
.file-uploader__file-card {
  flex: 1; display: flex; align-items: center; gap: 10px; min-width: 0;
}
.file-uploader__file-card i { font-size: 1.8rem; color: #C14428; }
.file-uploader__filename {
  color: #2c3142; font-size: .9rem; font-weight: 600;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  text-decoration: none;
}
.file-uploader__filename:hover { text-decoration: underline; }

.file-uploader__actions {
  display: flex; flex-direction: column; gap: 6px;
}
.btn-replace, .btn-remove {
  border: none; border-radius: 6px; padding: 6px 10px;
  font-size: .78rem; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 5px;
  white-space: nowrap;
}
.btn-replace { background: #f0e9d9; color: #5a4d2a; }
.btn-replace:hover { background: #e3d9c0; }
.btn-remove { background: #fde7e2; color: #C14428; }
.btn-remove:hover { background: #f9d4cb; }

.file-uploader__error {
  display: inline-flex; align-items: center; gap: 6px;
  margin-top: 8px;
  font-size: .82rem; color: #b3261e;
}
</style>
