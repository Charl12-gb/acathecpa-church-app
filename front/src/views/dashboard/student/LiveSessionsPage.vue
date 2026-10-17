<template>
  <div class="container-fluid py-4">
    <!-- Active meeting -->
    <div v-if="videoStore.activeMeetingUrl" class="meeting-wrap">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong>{{ activeSession?.title }}</strong>
        <button class="btn btn-outline-danger btn-sm" @click="leave">
          <i class="bi bi-box-arrow-left me-1"></i>Quitter la session
        </button>
      </div>
      <iframe
        :src="videoStore.activeMeetingUrl"
        class="meeting-iframe"
        allow="camera; microphone; fullscreen; display-capture; autoplay; clipboard-write"
      ></iframe>
    </div>

    <template v-else>
      <h2 class="mb-1">Sessions en direct</h2>
      <p class="text-muted mb-4">Les visioconférences programmées dans les cours que vous suivez.</p>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="!sessions.length" class="alert alert-info">
        Aucune session en direct pour vos cours pour le moment.
      </div>

      <template v-else>
        <div v-for="group in groups" :key="group.label" class="mb-4">
          <h5 v-if="group.items.length" class="mb-3">{{ group.label }}</h5>
          <div class="list-group">
            <div v-for="s in group.items" :key="s.id" class="list-group-item d-flex flex-wrap gap-3 align-items-center">
              <div class="flex-grow-1">
                <div class="fw-semibold">
                  {{ s.title }}
                  <span v-if="s.status === LiveSessionStatus.LIVE" class="badge bg-danger ms-2">En direct</span>
                </div>
                <small class="text-muted">
                  {{ formatDate(s.scheduled_for) }}
                  <template v-if="s.duration_minutes"> · {{ s.duration_minutes }} min</template>
                  <template v-if="s.host?.name"> · {{ s.host.name }}</template>
                </small>
                <p v-if="s.description" class="small mb-0 mt-1">{{ s.description }}</p>
              </div>
              <button v-if="s.status !== LiveSessionStatus.ENDED" class="btn btn-primary btn-sm"
                :disabled="joiningId === s.id" @click="join(s)">
                <span v-if="joiningId === s.id" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                Rejoindre
              </button>
            </div>
          </div>
        </div>
        <div v-if="joinError" class="alert alert-warning">{{ joinError }}</div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue';
import { getAllLiveSessions } from '../../../services/api/liveSession';
import { useVideoConferenceStore } from '../../../stores/videoConference';
import { useAuthStore } from '../../../stores/auth';
import { LiveSessionStatus, type LiveSession } from '../../../types/api/liveSessionTypes';

const videoStore = useVideoConferenceStore();
const authStore = useAuthStore();

const sessions = ref<LiveSession[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const joinError = ref<string | null>(null);
const joiningId = ref<number | null>(null);
const activeSession = ref<LiveSession | null>(null);

// The API returns only the sessions of the courses the student is enrolled in.
const groups = computed(() => [
  { label: 'À venir', items: sessions.value.filter(s => s.status !== LiveSessionStatus.ENDED)
      .sort((a, b) => a.scheduled_for.localeCompare(b.scheduled_for)) },
  { label: 'Terminées', items: sessions.value.filter(s => s.status === LiveSessionStatus.ENDED) },
]);

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString('fr-FR', { dateStyle: 'full', timeStyle: 'short' });

const join = async (session: LiveSession) => {
  joinError.value = null;
  joiningId.value = session.id;
  try {
    await videoStore.joinMeeting(session.id, authStore.user?.name || authStore.user?.email || 'Étudiant');
    activeSession.value = session;
  } catch {
    joinError.value = videoStore.error || 'Impossible de rejoindre la session.';
  } finally {
    joiningId.value = null;
  }
};

const leave = async () => {
  await videoStore.leaveMeeting();
  activeSession.value = null;
};

onMounted(async () => {
  try {
    sessions.value = await getAllLiveSessions();
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Impossible de charger les sessions.';
  } finally {
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  if (videoStore.activeMeetingUrl) videoStore.leaveMeeting();
});
</script>

<style scoped>
.meeting-iframe {
  width: 100%;
  height: 75vh;
  border: 0;
  border-radius: 8px;
  background: #000;
}
</style>
