import { defineConfig, devices } from '@playwright/test'

/**
 * End-to-end tests against the real app:
 *   - Django on :8001 with a throw-away SQLite database (config.settings_e2e),
 *     rebuilt and seeded by backend/tests/e2e_seed.py before each run;
 *   - Vite on :5174, pointed at that backend through VITE_API_URL.
 * Neither port clashes with the usual dev servers (8000 / 5173).
 */
const PYTHON = '../appEnv/bin/python'

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:5174',
    locale: 'fr-FR',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `${PYTHON} tests/e2e_seed.py && ${PYTHON} manage.py runserver 127.0.0.1:8001 --noreload`,
      cwd: '../backend',
      env: { DJANGO_SETTINGS_MODULE: 'config.settings_e2e' },
      url: 'http://127.0.0.1:8001/',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: 'npx vite --port 5174 --strictPort',
      env: { VITE_API_URL: 'http://127.0.0.1:8001' },
      url: 'http://localhost:5174',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
})
