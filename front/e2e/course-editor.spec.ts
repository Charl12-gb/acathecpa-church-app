import { test, expect, type Page } from '@playwright/test'

/** A professor builds a course with files, rich text and a table, then reopens it. */
const TITLE = 'Audit interne - premiers pas'
const PNG = { name: 'couverture.png', mimeType: 'image/png', buffer: Buffer.from('89504e470d0a1a0a', 'hex') }
const MP4 = { name: 'introduction.mp4', mimeType: 'video/mp4', buffer: Buffer.from('fake-video') }

async function expectUploadOk(page: Page, action: () => Promise<void>) {
  const upload = page.waitForResponse(r => r.url().includes('/api/v1/uploads/') && r.request().method() === 'POST')
  await action()
  const response = await upload
  expect(response.status(), await response.text()).toBe(201)
}

test('a professor creates a course with an image, a video, rich text and a table, and finds it all when editing', async ({ page }) => {
  await page.goto('/login')
  await page.locator('#identifier').fill('prof.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)

  // Step 1: information and cover image.
  await page.goto('/course-editor')
  await page.locator('#course-title').fill(TITLE)
  await page.locator('.field', { hasText: 'Catégorie' }).locator('.ss-control').click()
  await page.getByRole('option', { name: 'Comptabilité' }).click()
  await page.locator('.field', { hasText: 'Prix (XOF)' }).locator('input').fill('5000')
  await expectUploadOk(page, () => page.locator('.file-uploader__input').first().setInputFiles(PNG))
  await page.getByRole('button', { name: /Suivant/ }).click()
  await page.getByRole('button', { name: /Suivant/ }).click()

  // Step 3, section 1: rich text with a table.
  const sections = page.locator('.section-block')
  await sections.nth(0).getByPlaceholder('Ex : Introduction aux concepts de base').fill('Les principes')
  const sectionEditor = sections.nth(0).locator('.ProseMirror').first()
  await sectionEditor.click()
  await page.keyboard.type("L'audit interne évalue les risques.")
  await sections.nth(0).getByRole('button', { name: 'Insérer un tableau' }).first().click()
  await page.keyboard.type('Risque')

  // A text lesson written with the editor (the form starts with one empty lesson).
  const lesson = sections.nth(0).locator('.lesson-card').first()
  await lesson.getByPlaceholder('Titre de la leçon').fill('La cartographie des risques')
  await lesson.locator('.ss-control').click()
  await page.getByRole('option', { name: 'Texte' }).click()
  await lesson.locator('.ProseMirror').click()
  await page.keyboard.type('On classe chaque risque par probabilité.')

  // Section 2: an uploaded video.
  await page.locator('.btn-add-section').click()
  await sections.nth(1).getByPlaceholder('Ex : Introduction aux concepts de base').fill('En vidéo')
  await sections.nth(1).locator('label.type-option', { hasText: 'Vidéo' }).click()
  await expectUploadOk(page, () => sections.nth(1).locator('.file-uploader__input').setInputFiles(MP4))

  await page.getByRole('button', { name: 'Enregistrer le cours' }).click()
  await expect(page).toHaveURL(/\/manage-courses$/)

  // Reopen: everything is loaded back.
  await page.locator('.course-card', { hasText: TITLE }).getByRole('link', { name: 'Modifier' }).click()
  await expect(page.locator('#course-title')).toHaveValue(TITLE)
  await expect(page.locator('.file-uploader').first()).toHaveClass(/has-file/)
  await page.getByRole('button', { name: /Suivant/ }).click()
  await page.getByRole('button', { name: /Suivant/ }).click()
  await expect(sections.nth(0).locator('.ProseMirror').first()).toContainText("L'audit interne évalue les risques.")
  await expect(sections.nth(0).locator('.ProseMirror table').first()).toContainText('Risque')
  await expect(sections.nth(0).locator('.lesson-card .ProseMirror')).toContainText('On classe chaque risque par probabilité.')
  await expect(sections.nth(1).locator('.file-uploader')).toHaveClass(/has-file/)
})
