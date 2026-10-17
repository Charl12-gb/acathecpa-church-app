import { test, expect, type Page } from '@playwright/test'

/**
 * Professor side, on the data seeded by backend/tests/e2e_seed.py:
 *   - "Fiscalité des entreprises": free, 1 quiz section (2 lessons + "Quiz TVA"),
 *     Koffi Mensah enrolled at 33 % with one failed quiz attempt;
 *   - "Brouillon vide": draft without any content;
 *   - "Comptabilité OHADA - Les fondamentaux": the student journey's course.
 */
const API = 'http://127.0.0.1:8001/api/v1'
const FISC = 'Fiscalité des entreprises'
const VIDEO_URL = 'https://www.youtube.com/watch?v=Qm7lKsWbPDk'

async function loginAsProfessor(page: Page) {
  await page.goto('/login')
  await page.locator('#identifier').fill('prof.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
}

const courseCard = (page: Page, title: string) => page.locator('.course-card', { hasText: title })

async function openEditorContentStep(page: Page, title: string) {
  await page.goto('/manage-courses')
  await courseCard(page, title).getByRole('link', { name: 'Modifier' }).click()
  await expect(page.locator('#course-title')).toHaveValue(title) // course loaded
  await page.getByRole('button', { name: /Suivant/ }).click()
  await page.getByRole('button', { name: /Suivant/ }).click()
}

test.beforeEach(async ({ page }) => {
  page.on('dialog', dialog => dialog.accept())
})

test('saving a course keeps its quiz and stores video lessons as videos', async ({ page }) => {
  await loginAsProfessor(page)
  await expect(page.getByText('Certificats délivrés')).toBeVisible()

  await openEditorContentStep(page, FISC)
  const quizSummary = page.getByText('« Quiz TVA » : 1 question(s)')
  await expect(quizSummary).toBeVisible()

  // Add a video lesson to the quiz section, then save the whole course.
  await page.getByRole('button', { name: 'Ajouter une leçon' }).click()
  const newLesson = page.locator('.lesson-card').last()
  await newLesson.getByPlaceholder('Titre de la leçon').fill('La TVA en vidéo')
  await newLesson.getByPlaceholder('URL de la vidéo').fill(VIDEO_URL)
  await page.getByRole('button', { name: 'Enregistrer le cours' }).click()
  await expect(page).toHaveURL(/\/manage-courses$/)

  // The quiz survived the save...
  await openEditorContentStep(page, FISC)
  await expect(quizSummary).toBeVisible()

  // ...and the lesson is stored as a real video.
  const token = await page.evaluate(() => localStorage.getItem('token'))
  const courses = await (await page.request.get(`${API}/courses/instructor/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })).json()
  const fisc = courses.find((c: any) => c.title === FISC)
  const detail = await (await page.request.get(`${API}/courses/${fisc.id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })).json()
  const lesson = detail.sections.flatMap((s: any) => s.lessons).find((l: any) => l.title === 'La TVA en vidéo')
  expect(lesson.video_url).toBe(VIDEO_URL)
  expect(lesson.content_body).toBeNull()
})

test("the professor follows a course's students and cannot delete a course they joined", async ({ page }) => {
  await loginAsProfessor(page)
  await page.goto('/manage-courses')
  await expect(courseCard(page, FISC).getByText('1 étudiant(s)')).toBeVisible()

  await courseCard(page, FISC).getByRole('link', { name: 'Étudiants' }).click()
  await expect(page.getByRole('heading', { name: `Étudiants · ${FISC}` })).toBeVisible()
  const row = page.getByRole('row', { name: /Koffi Mensah/ })
  await expect(row).toContainText('koffi.e2e@acathecpa.test')
  await expect(row).toContainText('(1 essai)')
  await expect(page.getByText('Inscrits').locator('..')).toContainText('1')

  await page.goto('/manage-courses')
  await courseCard(page, FISC).getByRole('button', { name: 'Supprimer' }).click()
  await expect(page.locator('.notice-banner')).toContainText('ne peut pas être supprimé')
  await expect(courseCard(page, FISC)).toBeVisible()
})

test('an empty draft cannot be published but can be deleted', async ({ page }) => {
  await loginAsProfessor(page)
  await page.goto('/manage-courses')
  const card = courseCard(page, 'Brouillon vide')

  await card.locator('.status-select .ss-control').click()
  await card.getByRole('option', { name: 'Publié' }).click()
  await expect(page.locator('.notice-banner')).toContainText('Ajoutez au moins une leçon ou un quiz')
  await expect(card.locator('.thumb-badge')).toHaveText('Brouillon')

  await card.getByRole('button', { name: 'Supprimer' }).click()
  await expect(card).toHaveCount(0)
})

test("the professor's biography appears on the course page", async ({ page, browser }) => {
  const bio = 'Expert-comptable diplômé, quinze ans de missions d\'audit en zone OHADA.'
  await loginAsProfessor(page)
  await page.goto('/profile')
  await page.locator('#teacher-bio').fill(bio)
  await page.locator('#teacher-skills').fill('OHADA, Audit, TVA')
  await page.getByRole('button', { name: 'Enregistrer le profil formateur' }).click()
  await expect(page.getByText('Profil formateur enregistré.')).toBeVisible()

  const visitor = await browser.newPage()
  await visitor.goto('/browse-courses')
  await visitor.getByRole('link', { name: FISC }).first().click()
  const card = visitor.locator('.instructor-card')
  await expect(card).toContainText('Prof. Aminata Diallo')
  await expect(card).toContainText('Comptabilité et fiscalité')
  await expect(card).toContainText(bio)
  await expect(card).toContainText('Audit')
  await visitor.close()
})
