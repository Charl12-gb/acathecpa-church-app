<script setup lang="ts">
import { ref } from 'vue'

const contactForm = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const formSubmitted = ref(false)
const loading = ref(false)
const error = ref('')

const submitForm = async () => {
  loading.value = true
  error.value = ''
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    contactForm.value = { name: '', email: '', subject: '', message: '' }
    formSubmitted.value = true
  } catch (err: any) {
    error.value = err.message || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="contact-page">

    <!-- ════════ HERO ════════ -->
    <section class="page-hero">
      <div class="hero-pattern"></div>
      <div class="hero-inner">
        <span class="hero-badge"><i class="bi bi-chat-dots-fill"></i> Contact</span>
        <h1 class="hero-title">Contactez-Nous</h1>
        <p class="hero-sub">
          Une question, un projet ou besoin d'informations ? Notre équipe est là pour vous accompagner.
        </p>
      </div>
    </section>

    <!-- ════════ MAIN ════════ -->
    <div class="container">

      <!-- Info cards row -->
      <div class="info-cards">
        <div class="info-card">
          <div class="info-icon"><i class="bi bi-geo-alt-fill"></i></div>
          <h4>Adresse</h4>
          <p>123 Rue Principale<br>75000 Paris, France</p>
        </div>
        <div class="info-card">
          <div class="info-icon phone"><i class="bi bi-telephone-fill"></i></div>
          <h4>Téléphone</h4>
          <p>+33 1 23 45 67 89</p>
        </div>
        <div class="info-card">
          <div class="info-icon email"><i class="bi bi-envelope-fill"></i></div>
          <h4>Email</h4>
          <p>info@acathecpa.com</p>
        </div>
        <div class="info-card">
          <div class="info-icon hours"><i class="bi bi-clock-fill"></i></div>
          <h4>Horaires</h4>
          <p>Lun–Ven : 9h – 18h<br>Sam : 9h – 13h</p>
        </div>
      </div>

      <!-- Two columns: Form + Sidebar -->
      <div class="contact-grid">

        <!-- Form -->
        <div class="form-card">
          <div class="form-header">
            <h2>Envoyez-nous un message</h2>
            <p>Remplissez le formulaire ci-dessous et nous vous répondrons dans les plus brefs délais.</p>
          </div>

          <!-- Success -->
          <div v-if="formSubmitted" class="success-msg">
            <div class="success-icon"><i class="bi bi-check-circle-fill"></i></div>
            <h3>Message envoyé !</h3>
            <p>Merci pour votre message. Nous vous répondrons très bientôt.</p>
            <button class="btn-reset" @click="formSubmitted = false">
              <i class="bi bi-pencil-square"></i> Envoyer un autre message
            </button>
          </div>

          <!-- Error -->
          <div v-if="error" class="error-msg">
            <i class="bi bi-exclamation-triangle-fill"></i> {{ error }}
          </div>

          <!-- Form fields -->
          <form v-if="!formSubmitted" @submit.prevent="submitForm" class="contact-form">
            <div class="form-row">
              <div class="form-group">
                <label for="name">Nom complet</label>
                <div class="input-wrap">
                  <i class="bi bi-person"></i>
                  <input id="name" type="text" v-model="contactForm.name" placeholder="Jean Dupont" required />
                </div>
              </div>
              <div class="form-group">
                <label for="email">Adresse email</label>
                <div class="input-wrap">
                  <i class="bi bi-envelope"></i>
                  <input id="email" type="email" v-model="contactForm.email" placeholder="jean@exemple.com" required />
                </div>
              </div>
            </div>
            <div class="form-group">
              <label for="subject">Sujet</label>
              <div class="input-wrap">
                <i class="bi bi-tag"></i>
                <input id="subject" type="text" v-model="contactForm.subject" placeholder="Objet de votre message" required />
              </div>
            </div>
            <div class="form-group">
              <label for="message">Message</label>
              <textarea id="message" v-model="contactForm.message" rows="5" placeholder="Écrivez votre message ici…" required></textarea>
            </div>
            <button type="submit" class="btn-submit" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              <i v-else class="bi bi-send-fill"></i>
              {{ loading ? 'Envoi en cours…' : 'Envoyer le message' }}
            </button>
          </form>
        </div>

        <!-- Sidebar -->
        <div class="sidebar">
          <!-- Social -->
          <div class="sidebar-card">
            <h3>Suivez-nous</h3>
            <p class="sidebar-desc">Restez connecté avec ACATHECPA sur les réseaux sociaux.</p>
            <div class="social-links">
              <a href="#" class="social-btn facebook" aria-label="Facebook">
                <i class="bi bi-facebook"></i>
              </a>
              <a href="#" class="social-btn twitter" aria-label="Twitter">
                <i class="bi bi-twitter-x"></i>
              </a>
              <a href="#" class="social-btn instagram" aria-label="Instagram">
                <i class="bi bi-instagram"></i>
              </a>
              <a href="#" class="social-btn youtube" aria-label="YouTube">
                <i class="bi bi-youtube"></i>
              </a>
            </div>
          </div>

          <!-- FAQ hint -->
          <div class="sidebar-card highlight">
            <div class="highlight-icon"><i class="bi bi-question-circle-fill"></i></div>
            <h3>Questions fréquentes</h3>
            <p class="sidebar-desc">Consultez notre FAQ pour des réponses rapides aux questions courantes sur les inscriptions, cours et certifications.</p>
          </div>
        </div>
      </div>

      <!-- Map -->
      <div class="map-section">
        <div class="map-header">
          <i class="bi bi-pin-map-fill"></i>
          <h3>Notre localisation</h3>
        </div>
        <div class="map-container">
          <img src="https://placehold.co/1200x350/e7e0d4/5a6474?text=Carte+Google+Maps" alt="Localisation ACATHECPA" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
$primary:    #C14428;
$secondary:  #1B7A78;
$accent:     #F4A300;
$success:    #27664B;
$neutral:    #FFF8EE;
$dark:       #1a1a1a;
$text:       #2C2C2C;
$text-light: #5a6474;
$border:     #e7e0d4;
$radius:     12px;
$radius-lg:  18px;
$shadow-sm:  0 2px 8px rgba(0,0,0,.05);
$shadow:     0 4px 20px rgba(0,0,0,.07);
$shadow-lg:  0 8px 40px rgba(0,0,0,.10);

.contact-page {
  min-height: 100vh;
  background: $neutral;
}

/* ═══════ HERO ═══════ */
.page-hero {
  position: relative;
  background: linear-gradient(160deg, $success 0%, darken($secondary, 10%) 100%);
  padding: 110px 24px 60px;
  text-align: center;
  overflow: hidden;
}
.hero-pattern {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E");
  z-index: 0;
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(#fff, .14);
  color: #fff;
  font-size: .78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: 18px;
  backdrop-filter: blur(4px);
}
.hero-title {
  font-size: 2.6rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px;
  line-height: 1.15;
}
.hero-sub {
  font-size: 1.05rem;
  color: rgba(#fff, .82);
  margin: 0;
  line-height: 1.6;
}

/* ═══════ CONTAINER ═══════ */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 60px;
}

/* ═══════ INFO CARDS ═══════ */
.info-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: -40px;
  position: relative;
  z-index: 2;
  margin-bottom: 40px;
}
.info-card {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  padding: 24px 20px;
  text-align: center;
  box-shadow: $shadow;
  transition: transform .25s, box-shadow .25s;
  &:hover { transform: translateY(-3px); box-shadow: $shadow-lg; }
  h4 {
    font-size: .92rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 6px;
  }
  p {
    font-size: .82rem;
    color: $text-light;
    margin: 0;
    line-height: 1.5;
  }
}
.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  margin: 0 auto 14px;
  font-size: 1.15rem;
  color: #fff;
  background: $secondary;
  &.phone { background: $primary; }
  &.email { background: $accent; color: $dark; }
  &.hours { background: $success; }
}

/* ═══════ CONTACT GRID ═══════ */
.contact-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 28px;
  margin-bottom: 40px;
}

/* ── Form Card ── */
.form-card {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  padding: 36px;
  box-shadow: $shadow;
}
.form-header {
  margin-bottom: 28px;
  h2 {
    font-size: 1.4rem;
    font-weight: 800;
    color: $dark;
    margin: 0 0 8px;
  }
  p {
    font-size: .9rem;
    color: $text-light;
    margin: 0;
  }
}
.contact-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  label {
    font-size: .82rem;
    font-weight: 600;
    color: $text;
  }
}
.input-wrap {
  position: relative;
  i {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #b0a898;
    font-size: .88rem;
  }
  input {
    width: 100%;
    padding: 12px 14px 12px 40px;
    border-radius: 10px;
    border: 1px solid $border;
    background: $neutral;
    font-size: .9rem;
    color: $text;
    outline: none;
    transition: border-color .2s, box-shadow .2s;
    &::placeholder { color: #c4b9a8; }
    &:focus {
      border-color: $secondary;
      box-shadow: 0 0 0 3px rgba($secondary, .1);
      background: #fff;
    }
  }
}
textarea {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid $border;
  background: $neutral;
  font-size: .9rem;
  color: $text;
  resize: vertical;
  min-height: 120px;
  outline: none;
  font-family: inherit;
  transition: border-color .2s, box-shadow .2s;
  &::placeholder { color: #c4b9a8; }
  &:focus {
    border-color: $secondary;
    box-shadow: 0 0 0 3px rgba($secondary, .1);
    background: #fff;
  }
}
.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 32px;
  border-radius: 10px;
  border: none;
  background: $secondary;
  color: #fff;
  font-weight: 700;
  font-size: .95rem;
  cursor: pointer;
  transition: all .25s;
  align-self: flex-start;
  &:hover:not(:disabled) { background: darken($secondary, 8%); transform: translateY(-1px); box-shadow: 0 4px 16px rgba($secondary, .3); }
  &:disabled { opacity: .65; cursor: not-allowed; }
}
.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(#fff, .3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Success */
.success-msg {
  text-align: center;
  padding: 40px 20px;
}
.success-icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: rgba($success, .1);
  display: grid;
  place-items: center;
  margin: 0 auto 18px;
  i { font-size: 1.8rem; color: $success; }
}
.success-msg h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: $dark;
  margin: 0 0 8px;
}
.success-msg p {
  font-size: .92rem;
  color: $text-light;
  margin: 0 0 24px;
}
.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 8px;
  border: 1px solid $border;
  background: #fff;
  color: $text;
  font-weight: 600;
  font-size: .85rem;
  cursor: pointer;
  transition: .2s;
  &:hover { border-color: $secondary; color: $secondary; }
}
/* Error */
.error-msg {
  padding: 14px 18px;
  border-radius: 10px;
  background: rgba($primary, .06);
  border: 1px solid rgba($primary, .15);
  color: $primary;
  font-size: .88rem;
  font-weight: 600;
  margin-bottom: 18px;
  i { margin-right: 6px; }
}

/* ── Sidebar ── */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.sidebar-card {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  padding: 28px 24px;
  box-shadow: $shadow-sm;
  h3 {
    font-size: 1.08rem;
    font-weight: 700;
    color: $dark;
    margin: 0 0 8px;
  }
}
.sidebar-desc {
  font-size: .85rem;
  color: $text-light;
  line-height: 1.55;
  margin: 0 0 18px;
}
.social-links {
  display: flex;
  gap: 10px;
}
.social-btn {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.1rem;
  color: #fff;
  text-decoration: none;
  transition: transform .2s, box-shadow .2s;
  &:hover { transform: translateY(-2px); box-shadow: $shadow; }
  &.facebook { background: #1877F2; }
  &.twitter { background: #14171A; }
  &.instagram { background: linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }
  &.youtube { background: #FF0000; }
}
.sidebar-card.highlight {
  background: linear-gradient(135deg, rgba($accent, .08), rgba($accent, .03));
  border-color: rgba($accent, .2);
}
.highlight-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: rgba($accent, .15);
  display: grid;
  place-items: center;
  margin-bottom: 14px;
  i { font-size: 1.2rem; color: darken($accent, 10%); }
}

/* ═══════ MAP ═══════ */
.map-section {
  background: #fff;
  border-radius: $radius-lg;
  border: 1px solid $border;
  overflow: hidden;
  box-shadow: $shadow-sm;
}
.map-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 24px;
  border-bottom: 1px solid $border;
  i { font-size: 1.1rem; color: $primary; }
  h3 {
    font-size: 1rem;
    font-weight: 700;
    color: $dark;
    margin: 0;
  }
}
.map-container {
  height: 320px;
  overflow: hidden;
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

/* ═══════ RESPONSIVE ═══════ */
@media (max-width: 992px) {
  .info-cards { grid-template-columns: repeat(2, 1fr); }
  .contact-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .page-hero { padding: 90px 18px 42px; }
  .hero-title { font-size: 1.8rem; }
  .info-cards { grid-template-columns: 1fr 1fr; gap: 14px; margin-top: -30px; }
  .form-card { padding: 24px 18px; }
  .form-row { grid-template-columns: 1fr; }
  .map-container { height: 220px; }
}
</style>