import { test, expect, type Page } from '@playwright/test'

/**
 * Back office, on the data seeded by backend/tests/e2e_seed.py:
 *   - Admin Plateforme (admin) and Super Admin (super_admin);
 *   - Nouvel Inscrit: a student without any history;
 *   - Yao Adjo: a student who paid for and joined the OHADA course.
 */
async function login(page: Page, email: string) {
  await page.goto('/login')
  await page.locator('#identifier').fill(email)
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
}

const row = (page: Page, name: string) => page.getByRole('row', { name: new RegExp(name) })

test('an admin edits a user, protects history by deactivating, and cannot touch a super admin', async ({ page }) => {
  await login(page, 'admin.e2e@acathecpa.test')
  await page.goto('/manage-users')

  // Super admin accounts are out of reach.
  await expect(row(page, 'Super Admin')).toContainText('Protégé')

  // Editing a user works again.
  await row(page, 'Nouvel Inscrit').locator('a[href^="/user-form/"]').click()
  await expect(page.locator('#user-name')).toHaveValue('Nouvel Inscrit')
  await page.locator('#user-name').fill('Nouvel Inscrit Modifié')
  await page.getByRole('button', { name: 'Enregistrer' }).click()
  await expect(page).toHaveURL(/\/manage-users$/)
  await expect(row(page, 'Nouvel Inscrit Modifié')).toBeVisible()

  // A student with payments cannot be deleted by an admin: deactivate instead.
  await row(page, 'Yao Adjo').locator('.btn-outline-danger-custom').click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toContainText('1 inscription(s), 1 paiement(s)')
  await expect(dialog.getByRole('button', { name: /Supprimer/ })).toHaveCount(0)
  await dialog.getByRole('button', { name: 'Désactiver à la place' }).click()
  await expect(dialog).toHaveCount(0)
  await expect(row(page, 'Yao Adjo')).toContainText('Inactif')
})

test('a super admin deletes an account permanently after typing its email', async ({ page }) => {
  await login(page, 'super.e2e@acathecpa.test')
  await page.goto('/manage-users')

  await row(page, 'Yao Adjo').locator('.btn-outline-danger-custom').click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toContainText('Suppression définitive')
  const confirm = dialog.getByRole('button', { name: 'Supprimer définitivement' })
  await expect(confirm).toBeDisabled()
  await dialog.getByLabel(/pour confirmer/).fill('yao.e2e@acathecpa.test')
  await confirm.click()

  await expect(dialog).toHaveCount(0)
  await expect(row(page, 'Yao Adjo')).toHaveCount(0)
})
