import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UsersPage from '../../src/views/dashboard/admin/UsersPage.vue'
import UserFormPage from '../../src/views/dashboard/admin/UserFormPage.vue'
import * as userApi from '../../src/services/api/user'
import { makeRouter } from './helpers'

let currentRole = 'admin'
vi.mock('../../src/stores/auth', () => ({
  useAuthStore: () => ({ hasRole: (r: string) => r === currentRole }),
}))
vi.mock('../../src/services/api/user', () => ({
  getUsers: vi.fn(), deleteUser: vi.fn(), updateUser: vi.fn(),
  getUserDeletionImpact: vi.fn(), getUserById: vi.fn(),
}))
vi.mock('../../src/services/api/auth', () => ({ register: vi.fn() }))
const api = vi.mocked(userApi)

const history = (over = {}) => ({
  enrollments: 0, payments: 0, certificates: 0, courses: 0, course_enrollments: 0, contents: 0, live_sessions: 0, ...over,
})
const users = [
  { id: 1, name: 'Super Admin', email: 'super@test', role: { name: 'super_admin' }, is_active: true, created_at: '2026-10-01' },
  { id: 2, name: 'Yao Adjo', email: 'yao@test', role: { name: 'student' }, is_active: true, created_at: '2026-10-01' },
]

async function mountUsers() {
  api.getUsers.mockResolvedValue(users as any)
  const router = await makeRouter(UsersPage, [{ path: '/manage-users' }], '/manage-users')
  const wrapper = mount(UsersPage, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}
const yaoRow = (w: any) => w.findAll('tbody tr').find((r: any) => r.text().includes('Yao Adjo'))

beforeEach(() => { currentRole = 'admin' })

describe('Admin UsersPage', () => {
  it('shows super admin accounts as protected to an admin', async () => {
    const wrapper = await mountUsers()
    const superRow = wrapper.findAll('tbody tr').find(r => r.text().includes('Super Admin'))!
    expect(superRow.text()).toContain('Protégé')
    expect(superRow.find('.btn-outline-danger-custom').exists()).toBe(false)
  })

  it('offers deactivation instead of deletion for an account with history', async () => {
    api.getUserDeletionImpact.mockResolvedValue({ history: history({ enrollments: 1, payments: 1 }), has_history: true, can_delete: false })
    api.updateUser.mockResolvedValue({} as any)
    const wrapper = await mountUsers()
    await yaoRow(wrapper).get('.btn-outline-danger-custom').trigger('click')
    await flushPromises()

    const dialog = wrapper.get('[role="dialog"]')
    expect(dialog.text()).toContain('1 inscription(s), 1 paiement(s)')
    await dialog.findAll('button').find(b => b.text() === 'Désactiver à la place')!.trigger('click')
    await flushPromises()
    expect(api.updateUser).toHaveBeenCalledWith(2, { is_active: false })
    expect(api.deleteUser).not.toHaveBeenCalled()
    expect(yaoRow(wrapper).text()).toContain('Inactif')
  })

  it('lets a super admin delete permanently once the email is typed', async () => {
    currentRole = 'super_admin'
    api.getUserDeletionImpact.mockResolvedValue({ history: history({ payments: 1 }), has_history: true, can_delete: true })
    api.deleteUser.mockResolvedValue({} as any)
    const wrapper = await mountUsers()
    await yaoRow(wrapper).get('.btn-outline-danger-custom').trigger('click')
    await flushPromises()

    const confirmBtn = () => wrapper.findAll('[role="dialog"] button').find(b => b.text() === 'Supprimer définitivement')!
    expect(confirmBtn().attributes('disabled')).toBeDefined()
    await wrapper.get('#del-confirm').setValue('yao@test')
    await confirmBtn().trigger('click')
    await flushPromises()
    expect(api.deleteUser).toHaveBeenCalledWith(2)
    expect(yaoRow(wrapper)).toBeUndefined()
  })
})

describe('Admin UserFormPage', () => {
  it('sends the role as a plain name', async () => {
    api.getUserById.mockResolvedValue({ id: 2, name: 'Yao Adjo', email: 'yao@test', role: { name: 'student' }, is_active: true } as any)
    api.updateUser.mockResolvedValue({} as any)
    const router = await makeRouter(UserFormPage, [{ path: '/user-form/:id?' }], '/user-form/2')
    const wrapper = mount(UserFormPage, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.get('#user-name').setValue('Yao A.')
    await wrapper.get('button.btn-primary').trigger('click')
    await flushPromises()
    expect(api.updateUser).toHaveBeenCalledWith(2, expect.objectContaining({ name: 'Yao A.', role: 'student' }))
  })
})
