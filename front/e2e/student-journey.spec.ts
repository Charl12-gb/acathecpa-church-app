import { test, expect, type Page } from '@playwright/test'

/**
 * A new student goes through the whole journey in the browser, on the course
 * seeded by backend/tests/e2e_seed.py ("Comptabilité OHADA - Les fondamentaux",
 * 15 000 XOF, 3 lessons + 1 quiz of 2 questions, 2 attempts).
 */
const COURSE = 'Comptabilité OHADA - Les fondamentaux'
const STUDENT = {
  name: 'Awa Koné',
  email: `awa.kone.${Date.now()}@acathecpa.test`,
  phone: `+22507${String(Date.now()).slice(-8)}`,
  password: 'Password123!',
}

async function completeLesson(page: Page, title: string) {
  await expect(page.getByRole('heading', { level: 2, name: title })).toBeVisible()
  await page.getByRole('button', { name: 'Marquer la leçon comme terminée et continuer' }).click()
}

test('a student signs up, pays, follows the course, passes the quiz and gets a verifiable certificate', async ({ page, browser }) => {
  // 1. Sign-up
  await page.goto('/register')
  await page.locator('#name').fill(STUDENT.name)
  await page.locator('#email').fill(STUDENT.email)
  await page.locator('#phone').fill(STUDENT.phone)
  await page.locator('#birthdate').fill('1998-04-12')
  await page.locator('#password').fill(STUDENT.password)
  await page.locator('#confirm_password').fill(STUDENT.password)
  await page.locator('#terms').check()
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/login$/)

  // 2. Login
  await page.locator('#identifier').fill(STUDENT.email)
  await page.locator('#password').fill(STUDENT.password)
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)

  // 3. Catalogue -> course page
  await page.locator('.nav-item', { hasText: 'Explorer les cours' }).click()
  await page.getByRole('link', { name: COURSE }).first().click()
  await expect(page).toHaveURL(/\/course\/\d+$/)
  // Not enrolled yet: lessons are listed, no content is reachable.
  await expect(page.getByText('Le plan comptable').first()).toBeVisible()

  // 4. Simulated payment + enrollment
  await page.getByRole('button', { name: "Payer et s'inscrire" }).click()
  await expect(page.getByText('Paiement & inscription')).toBeVisible()
  await page.getByRole('button', { name: 'Payer 15000 XOF' }).click()
  await expect(page.getByText('Inscription réussie !')).toBeVisible()
  await page.locator('.enroll-success-state button').click()

  // 5. Lessons
  await page.getByRole('button', { name: 'Continuer le cours' }).click()
  await completeLesson(page, 'Le plan comptable')
  await completeLesson(page, 'Les journaux')
  await completeLesson(page, 'Lire un bilan')
  await expect(page.getByText('75% complété')).toBeVisible()

  // 6. Quiz: first attempt fails...
  await expect(page.getByRole('heading', { name: 'Quiz : Quiz : le bilan' })).toBeVisible()
  await expect(page.getByText('Tentatives : 0 / 2')).toBeVisible()
  await page.getByRole('button', { name: 'Commencer le quiz' }).click()
  await page.getByLabel('À droite').check()
  await page.getByLabel('Vrai').check()
  await page.getByRole('button', { name: 'Soumettre mes réponses' }).click()
  await expect(page.getByText('Score : 0 % (0 / 3 points)')).toBeVisible()
  await expect(page.getByText('Échoué')).toBeVisible()

  // ...the second one passes.
  await page.getByRole('button', { name: 'Repasser le quiz' }).click()
  await page.getByLabel('À gauche').check()
  await page.getByLabel('Faux').check()
  await page.getByRole('button', { name: 'Soumettre mes réponses' }).click()
  await expect(page.getByText('Score : 100 % (3 / 3 points)')).toBeVisible()
  await expect(page.getByText('Réussi', { exact: true })).toBeVisible()
  await expect(page.getByText('100% complété')).toBeVisible()
  // Both attempts used: no third try.
  await expect(page.getByRole('button', { name: 'Repasser le quiz' })).toHaveCount(0)

  // 7. Certificate
  await page.getByRole('link', { name: 'Obtenir mon certificat' }).click()
  await page.getByRole('button', { name: "Vérifier l'éligibilité au certificat" }).click()
  await page.getByRole('button', { name: 'Voir le certificat' }).click()
  await expect(page).toHaveURL(/\/certificates$/)
  const codeLink = page.getByRole('link', { name: /CERT-[0-9A-F]{10}/ })
  const code = (await codeLink.innerText()).trim()

  // 8. Anyone, without an account, can verify it.
  const visitor = await browser.newPage()
  await visitor.goto(`/certificates/verify/${code}`)
  await expect(visitor.getByText('Certificat authentique')).toBeVisible()
  await expect(visitor.getByText(STUDENT.name)).toBeVisible()
  await expect(visitor.getByText(COURSE)).toBeVisible()
  await visitor.close()
})

test('a visitor can browse the catalogue but not open lessons', async ({ page }) => {
  await page.goto('/browse-courses')
  await page.getByRole('link', { name: COURSE }).first().click()
  await expect(page).toHaveURL(/\/course\/\d+$/)
  // The outline is public...
  await expect(page.getByText('Le plan comptable').first()).toBeVisible()
  await expect(page.getByRole('button', { name: "Se connecter pour s'inscrire" })).toBeVisible()
  // ...the lesson viewer is not.
  const courseId = page.url().split('/').pop()
  await page.goto(`/lesson/${courseId}/1`)
  await expect(page).toHaveURL(/\/login$/)
})

test('an unknown certificate code is rejected', async ({ page }) => {
  await page.goto('/certificates/verify/CERT-0000000000')
  await expect(page.getByText('Aucun certificat ne correspond au code « CERT-0000000000 »')).toBeVisible()
})
