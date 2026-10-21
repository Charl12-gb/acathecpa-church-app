import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContentsAdminPage from '../../src/views/dashboard/admin/ContentsAdminPage.vue'
import * as contentApi from '../../src/services/api/content'
import apiClient from '../../src/services/api/index'
import { uploadFile } from '../../src/services/api/upload'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api/content', () => ({
  getAllContentsForAdmin: vi.fn(), updateContentStatus: vi.fn(), deleteContent: vi.fn(),
}))
vi.mock('../../src/services/api/index', () => ({ default: { post: vi.fn() } }))
const api = vi.mocked(contentApi)

const rows = [
  { id: 1, title: 'Brouillon TVA', type: 'article', format: 'text', status: 'draft', is_premium: false,
    author_name: 'Prof. Diallo', updated_at: '2026-10-20T10:00:00Z' },
  { id: 2, title: 'Podcast premium', type: 'podcast', format: 'audio', status: 'published', is_premium: true,
    price: 2000, author_name: 'Prof. Agbo', updated_at: '2026-10-19T10:00:00Z' },
]

async function mountPage() {
  api.getAllContentsForAdmin.mockResolvedValue(structuredClone(rows) as any)
  const router = await makeRouter(ContentsAdminPage, [{ path: '/manage-contents' }], '/manage-contents')
  const wrapper = mount(ContentsAdminPage, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}

beforeEach(() => vi.clearAllMocks())

describe('ContentsAdminPage', () => {
  it('lists every author’s posts with edit links', async () => {
    const wrapper = await mountPage()
    const [draft, premium] = wrapper.findAll('tbody tr')
    expect(draft.text()).toContain('Prof. Diallo')
    expect(premium.text()).toContain('Premium 2000 XOF')
    expect(draft.get('a[href="/content/editor/1?back=manage"]').text()).toBe('Modifier')
    expect(premium.find('a[href="/podcasts/2"]').exists()).toBe(true) // published: "Voir"
  })

  it('changes the status of a post', async () => {
    api.updateContentStatus.mockResolvedValue({ ...rows[0], status: 'published', updated_at: '2026-10-21T08:00:00Z' } as any)
    const wrapper = await mountPage()
    await wrapper.get('#status-1').setValue('published')
    await flushPromises()
    expect(api.updateContentStatus).toHaveBeenCalledWith(1, 'published')
  })

  it('deletes a post after confirmation', async () => {
    api.deleteContent.mockResolvedValue({} as any)
    const wrapper = await mountPage()
    await wrapper.findAll('tbody tr')[1].findAll('button').find(b => b.text() === 'Supprimer')!.trigger('click')
    expect(wrapper.get('[role="dialog"]').text()).toContain('Podcast premium')
    await wrapper.get('[role="dialog"] .btn-danger').trigger('click')
    await flushPromises()
    expect(api.deleteContent).toHaveBeenCalledWith(2)
    expect(wrapper.findAll('tbody tr')).toHaveLength(1)
  })
})

describe('uploadFile', () => {
  it('sends the file as a raw body (no multipart) with its name in the URL', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { url: '/media/x.pdf' } })
    const file = new File(['%PDF'], 'calendrier fiscal.pdf', { type: 'application/pdf' })
    await uploadFile(file, 'document')
    const [url, body, config] = vi.mocked(apiClient.post).mock.calls[0] as any[]
    expect(url).toBe('/uploads/')
    expect(body).toBe(file)
    expect(config.params).toEqual({ filename: 'calendrier fiscal.pdf', category: 'document' })
    expect(config.headers['Content-Type']).toBe('application/pdf')
  })
})
