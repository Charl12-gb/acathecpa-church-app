<template>
    <div class="container py-5">
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
            {{ error }}
        </div>

        <template v-else-if="podcast">
            <!-- Podcast Header -->
            <div class="row mb-4">
                <div class="col-lg-8 mx-auto">
                    <nav aria-label="breadcrumb" class="mb-4">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item">
                                <RouterLink to="/podcasts">Podcasts</RouterLink>
                            </li>
                            <li class="breadcrumb-item active" aria-current="page">
                                {{ podcast.title }}
                            </li>
                        </ol>
                    </nav>

                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-4 mb-md-0">
                                    <img :src="podcast.mediaUrl || pData.media_url || 'https://placehold.co/400x400?text=Podcast'"
                                        class="img-fluid rounded" :alt="podcast.title">
                                </div>
                                <div class="col-md-8">
                                    <h1 class="mb-3">{{ podcast.title }}</h1>

                                    <div class="d-flex flex-wrap gap-3 mb-3">
                                        <span class="badge"
                                            :class="podcast.format === 'audio' ? 'bg-success' : 'bg-danger'">
                                            {{ podcast.format }}
                                        </span>
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-calendar me-2"></i>
                                            <span>{{ new Date(podcast.created_at).toLocaleDateString() }}</span>
                                        </div>
                                    </div>

                                    <div class="d-flex align-items-center mb-4" v-if="podcast.author">
                                        <div class="rounded-circle bg-light p-2 me-2">
                                            <i class="bi bi-person-circle text-primary"></i>
                                        </div>
                                        <span>{{ podcast.author.name }}</span>
                                    </div>

                                    <p class="lead mb-4">{{ podcast.description }}</p>

                                    <div class="d-flex flex-wrap gap-2 mb-4">
                                        <span v-for="tag in podcast.tags" :key="tag" class="badge bg-light text-dark">
                                            {{ tag }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Podcast Content -->
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card border-0 shadow-sm mb-4">
                        <div class="card-body">
                            <!-- Premium gate -->
                            <div v-if="pData.requires_payment" class="premium-gate text-center py-5">
                                <div class="premium-icon mb-3">
                                    <i class="bi bi-headphones"></i>
                                </div>
                                <span class="badge bg-warning text-dark mb-3">
                                    <i class="bi bi-star-fill me-1"></i> Podcast Premium
                                </span>
                                <h3 class="mb-2 fw-bold">Écoutez l'épisode complet</h3>
                                <p class="text-muted mb-2">
                                    Cet épisode est réservé à nos auditeurs premium. Débloquez-le pour
                                    profiter de <strong>l'enregistrement intégral</strong>, des
                                    <strong>notes d'épisode détaillées</strong> et soutenez la production
                                    de contenus de qualité.
                                </p>
                                <ul class="list-unstyled text-start d-inline-block mt-3 mb-4">
                                    <li><i class="bi bi-check2-circle text-success me-2"></i>Écoute illimitée à vie</li>
                                    <li><i class="bi bi-check2-circle text-success me-2"></i>Streaming sur tous vos appareils</li>
                                    <li><i class="bi bi-check2-circle text-success me-2"></i>Soutien direct à l'auteur</li>
                                </ul>
                                <div class="price-tag mb-3">
                                    <span class="display-5 fw-bold text-primary">{{ podcast.price }}</span>
                                    <span class="text-muted ms-2">XOF · paiement unique</span>
                                </div>
                                <div v-if="purchaseError" class="alert alert-danger mt-3">{{ purchaseError }}</div>
                                <button
                                    class="btn btn-warning btn-lg px-4 mt-2"
                                    @click="openPurchaseModal"
                                >
                                    <i class="bi bi-unlock-fill me-2"></i>
                                    {{ authStore.isAuthenticated ? `Débloquer pour ${podcast.price} XOF` : 'Se connecter pour acheter' }}
                                </button>
                                <p class="small text-muted mt-3 mb-0">
                                    <i class="bi bi-shield-check me-1"></i>
                                    Paiement sécurisé · Accès immédiat après confirmation
                                </p>
                            </div>

                            <template v-else>
                            <!-- Audio Player -->
                            <div v-if="podcast.format === 'audio'" class="audio-player mb-4">
                                <audio controls class="w-100">
                                    <source :src="podcast.mediaUrl || pData.media_url" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                            </div>

                            <!-- Video Player -->
                            <div v-else-if="podcast.format === 'video'" class="ratio ratio-16x9 mb-4">
                                <iframe :src="podcast.mediaUrl || pData.media_url" allowfullscreen
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
                            </div>

                            <!-- Text Content -->
                            <div v-if="podcast.content || pData.content_body" class="podcast-content" v-html="podcast.content || pData.content_body"></div>
                            </template>
                        </div>
                    </div>

                    <!-- Premium Content Notice -->
                    <div v-if="podcast.isPremium || pData.is_premium" class="alert alert-warning">
                        <i class="bi bi-star-fill me-2"></i>
                        Contenu premium
                        <strong class="ms-2">{{ podcast.price }}XOF</strong>
                    </div>
                </div>
            </div>
        </template>

    <!-- ═══ Purchase Modal ═══ -->
    <Teleport to="body">
      <div
        v-if="showPurchaseModal && podcast"
        class="purchase-modal-backdrop"
        @click.self="closePurchaseModal"
      >
        <div class="purchase-modal">
          <button class="purchase-modal-close" @click="closePurchaseModal">
            <i class="bi bi-x-lg"></i>
          </button>

          <div v-if="purchaseSuccess" class="purchase-modal-body text-center">
            <div class="success-icon"><i class="bi bi-check-circle-fill"></i></div>
            <h3 class="mb-2">Paiement confirmé !</h3>
            <p class="text-muted mb-4">
              Vous avez maintenant accès à <strong>{{ podcast.title }}</strong>.
            </p>
            <button class="btn btn-warning btn-lg px-4" @click="closePurchaseModal">
              <i class="bi bi-play-circle-fill me-2"></i> Écouter le podcast
            </button>
          </div>

          <template v-else>
            <div class="purchase-modal-header text-center">
              <div class="purchase-modal-icon"><i class="bi bi-credit-card-fill"></i></div>
              <h3>Confirmer le paiement</h3>
              <p class="text-muted mb-0">{{ podcast.title }}</p>
            </div>

            <div class="purchase-modal-body">
              <div class="purchase-detail-row">
                <span><i class="bi bi-mic-fill me-2"></i>Type</span>
                <strong>Podcast premium</strong>
              </div>
              <div v-if="podcast.author" class="purchase-detail-row">
                <span><i class="bi bi-person me-2"></i>Auteur</span>
                <strong>{{ podcast.author.name }}</strong>
              </div>
              <div class="purchase-detail-row">
                <span><i class="bi bi-credit-card me-2"></i>Méthode</span>
                <select v-model="paymentMethod" class="form-select form-select-sm w-auto">
                  <option value="mobile_money">Mobile Money</option>
                  <option value="card">Carte bancaire</option>
                  <option value="bank_transfer">Virement</option>
                </select>
              </div>
              <div class="purchase-detail-row highlight">
                <span><i class="bi bi-tag-fill me-2"></i>Total</span>
                <strong class="price">{{ podcast.price }} XOF</strong>
              </div>

              <div v-if="purchaseError" class="alert alert-danger mt-3 mb-0">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ purchaseError }}
              </div>

              <p class="small text-muted text-center mt-3 mb-0">
                <i class="bi bi-info-circle me-1"></i>
                Mode démo : le paiement est simulé et confirmé automatiquement.
              </p>

              <div class="purchase-modal-actions">
                <button
                  class="btn btn-outline-secondary"
                  @click="closePurchaseModal"
                  :disabled="purchasing"
                >
                  Annuler
                </button>
                <button
                  class="btn btn-warning"
                  @click="purchase"
                  :disabled="purchasing"
                >
                  <span v-if="purchasing" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-lock-fill me-2"></i>
                  Payer {{ podcast.price }} XOF
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useContentStore } from '../../stores/content'
import { useAuthStore } from '../../stores/auth'
import { initiatePayment, confirmPayment } from '../../services/api/payment'
import type { Content } from '../../stores/content'

const route = useRoute()
const router = useRouter()
const contentStore = useContentStore()
const authStore = useAuthStore()

const podcast = ref<Content | null>(null)
// Alias non typé utilisé dans le template pour accéder aux champs snake_case
// renvoyés par l'API DRF (media_url, content_body, requires_payment, is_premium)
const pData = computed<any>(() => podcast.value || {})
const loading = ref(true)
const error = ref('')
const purchasing = ref(false)
const purchaseError = ref('')
const showPurchaseModal = ref(false)
const purchaseSuccess = ref(false)
const paymentMethod = ref('mobile_money')

const openPurchaseModal = () => {
    if (!authStore.isAuthenticated) {
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }
    purchaseError.value = ''
    purchaseSuccess.value = false
    showPurchaseModal.value = true
}

const closePurchaseModal = async () => {
    showPurchaseModal.value = false
    if (purchaseSuccess.value) {
        purchaseSuccess.value = false
        await loadPodcast()
    }
}

const loadPodcast = async () => {
    loading.value = true
    error.value = ''

    try {
        const podcastId = parseInt(route.params.id as string)
        const data = await contentStore.getContent(podcastId)
        podcast.value = data
    } catch (err: any) {
        error.value = err.message || 'Failed to load podcast'
    } finally {
        loading.value = false
    }
}

const purchase = async () => {
    if (!podcast.value) return
    purchasing.value = true
    purchaseError.value = ''
    try {
        const price = (podcast.value as any).price ?? 0
        const payment = await initiatePayment({
            content_id: podcast.value.id,
            amount: price,
            currency: 'XOF',
            payment_method: paymentMethod.value,
        })
        await confirmPayment(payment.id)
        purchaseSuccess.value = true
    } catch (err: any) {
        purchaseError.value =
            err?.response?.data?.detail || err?.message || 'Échec du paiement'
    } finally {
        purchasing.value = false
    }
}

onMounted(() => {
    loadPodcast()
})
</script>

<style scoped>
.badge {
    padding: 0.5rem 1rem;
}

.audio-player {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
}

.podcast-content {
    font-size: 1.1rem;
    line-height: 1.8;
}

.podcast-content :deep(h2),
.podcast-content :deep(h3) {
    margin: 2rem 0 1rem;
}

.podcast-content :deep(p) {
    margin-bottom: 1.5rem;
}

.premium-gate {
    background: linear-gradient(160deg, #fff8eb 0%, #fff 100%);
    border-radius: 0.75rem;
}
.premium-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #FFD86B 0%, #F4A300 100%);
    border-radius: 50%;
    box-shadow: 0 8px 24px rgba(244, 163, 0, 0.35);
}
.premium-icon i { font-size: 2.5rem; color: #fff; }
.price-tag { line-height: 1; }

/* ═══ Purchase modal ═══ */
.purchase-modal-backdrop {
    position: fixed; inset: 0; z-index: 1080;
    background: rgba(0,0,0,.55);
    display: grid; place-items: center;
    padding: 1rem;
    animation: fadeIn .2s ease;
}
@keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
.purchase-modal {
    position: relative;
    width: 100%; max-width: 480px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,.25);
    overflow: hidden;
    animation: slideUp .25s ease;
}
@keyframes slideUp { from { transform: translateY(20px); opacity: 0 } to { transform: none; opacity: 1 } }
.purchase-modal-close {
    position: absolute; top: 12px; right: 12px;
    width: 34px; height: 34px;
    border: none; background: rgba(0,0,0,.05);
    border-radius: 50%; cursor: pointer;
    display: grid; place-items: center;
    transition: background .2s;
    z-index: 2;
}
.purchase-modal-close:hover { background: rgba(0,0,0,.12); }
.purchase-modal-header {
    padding: 32px 24px 16px;
    background: linear-gradient(160deg, #fff8eb 0%, #fff 100%);
}
.purchase-modal-icon {
    width: 64px; height: 64px; margin: 0 auto 12px;
    border-radius: 50%;
    display: grid; place-items: center;
    background: linear-gradient(135deg, #FFD86B 0%, #F4A300 100%);
    box-shadow: 0 6px 18px rgba(244,163,0,.4);
}
.purchase-modal-icon i { font-size: 1.8rem; color: #fff; }
.purchase-modal-body {
    padding: 20px 24px 24px;
}
.purchase-detail-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #f0eadf;
    font-size: .95rem;
    color: #5a6474;
}
.purchase-detail-row:last-of-type { border-bottom: none; }
.purchase-detail-row.highlight {
    margin-top: 8px;
    padding-top: 16px;
    border-top: 2px solid #f0eadf;
    font-size: 1.05rem;
}
.purchase-detail-row .price { color: #C14428; font-size: 1.4rem; font-weight: 800; }
.purchase-modal-actions {
    display: flex; gap: 12px; margin-top: 20px;
}
.purchase-modal-actions button { flex: 1; padding: 12px; font-weight: 600; }
.success-icon {
    width: 80px; height: 80px; margin: 0 auto 16px;
    border-radius: 50%;
    display: grid; place-items: center;
    background: rgba(39,102,75,.1);
}
.success-icon i { font-size: 3rem; color: #27664B; }
</style>