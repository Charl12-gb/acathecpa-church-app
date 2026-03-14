<script setup lang="ts">
import { ref } from 'vue'
import { APP_NAME } from '../../config'

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
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Reset form after successful submission
    contactForm.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
    
    formSubmitted.value = true
  } catch (err: any) {
    error.value = err.message || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <!-- Contact Header -->
    <section class="text-white py-5" style="background-color: #27664B;">
      <div class="container text-center">
        <h1 class="display-4 fw-bold">Contactez-Nous</h1>
        <p class="lead">Nous sommes là pour répondre à toutes vos questions</p>
      </div>
    </section>

    <!-- Contact Information -->
    <section class="py-5">
      <div class="container">
        <div class="row g-5">
          <!-- Contact Form -->
          <div class="col-lg-7">
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h3 class="mb-4">Envoyez-nous un message</h3>
                
                <!-- Success Message -->
                <div v-if="formSubmitted" class="alert alert-success">
                  Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.
                </div>
                
                <!-- Error Message -->
                <div v-if="error" class="alert alert-danger">
                  {{ error }}
                </div>
                
                <!-- Contact Form -->
                <form v-if="!formSubmitted" @submit.prevent="submitForm">
                  <div class="mb-3">
                    <label for="name" class="form-label">Nom complet</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="name" 
                      v-model="contactForm.name"
                      required
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label for="email" class="form-label">Adresse email</label>
                    <input 
                      type="email" 
                      class="form-control" 
                      id="email" 
                      v-model="contactForm.email"
                      required
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label for="subject" class="form-label">Sujet</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="subject" 
                      v-model="contactForm.subject"
                      required
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label for="message" class="form-label">Message</label>
                    <textarea 
                      class="form-control" 
                      id="message" 
                      rows="5" 
                      v-model="contactForm.message"
                      required
                    ></textarea>
                  </div>
                  
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    <span v-if="loading">Envoi en cours...</span>
                    <span v-else>Envoyer le message</span>
                  </button>
                </form>
              </div>
            </div>
          </div>
          
          <!-- Contact Information -->
          <div class="col-lg-5">
            <div class="card bg-light border-0 mb-4">
              <div class="card-body p-4">
                <h3 class="mb-4">Nos coordonnées</h3>
                
                <div class="d-flex mb-4">
                  <div class="flex-shrink-0 me-3">
                    <div  style="background-color: #27664B;" class="text-white rounded-circle p-3">
                      <i class="bi bi-geo-alt"></i>
                    </div>
                  </div>
                  <div>
                    <h5>Adresse</h5>
                    <p class="mb-0">
                      123 Rue Principale<br>
                      75000 Paris, France
                    </p>
                  </div>
                </div>
                
                <div class="d-flex mb-4">
                  <div class="flex-shrink-0 me-3">
                    <div  style="background-color: #27664B;" class="text-white rounded-circle p-3">
                      <i class="bi bi-telephone"></i>
                    </div>
                  </div>
                  <div>
                    <h5>Téléphone</h5>
                    <p class="mb-0">+33 1 23 45 67 89</p>
                  </div>
                </div>
                
                <div class="d-flex mb-4">
                  <div class="flex-shrink-0 me-3">
                    <div  style="background-color: #27664B;" class="text-white rounded-circle p-3">
                      <i class="bi bi-envelope"></i>
                    </div>
                  </div>
                  <div>
                    <h5>Email</h5>
                    <p class="mb-0">info@acathecpa.com</p>
                  </div>
                </div>
                
                <div class="d-flex">
                  <div class="flex-shrink-0 me-3">
                    <div  style="background-color: #27664B;" class="text-white rounded-circle p-3">
                      <i class="bi bi-clock"></i>
                    </div>
                  </div>
                  <div>
                    <h5>Heures d'ouverture</h5>
                    <p class="mb-0">
                      Lundi - Vendredi: 9h - 18h<br>
                      Samedi: 9h - 13h<br>
                      Dimanche: Fermé
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Social Media -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h3 class="mb-4">Suivez-nous</h3>
                <div class="d-flex gap-3">
                  <a href="#" class="btn btn-outline-primary">
                    <i class="bi bi-facebook me-2"></i>Facebook
                  </a>
                  <a href="#" class="btn btn-outline-primary">
                    <i class="bi bi-twitter me-2"></i>Twitter
                  </a>
                  <a href="#" class="btn btn-outline-primary">
                    <i class="bi bi-instagram me-2"></i>Instagram
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Map Section (Placeholder) -->
    <section class="py-0">
      <div class="container-fluid p-0">
        <div class="map-container">
          <img src="https://placehold.co/1200x400?text=Google+Map" alt="Google Map" class="img-fluid w-100">
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.rounded-circle {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.map-container {
  height: 400px;
  overflow: hidden;
}
</style>