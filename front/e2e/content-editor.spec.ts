import { test, expect } from '@playwright/test'

/** The professor edits the article seeded by backend/tests/e2e_seed.py and adds a table. */
const TITLE = 'Les obligations fiscales'

test('editing an article shows its text, adds a table and updates the same article', async ({ page, browser }) => {
  await page.goto('/login')
  await page.locator('#identifier').fill('prof.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)

  await page.goto('/my-content')
  const cards = page.locator('.list-card')
  await expect(cards.filter({ hasText: TITLE })).toHaveCount(1)
  const before = await cards.count()
  await cards.filter({ hasText: TITLE }).locator('a[href^="/content/editor/"]').click()

  // Step 2: the saved text is in the editor.
  await page.locator('.btn-next').click()
  const editor = page.locator('.ProseMirror')
  await expect(editor).toContainText('Chaque entreprise déclare sa TVA chaque mois.')

  // Add a table at the end and fill two cells.
  await editor.click()
  await page.keyboard.press('ControlOrMeta+End')
  await page.getByRole('button', { name: 'Insérer un tableau' }).click()
  await expect(page.getByRole('toolbar', { name: 'Outils du tableau' })).toBeVisible()
  await page.keyboard.type('Impôt')
  await page.keyboard.press('Tab')
  await page.keyboard.type('Échéance')
  await page.getByRole('button', { name: '+ Ligne' }).click()
  await expect(editor.locator('table tr')).toHaveCount(4)

  await page.locator('.btn-save').last().click()
  await expect(page).toHaveURL(/\/my-content$/)
  await expect(cards).toHaveCount(before) // updated, not duplicated

  // The public article shows the table.
  const visitor = await browser.newPage()
  await visitor.goto('/articles')
  await visitor.getByText(TITLE).first().click()
  const table = visitor.locator('.article-content table')
  await expect(table).toBeVisible()
  await expect(table.locator('th').first()).toHaveText('Impôt')
  await expect(table.locator('th').nth(1)).toHaveText('Échéance')
  await visitor.close()
})
