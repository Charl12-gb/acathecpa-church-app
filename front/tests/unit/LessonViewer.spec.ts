import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LessonViewer from '../../src/views/dashboard/student/LessonViewer.vue'
import * as api from '../../src/services/api/course'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api/course', () => ({
  getCourseById: vi.fn(),
  fetchFullCourseTest: vi.fn(),
  submitStudentTestAttempt: vi.fn(),
  markStudentLessonCompleted: vi.fn(),
  getMyCourseEnrollmentProgress: vi.fn(),
}))

const mocked = vi.mocked(api)

// What the API sends to an enrolled student: content, but no quiz answers.
const course = {
  id: 1,
  title: 'Comptabilité OHADA',
  sections: [
    {
      id: 1, title: 'Bases', order: 1, content_type: 'text',
      text_content: '<p>Présentation de la section</p>', video_url: null, test: null,
      lessons: [
        { id: 101, title: 'Le plan comptable', type: 'text', content_body: '<p>Classes 1 à 9</p>', video_url: null },
        { id: 102, title: 'Les journaux', type: 'text', content_body: '<p>Journal général</p>', video_url: null },
      ],
    },
    {
      id: 2, title: 'Bilan', order: 2, content_type: 'quiz', text_content: null, video_url: null,
      test: { id: 7, title: 'Quiz bilan' },
      lessons: [],
    },
  ],
}

const quiz = {
  id: 7, title: 'Quiz bilan', passing_score: 70, max_attempts: 2,
  questions: [
    { id: 71, question_text: "L'actif est à…", question_type: 'multiple_choice', points: 1,
      options: [{ text: 'gauche' }, { text: 'droite' }] },
    { id: 72, question_text: 'Le capital est un…', question_type: 'multiple_choice', points: 2,
      options: [{ text: 'Vrai' }, { text: 'Faux' }] },
  ],
}

const progress = (over: Record<string, unknown> = {}) => ({
  user_id: 5, course_id: 1, enrolled_at: '2026-10-01T10:00:00Z',
  progress_percentage: 0, completed_lessons: [], completed_sections: [],
  test_attempts: [], test_scores: [], ...over,
})

const routes = [
  { path: '/lesson/:courseId/:lessonId', name: 'lesson-viewer' },
  { path: '/lesson/:courseId/section/:sectionId/:part?', name: 'section-viewer' },
]

async function mountAt(path: string) {
  const router = await makeRouter(LessonViewer, routes, path)
  const wrapper = mount(LessonViewer, { global: { plugins: [router] } })
  await flushPromises()
  return { wrapper, router }
}

beforeEach(() => {
  mocked.getCourseById.mockResolvedValue(course as any)
  mocked.getMyCourseEnrollmentProgress.mockResolvedValue(progress() as any)
  mocked.fetchFullCourseTest.mockResolvedValue(quiz as any)
})

describe('LessonViewer', () => {
  it('lists the course as intro, lessons then quiz, and shows the lesson body', async () => {
    const { wrapper } = await mountAt('/lesson/1/101')

    const outline = wrapper.findAll('.list-group-item-action').map(b => b.text())
    expect(outline).toEqual(['Introduction', 'Le plan comptable', 'Les journaux', 'Quiz : Quiz bilan'])
    expect(wrapper.find('h2').text()).toBe('Le plan comptable')
    // The lesson body is shown, not the section text.
    expect(wrapper.html()).toContain('Classes 1 à 9')
    expect(wrapper.html()).not.toContain('Présentation de la section')
  })

  it('shows the section introduction on its own step', async () => {
    const { wrapper } = await mountAt('/lesson/1/section/1')
    expect(wrapper.html()).toContain('Présentation de la section')
  })

  it('marks a lesson as done and moves to the next step', async () => {
    mocked.markStudentLessonCompleted.mockResolvedValue(
      progress({ completed_lessons: [101], progress_percentage: 33.3 }) as any,
    )
    const { wrapper, router } = await mountAt('/lesson/1/101')

    await wrapper.get('.card-body .btn-primary.btn-lg').trigger('click')
    await flushPromises()

    expect(mocked.markStudentLessonCompleted).toHaveBeenCalledWith(1, 101)
    expect(router.currentRoute.value.fullPath).toBe('/lesson/1/102')
    expect(wrapper.text()).toContain('33% complété')
    expect(wrapper.find('.list-group-item-action .bi-check-circle-fill').exists()).toBe(true)
  })

  it('reaches a quiz that has no lessons and sends only the chosen options', async () => {
    mocked.submitStudentTestAttempt.mockResolvedValue(progress({
      test_attempts: [{ test_id: 7, attempt_number: 1, score: 33.33, passed: false,
        points_earned: 1, points_possible: 3, attempted_at: '2026-10-17T09:00:00Z', questions_summary: [] }],
    }) as any)
    const { wrapper } = await mountAt('/lesson/1/section/2/quiz')

    expect(mocked.fetchFullCourseTest).toHaveBeenCalledWith(7)
    expect(wrapper.text()).toContain('Tentatives : 0 / 2')

    await wrapper.get('button.btn-primary').trigger('click') // Commencer le quiz
    await wrapper.get('#option-71-0').setValue(true)
    expect(wrapper.text()).toContain('1 question(s) sans réponse.')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(mocked.submitStudentTestAttempt).toHaveBeenCalledWith(1, 7, {
      answers: [{ question_id: 71, answer: 0 }, { question_id: 72, answer: null }],
    })
    expect(wrapper.text()).toContain('Score : 33.33 % (1 / 3 points)')
    expect(wrapper.text()).toContain('Échoué')
    expect(wrapper.text()).toContain('Repasser le quiz')
  })

  it('stops offering the quiz once the attempts are used up', async () => {
    const failed = { test_id: 7, score: 0, passed: false, points_earned: 0, points_possible: 3,
      attempted_at: '2026-10-17T09:00:00Z', questions_summary: [] }
    mocked.getMyCourseEnrollmentProgress.mockResolvedValue(progress({
      test_attempts: [{ ...failed, attempt_number: 1 }, { ...failed, attempt_number: 2 }],
    }) as any)
    const { wrapper } = await mountAt('/lesson/1/section/2/quiz')

    expect(wrapper.text()).toContain('Nombre maximum de tentatives atteint.')
    expect(wrapper.text()).not.toContain('Repasser le quiz')
  })

  it('shows the server error when the quiz is refused', async () => {
    mocked.submitStudentTestAttempt.mockRejectedValue({
      response: { data: { detail: 'Nombre maximum de tentatives atteint.' } },
    })
    const { wrapper } = await mountAt('/lesson/1/section/2/quiz')
    await wrapper.get('button.btn-primary').trigger('click')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('.alert-warning').text()).toBe('Nombre maximum de tentatives atteint.')
  })

  it('points to the certificate when the course is finished', async () => {
    mocked.getMyCourseEnrollmentProgress.mockResolvedValue(
      progress({ progress_percentage: 100, completed_lessons: [101, 102] }) as any,
    )
    const { wrapper } = await mountAt('/lesson/1/102')
    expect(wrapper.text()).toContain('Obtenir mon certificat')
  })

  it('asks a visitor who is not enrolled to enroll', async () => {
    mocked.getMyCourseEnrollmentProgress.mockRejectedValue({ response: { status: 404 } })
    const { wrapper } = await mountAt('/lesson/1/101')
    expect(wrapper.text()).toContain("Vous n'êtes pas inscrit à ce cours.")
    expect(wrapper.get('a.btn-primary').attributes('href')).toBe('/course/1')
  })
})
