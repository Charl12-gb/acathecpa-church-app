import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RolesPermissionsPage from '../../src/views/dashboard/admin/RolesPermissionsPage.vue'
import AuditLogPage from '../../src/views/dashboard/admin/AuditLogPage.vue'
import * as permApi from '../../src/services/api/permissions'
import * as auditApi from '../../src/services/api/audit'

vi.mock('../../src/router', () => ({ default: { push: vi.fn() } }))
vi.mock('../../src/services/api/permissions', () => ({
  getRoles: vi.fn(), getPermissionDefinitions: vi.fn(), getRolePermissions: vi.fn(),
  grantRolePermission: vi.fn(), revokeRolePermission: vi.fn(),
  getUserOverrides: vi.fn(), addUserOverride: vi.fn(), removeUserOverride: vi.fn(),
}))
vi.mock('../../src/services/api/user', () => ({ getUsers: vi.fn() }))
vi.mock('../../src/services/api/audit', () => ({ getAuditLogs: vi.fn() }))
const perm = vi.mocked(permApi)
const audit = vi.mocked(auditApi)

const roles = ['student', 'professor', 'admin', 'super_admin'].map(name => ({ id: `r-${name}`, name }))
const P = (permission: string, title: string, category: string) => ({ id: `p-${permission}`, permission, title, category })
const permissions = [
  P('enroll_in_course', 'Enroll in Course', 'Course Enrollment'),
  P('create_content', 'Create Content', 'Content Management'),
  P('create_role', 'Create Role', 'Role Management'),
]

beforeEach(() => {
  perm.getRoles.mockResolvedValue(roles)
  perm.getPermissionDefinitions.mockResolvedValue(permissions)
  perm.getRolePermissions.mockResolvedValue([
    { id: 'l1', role: roles[0], permission: permissions[0] },
  ])
  perm.getUserOverrides.mockResolvedValue([])
})

describe('RolesPermissionsPage', () => {
  it('lets the super admin toggle student and professor permissions only', async () => {
    perm.grantRolePermission.mockResolvedValue({ id: 'l2', role: roles[1], permission: permissions[1] })
    perm.revokeRolePermission.mockResolvedValue()
    const wrapper = mount(RolesPermissionsPage)
    await flushPromises()

    const studentEnroll = wrapper.get('#p-student-enroll_in_course')
    expect((studentEnroll.element as HTMLInputElement).checked).toBe(true)
    // Admin and super admin columns are not editable.
    expect(wrapper.find('#p-admin-enroll_in_course').exists()).toBe(false)
    const createRoleRow = wrapper.findAll('tbody tr').find(r => r.text().includes('create_role'))!
    expect(createRoleRow.findAll('.bi-check-lg')).toHaveLength(1) // super admin only, not admin

    await wrapper.get('#p-professor-create_content').trigger('change')
    await flushPromises()
    expect(perm.grantRolePermission).toHaveBeenCalledWith('r-professor', 'p-create_content')

    await studentEnroll.trigger('change')
    await flushPromises()
    expect(perm.revokeRolePermission).toHaveBeenCalledWith('l1')
  })

  it('shows the server refusal instead of failing silently', async () => {
    perm.grantRolePermission.mockRejectedValue({ response: { data: { detail: 'Refusé.' } } })
    const wrapper = mount(RolesPermissionsPage)
    await flushPromises()
    await wrapper.get('#p-student-create_content').trigger('change')
    await flushPromises()
    expect(wrapper.get('.alert-danger').text()).toContain('Refusé.')
  })
})

describe('AuditLogPage', () => {
  it('lists actions with readable details', async () => {
    audit.getAuditLogs.mockResolvedValue([
      { id: 2, created_at: '2026-10-18T09:00:00Z', actor_email: 'super@test', action: 'user.deleted_with_data',
        action_label: 'Compte supprimé définitivement avec ses données', target_type: 'user', target_id: '5',
        target_label: 'prof@test', details: { history: { courses: 1, payments: 0, course_enrollments: 3 } } },
      { id: 1, created_at: '2026-10-18T08:00:00Z', actor_email: 'admin@test', action: 'user.role_changed',
        action_label: 'Changement de rôle', target_type: 'user', target_id: '4', target_label: 'eleve@test',
        details: { old: 'student', new: 'professor' } },
    ])
    const wrapper = mount(AuditLogPage)
    await flushPromises()
    const rows = wrapper.findAll('tbody tr').map(r => r.text())
    expect(rows[0]).toContain('1 cours, 3 inscription(s) à ses cours')
    expect(rows[1]).toContain('student → professor')

    await wrapper.get('#audit-action').setValue('user.role_changed')
    await flushPromises()
    expect(audit.getAuditLogs).toHaveBeenLastCalledWith({ action: 'user.role_changed', q: undefined })
  })
})

describe('auth store', () => {
  it('does not crash for a user without role', async () => {
    localStorage.setItem('user', JSON.stringify({ id: 1, email: 'root@test', role: null }))
    localStorage.setItem('token', 'x')
    setActivePinia(createPinia())
    const { useAuthStore } = await import('../../src/stores/auth')
    const store = useAuthStore()
    expect(store.hasMinRole('student' as any)).toBe(false)
    expect(store.hasRole('super_admin' as any)).toBe(false)
    localStorage.clear()
  })
})
