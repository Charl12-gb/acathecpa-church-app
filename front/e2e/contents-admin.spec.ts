import { test, expect } from '@playwright/test'

/** An admin manages other authors' posts (seeded by backend/tests/e2e_seed.py). */
test('an admin publishes, edits and deletes posts of other authors', async ({ page }) => {
  await page.goto('/login')
  await page.locator('#identifier').fill('admin.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)

  await page.locator('.nav-item[href="/manage-contents"]').click()
  await expect(page.getByRole('heading', { name: 'Tous les contenus' })).toBeVisible()
  const row = (title: string) => page.getByRole('row', { name: new RegExp(title) })

  // Publish someone else's draft.
  await expect(row('Brouillon à modérer')).toContainText('Prof. Kossi Agbo')
  await row('Brouillon à modérer').getByLabel(/Statut de/).selectOption('published')
  await expect(row('Brouillon à modérer').getByRole('link', { name: 'Voir' })).toBeVisible()

  // Edit it: the text is loaded, saving brings back to this list.
  await row('Brouillon à modérer').getByRole('link', { name: 'Modifier' }).click()
  await page.locator('.btn-next').click()
  await expect(page.locator('.ProseMirror')).toContainText('Épisode en préparation.')
  await page.locator('.btn-save').last().click()
  await expect(page).toHaveURL(/\/manage-contents$/)

  // Delete it.
  await row('Brouillon à modérer').getByRole('button', { name: 'Supprimer' }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Supprimer' }).click()
  await expect(row('Brouillon à modérer')).toHaveCount(0)
})

test('a professor has no access to the posts of everyone', async ({ page }) => {
  await page.goto('/login')
  await page.locator('#identifier').fill('prof.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
  await page.goto('/manage-contents')
  await expect(page).toHaveURL(/\/dashboard$/)
})
