import { test, expect, type Page } from '@playwright/test'

/** A professor creates a PDF, an audio and a video post, then replaces a file while editing. */
const FILES = {
  pdf: { name: 'calendrier.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\n%test\n') },
  audio: { name: 'episode.mp3', mimeType: 'audio/mpeg', buffer: Buffer.from('ID3fake-audio') },
  video: { name: 'cours.mp4', mimeType: 'video/mp4', buffer: Buffer.from('fake-video') },
} as const

async function login(page: Page) {
  await page.goto('/login')
  await page.locator('#identifier').fill('prof.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
}

async function uploadIn(page: Page, file: (typeof FILES)[keyof typeof FILES]) {
  const upload = page.waitForResponse(r => r.url().includes('/api/v1/uploads/') && r.request().method() === 'POST')
  await page.locator('.file-uploader__input').setInputFiles(file)
  const response = await upload
  expect(response.status(), await response.text()).toBe(201)
  await expect(page.locator('.file-uploader')).toHaveClass(/has-file/)
}

for (const format of ['pdf', 'audio', 'video'] as const) {
  test(`a professor creates a ${format} post with its file`, async ({ page }) => {
    await login(page)
    await page.goto('/content/editor')
    await page.getByPlaceholder('Ex : Les fondamentaux de la comptabilité').fill(`Support ${format}`)
    await page.locator('label.format-chip', { has: page.locator(`input[value="${format}"]`) }).click()
    await page.locator('.btn-next').click()
    await uploadIn(page, FILES[format])

    const saved = page.waitForResponse(r => r.url().includes('/api/v1/contents/') && r.request().method() === 'POST')
    await page.locator('.btn-save').last().click()
    const body = await (await saved).json()
    expect(body.media_url).toContain(`/media/uploads/${format === 'pdf' ? 'document' : format}/`)
    await expect(page).toHaveURL(/\/my-content$/)
  })
}

test('a professor replaces the file of an existing post', async ({ page }) => {
  await login(page)
  await page.goto('/my-content')
  await page.locator('.list-card', { hasText: 'Support pdf' }).locator('a[href^="/content/editor/"]').click()
  await page.locator('.btn-next').click()
  await expect(page.locator('.file-uploader')).toHaveClass(/has-file/)
  await expect(page.locator('.file-uploader__actions').getByRole('button', { name: /Remplacer/ })).toBeVisible()
  await uploadIn(page, { ...FILES.pdf, name: 'calendrier-2027.pdf' })
  const saved = page.waitForResponse(r => /\/api\/v1\/contents\/\d+$/.test(r.url()) && r.request().method() === 'PUT')
  await page.locator('.btn-save').last().click()
  expect((await saved).status()).toBe(200)
})
