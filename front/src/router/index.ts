import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Public Pages
import HomePage from '../views/public/HomePage.vue'
import ContactPage from '../views/public/ContactPage.vue'
import LoginPage from '../views/auth/LoginPage.vue'
import RegisterPage from '../views/auth/RegisterPage.vue'
import ForgotPasswordPage from '../views/auth/ForgotPasswordPage.vue' // Added
import ResetPasswordPage from '../views/auth/ResetPasswordPage.vue' // Added
import ArticlesPage from '../views/public/ArticlesPage.vue'
import PodcastsPage from '../views/public/PodcastsPage.vue'
import ArticleDetailPage from '../views/public/ArticleDetailPage.vue'
import PodcastDetailPage from '../views/public/PodcastDetailPage.vue'

// Private Pages
import DashboardPage from '../views/dashboard/DashboardPage.vue'
import ProfilePage from '../views/dashboard/ProfilePage.vue'
import MyContentPage from '../views/dashboard/content/MyContentPage.vue'
import ContentEditorPage from '../views/dashboard/content/ContentEditorPage.vue'

// Student Pages
import StudentCoursesPage from '../views/dashboard/student/CoursesPage.vue'
import StudentCertificatesPage from '../views/dashboard/student/CertificatesPage.vue'
import BrowseCoursesPage from '../views/dashboard/student/BrowseCoursesPage.vue'
import CourseDetailPage from '../views/dashboard/student/CourseDetailPage.vue'
import LessonViewer from '../views/dashboard/student/LessonViewer.vue'

// Professor Pages
import ProfessorCoursesPage from '../views/dashboard/professor/CoursesPage.vue'
import CourseEditorPage from '../views/dashboard/professor/CourseEditorPage.vue'
import LiveSessionPage from '../views/dashboard/professor/LiveSessionPage.vue'
import LiveListe from '../views/dashboard/professor/LiveListe.vue'

// Admin Pages
import AdminProfessorsPage from '../views/dashboard/admin/ProfessorsPage.vue'
import ProfessorFormPage from '../views/dashboard/admin/ProfessorFormPage.vue'
import AdminUsersPage from '../views/dashboard/admin/UsersPage.vue'
import UserFormPage from '../views/dashboard/admin/UserFormPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Public routes
    { path: '/', name: 'home', component: HomePage },
    { path: '/contact', name: 'contact', component: ContactPage },
    { path: '/login', name: 'login', component: LoginPage, meta: { requiresAuth: false } },
    { path: '/register', name: 'register', component: RegisterPage, meta: { requiresAuth: false } },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPasswordPage,
      meta: { requiresAuth: false }
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPasswordPage,
      meta: { requiresAuth: false }
    },
    { path: '/articles', name: 'articles', component: ArticlesPage },
    { path: '/podcasts', name: 'podcasts', component: PodcastsPage },
    { path: '/articles/:id', name: 'article-detail', component: ArticleDetailPage },
    { path: '/podcasts/:id', name: 'podcast-detail', component: PodcastDetailPage },
    
    // Protected routes
    { 
      path: '/dashboard', 
      name: 'dashboard', 
      component: DashboardPage,
      meta: { requiresAuth: true }
    },
    { 
      path: '/profile', 
      name: 'profile', 
      component: ProfilePage,
      meta: { requiresAuth: true }
    },
    { 
      path: '/my-content', 
      name: 'my-content', 
      component: MyContentPage,
      meta: { requiresAuth: true }
    },
    { 
      path: '/content/editor/:id?', 
      name: 'content-editor', 
      component: ContentEditorPage,
      meta: { requiresAuth: true }
    },
    
    // Student routes
    { 
      path: '/my-courses', 
      name: 'student-courses', 
      component: StudentCoursesPage,
      meta: { requiresAuth: true, role: 'student' }
    },
    { 
      path: '/course/:id', 
      name: 'course-detail', 
      component: CourseDetailPage,
      meta: { requiresAuth: true, role: 'student' }
    },
    { 
      path: '/certificates', 
      name: 'certificates', 
      component: StudentCertificatesPage,
      meta: { requiresAuth: true, role: 'student' }
    },
    { 
      path: '/browse-courses', 
      name: 'browse-courses', 
      component: BrowseCoursesPage,
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/lesson/:courseId/:lessonId',
      name: 'lesson-viewer',
      component: LessonViewer,
      meta: { requiresAuth: true, role: 'student' }
    },
    
    // Professor routes
    { 
      path: '/manage-courses', 
      name: 'professor-courses', 
      component: ProfessorCoursesPage,
      meta: { requiresAuth: true, role: 'professor' }
    },
    { 
      path: '/course-editor/:id?', 
      name: 'course-editor', 
      component: CourseEditorPage,
      meta: { requiresAuth: true, role: 'professor' }
    },
    {
      path: '/live-sessions',
      name: 'live-sessions',
      component: LiveListe,
      meta: { requiresAuth: true, role: ['professor', 'admin', 'super_admin'] }
    },
    {
      path: '/live-session/:id?',
      name: 'live-session',
      component: LiveSessionPage,
      meta: { requiresAuth: true, role: ['professor', 'admin', 'super_admin'] }
    },
    
    // Admin routes
    { 
      path: '/manage-professors', 
      name: 'manage-professors', 
      component: AdminProfessorsPage,
      meta: { requiresAuth: true, role: ['admin', 'super_admin'] }
    },
    { 
      path: '/professor-form/:id?', 
      name: 'professor-form', 
      component: ProfessorFormPage,
      meta: { requiresAuth: true, role: ['admin', 'super_admin'] }
    },
    { 
      path: '/manage-users', 
      name: 'manage-users', 
      component: AdminUsersPage,
      meta: { requiresAuth: true, role: ['admin', 'super_admin'] }
    },
    { 
      path: '/user-form/:id?', 
      name: 'user-form', 
      component: UserFormPage,
      meta: { requiresAuth: true, role: ['admin', 'super_admin'] }
    },
    
    // Catch-all redirect to home
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiredRole = to.meta.role

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiredRole && !authStore.hasRole(requiredRole)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router