<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getAllCourses } from '../../services/api/course'
import type { Course } from '../../types/api' // Ensure Course type is imported

onMounted(async () => {
  new TypeIt("#typeit-text", {
    speed: 100,
    loop: true,
    deleteSpeed: 50,
    waitUntilVisible: true,
  })
  .type("Bienvenue à ACATHECPA")
  .pause(3500)
  .delete()
  .type("Welcome to ACATHECPA")
  .pause(3500)
  .delete()
  .type("Bienvenido a ACATHECPA")
  .pause(3500)
  .delete()
  .go();

  // Fetch featured courses
  try {
    const courses = await getAllCourses({ limit: 3, sortBy: 'created_at', sortOrder: 'desc' });
    featuredCourses.value = courses;
  } catch (error) {
    console.error("Failed to fetch featured courses:", error);
    // Optionally, set featuredCourses to an empty array or handle error state
    featuredCourses.value = [];
  }
})

// Sample data for courses and partners
const featuredCourses = ref<Course[]>([]);

const partners = ref([
  { name: 'Université de Paris', logo: 'https://placehold.co/200x100?text=Université+de+Paris' },
  { name: 'Microsoft', logo: 'https://placehold.co/200x100?text=Microsoft' },
  { name: 'IBM', logo: 'https://placehold.co/200x100?text=IBM' },
  { name: 'Orange', logo: 'https://placehold.co/200x100?text=Orange' },
])

// Testimonials
const testimonials = ref([
  {
    name: 'Sophie M.',
    position: 'Étudiante diplômée',
    content: 'La formation que j\'ai suivie à ACATHECPA m\'a permis de trouver rapidement un emploi dans mon domaine. Les professeurs sont excellents et le contenu très pratique.',
    avatar: 'https://placehold.co/100x100?text=SM'
  },
  {
    name: 'Thomas D.',
    position: 'Professionnel en reconversion',
    content: 'J\'ai changé de carrière grâce à ACATHECPA. La qualité des cours et le suivi personnalisé m\'ont donné confiance pour me lancer dans ce nouveau domaine.',
    avatar: 'https://placehold.co/100x100?text=TD'
  },
])
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section text-white py-5 position-relative" style="background: url('https://images.unsplash.com/photo-1589739907626-5bfb198dde73?crop=entropy&cs=tinysrgb&fit=crop&h=800&w=1600') no-repeat center center; background-size: cover;">
  
  <!-- Filtre sombre semi-transparent -->
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.4);"></div>

  <div class="container position-relative">
  <div class="row align-items-center">
    
    <!-- Texte -->
    <div class="col-lg-6">
      <h1 class="display-4 fw-bold mb-4 animate__animated animate__fadeInDown">
        <span id="typeit-text" class="ms-2"></span>
      </h1>
      <p class="lead mb-4 animate__animated animate__fadeInUp animate__delay-1s">
        Académie de Formation Théologico-Missionnaire Innovante - Conjuguant approche multidisciplinaire et ancrage contextuel Africain pour une formation pertinente.
      </p>
    </div>

    <!-- Image -->
    <div class="col-lg-6 d-none d-lg-block animate__animated animate__zoomIn animate__delay-3s">
      <img src="../../assets/logo.png" class="img-fluid rounded" alt="Hero Image">
    </div>

  </div>
</div>
</section>


    <!-- About Section -->
    <section class="py-5">
      <div class="container">
        <div class="row">
          <div class="col-lg-8 mx-auto text-center">
            <h2 class="fw-bold mb-4">À Propos de Nous</h2>
            <p class="lead mb-4">
              ACATHECPA est une Académie de Formation Théologico-Missionnaire Innovante, qui conjugue approche multidisciplinaire et ancrage contextuel Africain pour une formation pertinente.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Vision & Mission Section -->
    <section class="py-5 bg-light">
      <div class="container">
        <div class="row g-4">
          <div class="col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <h3 class="card-title fw-bold mb-3">Notre Vision</h3>
                <p class="card-text">
                  Devenir un centre d'excellence en formation et en recherche, intégrant Théologie et Missiologie Intégrée au Contexte pour former des leaders visionnaires, transformatifs et dévoués au service des communautés locales et au développement durable de l'Afrique.
                </p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <h3 class="card-title fw-bold mb-3">Notre Mission</h3>
                <p class="card-text">
                  Développer et mettre en œuvre des programmes de formations et de recherches pour les vocations ecclésiastiques et les ministères laïcs, afin de les équiper de connaissances approfondies en théologie et missiologie contextualisées, de les habiliter à exercer un leadership transformateur et servant dans leur environnement et dans leurs sphères d'influence.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Why Choose Us (Priorités Stratégiques) -->
    <section class="py-5">
      <div class="container">
        <h2 class="text-center fw-bold mb-5">Nos Priorités Stratégiques</h2>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-book-fill"></i>
                </div>
                <h5 class="card-title">Excellence Pracadémique</h5>
                <p class="card-text">Offrir des programmes de formation de pointe, pertinents au contexte, en Théologie et Missiologie, qui favorisent la rigueur académique et la pensée innovante.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-search"></i>
                </div>
                <h5 class="card-title">Recherche et Innovation Pédagogique</h5>
                <p class="card-text">Promouvoir la recherche et l'innovation en Théologie et Missiologie en lien avec les besoins du contexte, pour informer et enrichir nos programmes de formation.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-globe"></i>
                </div>
                <h5 class="card-title">Contextualisation Critique</h5>
                <p class="card-text">Favoriser une approche contextualisée de la Théologie et de la Missiologie, qui prend en compte les réalités socioculturelles, religieuses et pratiques des communautés.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Values Section -->
    <section class="py-5 bg-light">
      <div class="container">
        <h2 class="text-center fw-bold mb-5">Nos Valeurs</h2>
        <div class="row g-4">
          <div class="col-md-3 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-shield-check"></i>
                </div>
                <h5 class="card-title">Éthique</h5>
                <p class="card-text">Agir de manière intègre dans toutes nos activités et promouvoir une culture de la transparence.</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-check-circle"></i>
                </div>
                <h5 class="card-title">Redevabilité</h5>
                <p class="card-text">Agir de manière responsable et assumer la responsabilité de nos décisions et actions.</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-people"></i>
                </div>
                <h5 class="card-title">Inclusion</h5>
                <p class="card-text">Respecter la diversité des personnes, des cultures et des perspectives pour créer un environnement inclusif.</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-graph-up-arrow"></i>
                </div>
                <h5 class="card-title">Croissance</h5>
                <p class="card-text">Agir pour la croissance et le développement personnel et professionnel des étudiants et du personnel.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-heart"></i>
                </div>
                <h5 class="card-title">Compassion</h5>
                <p class="card-text">Agir pour soulager la souffrance et apporter réconfort et soutien aux personnes et aux communautés.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-star"></i>
                </div>
                <h5 class="card-title">Foi</h5>
                <p class="card-text">Agir avec une perspective spirituelle dans notre quotidien en vue de renforcer notre identité et notre mission.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 col-sm-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <div class="feature-icon text-white rounded-circle mb-3" style="background-color: #27664B;">
                  <i class="bi bi-houses"></i>
                </div>
                <h5 class="card-title">Communauté</h5>
                <p class="card-text">Agir avec la communauté pour identifier les besoins et développer des solutions qui contribuent à son développement.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Courses -->
    <section class="py-5">
      <div class="container">
        <div class="row mb-4">
          <div class="col-lg-8">
            <h2 class="fw-bold">Nos Formations</h2>
            <p class="lead">Découvrez nos programmes de formation théologico-missionnaire adaptés au contexte africain</p>
          </div>
          <div class="col-lg-4 text-lg-end">
            <RouterLink to="/browse-courses" class="btn btn-outline-primary">Voir tous les cours</RouterLink>
          </div>
        </div>
        <div class="row g-4">
          <div v-for="course in featuredCourses" :key="course.id" class="col-md-4">
            <div class="card h-100 shadow-sm">
              <img :src="course.image_url || 'https://placehold.co/600x400?text=Course'" class="card-img-top" :alt="course.title">
              <div class="card-body">
                <h5 class="card-title fw-bold">{{ course.title }}</h5>
                <p class="card-text">
                  {{ course.description.length > 50 ? course.description.slice(0, 100) + '...' : course.description }}
                </p>

                <div class="d-flex align-items-center mb-3">
                  <i class="bi bi-person-circle me-2"></i>
                  <small>{{ course.instructor?.name || 'Instructor N/A' }}</small>
                </div>
                <!-- Duration removed as per instructions -->
              </div>
              <div class="card-footer bg-white border-0">
                <RouterLink :to="`/course/${course.id}`" class="btn btn-primary w-100">Voir le cours</RouterLink> <!-- Updated link to course details -->
              </div>
            </div>
          </div>
        </div>
        <!-- Message if no courses are found -->
        <div v-if="featuredCourses.length === 0" class="text-center mt-4">
          <p>Aucun cours à afficher pour le moment. Veuillez revenir plus tard.</p>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="py-5 bg-light">
      <div class="container">
        <h2 class="text-center fw-bold mb-5">Ce que disent nos étudiants</h2>
        <div class="row g-4">
          <div v-for="(testimonial, index) in testimonials" :key="index" class="col-md-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <div class="d-flex mb-4">
                  <img :src="testimonial.avatar" class="rounded-circle me-3" width="60" height="60" :alt="testimonial.name">
                  <div>
                    <h5 class="mb-1">{{ testimonial.name }}</h5>
                    <p class="text-muted mb-0">{{ testimonial.position }}</p>
                  </div>
                </div>
                <p class="mb-0">{{ testimonial.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners Section -->
    <section class="py-5">
      <div class="container">
        <h2 class="text-center fw-bold mb-5">Nos Partenaires</h2>
        <div class="row g-4 align-items-center justify-content-center">
          <div v-for="(partner, index) in partners" :key="index" class="col-md-3 col-6 text-center">
            <img :src="partner.logo" :alt="partner.name" class="img-fluid partner-logo">
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-5 text-white" style="background-color: #27664B;">
      <div class="container text-center">
        <h2 class="fw-bold mb-4">Prêt à développer votre vocation?</h2>
        <p class="lead mb-4">Rejoignez ACATHECPA dès aujourd'hui et commencez votre parcours pour devenir un leader transformateur au service de l'Église et de la société.</p>
        <RouterLink to="/register" class="btn btn-light btn-lg px-5">S'inscrire maintenant</RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero-section {
  padding-top: 80px;
  padding-bottom: 80px;
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  font-size: 1.5rem;
}

.partner-logo {
  max-height: 80px;
  transition: transform 0.3s ease;
}

.partner-logo:hover {
  transform: scale(1.05);
}
</style>