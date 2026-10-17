// export const API_URL = 'https://api.acathecpa.org';
// Overridable at build/dev time, e.g. VITE_API_URL=http://127.0.0.1:8001 for the e2e tests.
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
export const API_V1_PREFIX = '/api/v1';
export const API_BASE_URL = `${API_URL}${API_V1_PREFIX}`;