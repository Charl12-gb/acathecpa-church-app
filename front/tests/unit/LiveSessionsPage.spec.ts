import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { reactive } from 'vue'
import LiveSessionsPage from '../../src/views/dashboard/student/LiveSessionsPage.vue'
import * as liveApi from '../../src/services/api/liveSession'

const videoStore = reactive({
  activeMeetingUrl: '' as string,
  error: '',
  joinMeeting: vi.fn(async () => { videoStore.activeMeetingUrl = 'https://8x8.test/app/live-session-1' }),
  leaveMeeting: vi.fn(async () => { videoStore.activeMeetingUrl = '' }),
})

vi.mock('../../src/services/api/liveSession', () => ({ getAllLiveSessions: vi.fn() }))
vi.mock('../../src/stores/videoConference', () => ({ useVideoConferenceStore: () => videoStore }))
vi.mock('../../src/stores/auth', () => ({ useAuthStore: () => ({ user: { name: 'Awa Koné' } }) }))

const mocked = vi.mocked(liveApi)

const session = (id: number, status: string, scheduled_for: string) => ({
  id, title: `Session ${id}`, status, scheduled_for, host_id: 2, host: { name: 'Prof. Diallo' },
})

describe('Student LiveSessionsPage', () => {
  it('groups sessions and lets the student join an upcoming one', async () => {
    mocked.getAllLiveSessions.mockResolvedValue([
      session(3, 'ended', '2026-10-01T10:00:00Z'),
      session(2, 'scheduled', '2026-10-20T10:00:00Z'),
      session(1, 'live', '2026-10-17T10:00:00Z'),
    ] as any)
    const wrapper = mount(LiveSessionsPage)
    await flushPromises()

    const titles = wrapper.findAll('.fw-semibold').map(e => e.text())
    expect(titles).toEqual(['Session 1 En direct', 'Session 2', 'Session 3'])
    // Ended sessions have no join button.
    expect(wrapper.findAll('button.btn-primary')).toHaveLength(2)

    await wrapper.get('button.btn-primary').trigger('click')
    await flushPromises()
    expect(videoStore.joinMeeting).toHaveBeenCalledWith(1, 'Awa Koné')
    expect(wrapper.get('iframe').attributes('src')).toBe('https://8x8.test/app/live-session-1')

    await wrapper.get('button.btn-outline-danger').trigger('click')
    await flushPromises()
    expect(videoStore.leaveMeeting).toHaveBeenCalled()
    expect(wrapper.find('iframe').exists()).toBe(false)
  })

  it('explains when there is no session', async () => {
    mocked.getAllLiveSessions.mockResolvedValue([])
    const wrapper = mount(LiveSessionsPage)
    await flushPromises()
    expect(wrapper.text()).toContain('Aucune session en direct pour vos cours')
  })
})
