import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import VerifyEmailPage from '../../src/views/auth/VerifyEmailPage.vue'
import * as authApi from '../../src/services/api/auth'
import { makeRouter } from './helpers'

const push = vi.fn()
vi.mock('../../src/router', () => ({ default: { push: (...a: any[]) => push(...a) } }))
vi.mock('../../src/services/api/auth', () => ({
  login: vi.fn(), getMe: vi.fn(), register: vi.fn(), updateMe: vi.fn(),
  requestPasswordReset: vi.fn(), resetPassword: vi.fn(), verifyEmail: vi.fn(), resendVerification: vi.fn(),
}))
const api = vi.mocked(authApi)

beforeEach(() => {
  localStorage.clear()
  push.mockClear()
  setActivePinia(createPinia())
  api.login.mockResolvedValue({ access_token: 't', refresh_token: 'r' } as any)
  api.getMe.mockResolvedValue({ id: 1, email: 'awa@test', role: { name: 'student' } } as any)
})

describe('login redirect', () => {
  it('goes back to the page the visitor came from', async () => {
    const { useAuthStore } = await import('../../src/stores/auth')
    await useAuthStore().login('awa@test', 'pw', '/course/4')
    expect(push).toHaveBeenCalledWith('/course/4')
  })

  it('ignores redirects to other sites', async () => {
    const { useAuthStore } = await import('../../src/stores/auth')
    await useAuthStore().login('awa@test', 'pw', '//evil.example/phish')
    expect(push).toHaveBeenCalledWith('/dashboard')
  })

  it('shows the server message when there were too many attempts', async () => {
    api.login.mockRejectedValue({ response: { status: 429, data: { detail: 'Trop de tentatives de connexion.' } } })
    const { useAuthStore } = await import('../../src/stores/auth')
    const store = useAuthStore()
    await store.login('awa@test', 'pw')
    expect(store.error).toBe('Trop de tentatives de connexion.')
  })
})

describe('VerifyEmailPage', () => {
  const mountAt = async (path: string) => {
    const router = await makeRouter(VerifyEmailPage, [{ path: '/verify-email' }], path)
    const wrapper = mount(VerifyEmailPage, { global: { plugins: [router] } })
    await flushPromises()
    return wrapper
  }

  it('confirms the address from the link', async () => {
    api.verifyEmail.mockResolvedValue({ message: 'ok' })
    const wrapper = await mountAt('/verify-email?token=abc')
    expect(api.verifyEmail).toHaveBeenCalledWith('abc')
    expect(wrapper.text()).toContain('Adresse email confirmée')
  })

  it('explains an expired link', async () => {
    api.verifyEmail.mockRejectedValue({ response: { data: { detail: 'Ce lien de confirmation est invalide ou expiré.' } } })
    const wrapper = await mountAt('/verify-email?token=old')
    expect(wrapper.text()).toContain('Lien invalide ou expiré')
    expect(wrapper.text()).toContain('Ce lien de confirmation est invalide ou expiré.')
  })
})
