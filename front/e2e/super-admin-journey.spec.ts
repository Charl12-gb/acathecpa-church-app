import { test, expect, type Page } from '@playwright/test'

/** Super admin screens, on the accounts seeded by backend/tests/e2e_seed.py. */
async function login(page: Page, email: string, password = 'Password123!') {
  await page.goto('/login')
  await page.locator('#identifier').fill(email)
  await page.locator('#password').fill(password)
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
}

test('a super admin adjusts a role permission and finds it in the audit log', async ({ page }) => {
  await login(page, 'super.e2e@acathecpa.test')
  await page.locator('.nav-item', { hasText: 'Rôles et permissions' }).click()
  await expect(page.getByRole('heading', { name: 'Rôles et permissions' })).toBeVisible()

  const box = page.locator('#p-student-create_content')
  await expect(box).not.toBeChecked()
  await box.check()
  await page.reload()
  await expect(page.locator('#p-student-create_content')).toBeChecked()

  await page.locator('.nav-item', { hasText: "Journal d'audit" }).click()
  const row = page.getByRole('row', { name: /Permission accordée à un rôle/ }).first()
  await expect(row).toContainText('super.e2e@acathecpa.test')
  await expect(row).toContainText('student')
  await expect(row).toContainText('create_content')
})

test('an admin has no access to the super admin screens', async ({ page }) => {
  await login(page, 'admin.e2e@acathecpa.test')
  await expect(page.locator('.nav-item', { hasText: 'Rôles et permissions' })).toHaveCount(0)
  await page.goto('/roles-permissions')
  await expect(page).toHaveURL(/\/dashboard$/)
})

test('a user changes their own password from the profile', async ({ page }) => {
  await login(page, 'nouveau.e2e@acathecpa.test')
  await page.goto('/profile')
  await page.getByRole('button', { name: /Sécurité/ }).click()
  await page.locator('#current_password').fill('Password123!')
  await page.locator('#new_password').fill('NouveauSecret456!')
  await page.locator('#confirm_password').fill('NouveauSecret456!')
  await page.locator('form').filter({ has: page.locator('#current_password') }).locator('button[type="submit"]').click()
  await expect(page.getByText('Mot de passe modifié.')).toBeVisible()

  await page.context().clearCookies()
  await page.evaluate(() => localStorage.clear())
  await login(page, 'nouveau.e2e@acathecpa.test', 'NouveauSecret456!')
})
