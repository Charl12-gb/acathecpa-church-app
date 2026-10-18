// API URL - Pointing to the FastAPI backend
export const API_URL = 'http://localhost:8000/api/v1'

// App constants
export const APP_NAME = 'ACATHECPA'
export const APP_DESCRIPTION = 'Centre de formation professionnelle'

// Color System
export const COLORS = {
  primary: '#2c3e50',    // Dark blue
  secondary: '#3498db',  // Light blue
  accent: '#e74c3c',     // Red
  success: '#2ecc71',    // Green
  warning: '#f39c12',    // Orange
  error: '#c0392b',      // Dark red
  neutral: '#ecf0f1'     // Light gray
}

// Organisation details shown in the footer and the legal pages.
// Fill in the empty fields: an empty value is simply not displayed.
export const ORGANISATION = {
  name: 'ACATHECPA',
  legalName: '',          // raison sociale complète, ex. « Association ACATHECPA »
  registration: '',       // numéro d'immatriculation (RCCM, IFU…)
  address: '',            // adresse postale
  phone: '',              // ex. « +229 01 00 00 00 00 »
  email: 'info@acathecpa.com',
  privacyEmail: 'info@acathecpa.com', // adresse pour les demandes sur les données personnelles
  host: '',               // hébergeur du site : nom et adresse
  socialLinks: [] as Array<{ label: string; icon: string; url: string }>, // ex. { label: 'Facebook', icon: 'bi-facebook', url: 'https://…' }
  legalUpdatedAt: '18 octobre 2026',
}
