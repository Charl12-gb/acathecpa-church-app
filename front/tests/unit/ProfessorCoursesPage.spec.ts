import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CoursesPage from '../../src/views/dashboard/professor/CoursesPage.vue'
import * as api from '../../src/services/api/course'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api/course', () => ({
  getInstructorCourses: vi.fn(),
  deleteCourse: vi.fn(),
  publishCourse: vi.fn(),
  updateCourse: vi.fn(),
}))
const mocked = vi.mocked(api)

const course = (id: number, title: string, extra: Record<string, unknown> = {}) => ({
  id, title, status: 'published', is_free: false, price: 5000, created_at: '2026-10-01T10:00:00Z',
  updated_at: '2026-10-01T10:00:00Z', students_count: 0, revenue: 0, ...extra,
})

async function mountPage() {
  const router = await makeRouter(CoursesPage, [{ path: '/manage-courses' }], '/manage-courses')
  const wrapper = mount(CoursesPage, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  mocked.getInstructorCourses.mockResolvedValue([
    course(1, 'Fiscalité', { students_count: 3, revenue: 15000 }),
    course(2, 'Brouillon vide', { status: 'draft', students_count: 0 }),
  ] as any)
})

describe('Professor CoursesPage', () => {
  it('shows real students and revenue per course and in total', async () => {
    const wrapper = await mountPage()
    expect(wrapper.find('.stats-strip').text()).toContain('3 étudiants')
    expect(wrapper.find('.stats-strip').text()).toMatch(/15\s000 XOF/)
    expect(wrapper.find('.stats-strip').text()).not.toContain('note')
    const fisc = wrapper.findAll('.course-card')[0]
    expect(fisc.text()).toContain('3 étudiant(s)')
    expect(fisc.get('a[href="/manage-courses/1/students"]').text()).toContain('Étudiants')
  })

  it('explains why a course with students cannot be deleted, and keeps it listed', async () => {
    mocked.deleteCourse.mockRejectedValue({
      response: { status: 409, data: { detail: 'Ce cours a des étudiants inscrits… il ne peut pas être supprimé.' } },
    })
    const wrapper = await mountPage()
    await wrapper.findAll('.course-card')[0].get('button.danger').trigger('click')
    await flushPromises()
    expect(wrapper.get('.notice-banner').text()).toContain('il ne peut pas être supprimé')
    expect(wrapper.findAll('.course-card')).toHaveLength(2)
  })

  it('explains why an empty course cannot be published', async () => {
    mocked.publishCourse.mockRejectedValue({
      response: { status: 400, data: { detail: 'Ajoutez au moins une leçon ou un quiz avant de publier ce cours.' } },
    })
    const wrapper = await mountPage()
    const draft = wrapper.findAll('.course-card')[1]
    await draft.get('.status-select .ss-control').trigger('click')
    await draft.findAll('.ss-option').find(o => o.text() === 'Publié')!.trigger('click')
    await flushPromises()
    expect(mocked.publishCourse).toHaveBeenCalledWith(2)
    expect(wrapper.get('.notice-banner').text()).toContain('Ajoutez au moins une leçon')
    expect(draft.get('.thumb-badge').text()).toBe('Brouillon')
  })
})
