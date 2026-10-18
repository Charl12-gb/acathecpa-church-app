import { test, expect } from '@playwright/test'

/** Public side of the site, on the data seeded by backend/tests/e2e_seed.py. */
const COURSE = 'Fiscalité des entreprises'

test('a visitor finds the courses from the menu, signs in to enroll and comes back to the course', async ({ page }) => {
  await page.goto('/')
  await page.locator('nav').getByRole('link', { name: 'Formations' }).first().click()
  await expect(page).toHaveURL(/\/browse-courses$/)

  await page.getByRole('link', { name: COURSE }).first().click()
  await expect(page).toHaveURL(/\/course\/\d+$/)
  const courseUrl = page.url()

  await page.getByRole('button', { name: "Se connecter pour s'inscrire" }).click()
  await expect(page).toHaveURL(/\/login\?redirect=/)
  await page.locator('#identifier').fill('koffi.e2e@acathecpa.test')
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(courseUrl)
})

test('a new account sees the email confirmation reminder and can ask for a new link', async ({ page }) => {
  const email = `inscrit.${Date.now()}@acathecpa.test`
  await page.goto('/register')
  await expect(page.getByRole('link', { name: "conditions d'utilisation" })).toHaveAttribute('href', '/conditions-utilisation')
  await page.locator('#name').fill('Nouvelle Inscrite')
  await page.locator('#email').fill(email)
  await page.locator('#phone').fill(`+22997${String(Date.now()).slice(-8)}`)
  await page.locator('#birthdate').fill('2000-01-01')
  await page.locator('#password').fill('Password123!')
  await page.locator('#confirm_password').fill('Password123!')
  await page.locator('#terms').check()
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/login$/)

  await page.locator('#identifier').fill(email)
  await page.locator('#password').fill('Password123!')
  await page.locator('button[type="submit"]').click()
  await expect(page).toHaveURL(/\/dashboard$/)
  const banner = page.locator('.verify-banner')
  await expect(banner).toContainText('Confirmez votre adresse email')
  await banner.getByRole('button', { name: 'Renvoyer le lien' }).click()
  await expect(banner).toContainText(`Un nouveau lien a été envoyé à ${email}`)
})

test('legal pages and the not-found page are reachable', async ({ page }) => {
  await page.goto('/')
  await page.locator('footer').getByRole('link', { name: 'Confidentialité' }).click()
  await expect(page.getByRole('heading', { name: 'Politique de confidentialité' })).toBeVisible()
  await page.locator('footer').getByRole('link', { name: "Conditions d'utilisation" }).click()
  await expect(page.getByRole('heading', { name: "Conditions générales d'utilisation" })).toBeVisible()

  await page.goto('/une-page-qui-nexiste-pas')
  await expect(page.getByRole('heading', { name: "Cette page n'existe pas" })).toBeVisible()
  await expect(page.locator('footer')).not.toContainText('123 Rue Principale')
})
