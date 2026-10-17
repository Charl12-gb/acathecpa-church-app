import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CourseStudentsPage from '../../src/views/dashboard/professor/CourseStudentsPage.vue'
import * as api from '../../src/services/api/course'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api/course', () => ({ getCourseById: vi.fn(), getCourseStudents: vi.fn() }))
const mocked = vi.mocked(api)

const quiz = (best: number | null, attempts: number, passed: boolean) =>
  [{ test_id: 7, title: 'Quiz TVA', attempts, best_score: best, passed }]

const rows = [
  { user_id: 1, name: 'Awa Koné', email: 'awa@test', enrolled_at: '2026-10-01T10:00:00Z', progress_percentage: 100,
    completed_lessons: 3, completed_at: '2026-10-10T10:00:00Z', last_activity: '2026-10-10T10:00:00Z',
    quizzes: quiz(100, 2, true), certificate_code: 'CERT-AAAA000001' },
  { user_id: 2, name: 'Koffi Mensah', email: 'koffi@test', enrolled_at: '2026-10-05T10:00:00Z', progress_percentage: 33.3,
    completed_lessons: 1, completed_at: null, last_activity: '2026-10-16T10:00:00Z',
    quizzes: quiz(0, 1, false), certificate_code: null },
  { user_id: 3, name: 'Yao Adjo', email: 'yao@test', enrolled_at: '2026-10-15T10:00:00Z', progress_percentage: 0,
    completed_lessons: 0, completed_at: null, last_activity: '2026-10-15T10:00:00Z',
    quizzes: quiz(null, 0, false), certificate_code: null },
]

async function mountPage() {
  mocked.getCourseById.mockResolvedValue({ id: 4, title: 'Fiscalité' } as any)
  mocked.getCourseStudents.mockResolvedValue(rows as any)
  const router = await makeRouter(CourseStudentsPage, [{ path: '/manage-courses/:id/students' }], '/manage-courses/4/students')
  const wrapper = mount(CourseStudentsPage, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}

describe('CourseStudentsPage', () => {
  it('summarises the class and lists each student', async () => {
    const wrapper = await mountPage()
    expect(mocked.getCourseStudents).toHaveBeenCalledWith(4)
    expect(wrapper.find('h2').text()).toBe('Étudiants · Fiscalité')
    const tiles = wrapper.findAll('.card-body').map(t => t.text())
    expect(tiles).toEqual(['Inscrits3', 'Progression moyenne44 %', 'Ont terminé1', 'Certificats1'])
    expect(wrapper.findAll('th').map(th => th.text())).toContain('Quiz TVA')

    const [awa, koffi, yao] = wrapper.findAll('tbody tr')
    expect(awa.text()).toContain('100 % (2 essais)')
    expect(awa.text()).toContain('CERT-AAAA000001')
    expect(koffi.text()).toContain('0 % (1 essai)')
    expect(yao.text()).toContain('—')
  })

  it('filters by state and by name', async () => {
    const wrapper = await mountPage()
    await wrapper.get('#student-filter').setValue('in_progress')
    expect(wrapper.findAll('tbody tr').map(r => r.find('.fw-semibold').text())).toEqual(['Koffi Mensah'])

    await wrapper.get('#student-filter').setValue('all')
    await wrapper.get('#student-search').setValue('yao')
    expect(wrapper.findAll('tbody tr').map(r => r.find('.fw-semibold').text())).toEqual(['Yao Adjo'])
  })
})
