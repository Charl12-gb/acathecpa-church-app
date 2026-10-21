import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MyContentPage from '../../src/views/dashboard/content/MyContentPage.vue'
import ContentEditorPage from '../../src/views/dashboard/content/ContentEditorPage.vue'
import { useContentStore } from '../../src/stores/content'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() } }))

/** A promise the test resolves when it wants: lets us look at the page while loading. */
function deferred<T>() {
  let resolve!: (v: T) => void
  let reject!: (e: unknown) => void
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej })
  return { promise, resolve, reject }
}

beforeEach(() => {
  setActivePinia(createPinia())
  window.scrollTo = (() => undefined) as any
  ;(document as any).elementFromPoint = () => null
  Range.prototype.getClientRects = () => ({ length: 0, item: () => null, [Symbol.iterator]: [][Symbol.iterator] }) as any
  Range.prototype.getBoundingClientRect = () => ({ top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0 }) as any
})

describe('Mes contenus', () => {
  const mountList = async () => {
    const router = await makeRouter(MyContentPage, [{ path: '/my-content' }], '/my-content')
    return mount(MyContentPage, { global: { plugins: [router] } })
  }

  it('shows a loader, not "Aucun contenu", until the list arrives', async () => {
    const pending = deferred<any[]>()
    vi.spyOn(useContentStore(), 'getUserContents').mockReturnValue(pending.promise)
    const wrapper = await mountList()
    expect(wrapper.find('[role="status"]').text()).toContain('Chargement de vos contenus')
    expect(wrapper.find('.empty-state').exists()).toBe(false)

    pending.resolve([{ id: 1, title: 'La TVA', type: 'article', format: 'text', status: 'draft', tags: [],
      created_at: '2026-10-20T10:00:00Z', updated_at: '2026-10-20T10:00:00Z' }])
    await flushPromises()
    expect(wrapper.find('[role="status"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('La TVA')
  })

  it('explains a loading failure', async () => {
    vi.spyOn(useContentStore(), 'getUserContents').mockRejectedValue('Network Error')
    const wrapper = await mountList()
    await flushPromises()
    expect(wrapper.get('.alert-danger').text()).toContain('Impossible de charger vos contenus')
    expect(wrapper.find('.empty-state').exists()).toBe(false)
  })
})

describe('Modification d’un contenu', () => {
  const mountEditor = async () => {
    const router = await makeRouter(ContentEditorPage, [{ path: '/content/editor/:id?' }, { path: '/my-content' }], '/content/editor/5')
    return mount(ContentEditorPage, { global: { plugins: [router] }, attachTo: document.body })
  }

  it('shows a loader, then the filled form', async () => {
    const pending = deferred<any>()
    vi.spyOn(useContentStore(), 'getContent').mockReturnValue(pending.promise)
    const wrapper = await mountEditor()
    expect(wrapper.find('[role="status"]').text()).toContain('Chargement du contenu')
    expect(wrapper.find('.ProseMirror').exists()).toBe(false)

    pending.resolve({ id: 5, title: 'La TVA', content_body: '<p>Texte enregistré</p>', type: 'article',
      format: 'text', status: 'draft', tags: [] })
    await flushPromises()
    expect(wrapper.find('[role="status"]').exists()).toBe(false)
    expect(wrapper.find('.ProseMirror').text()).toContain('Texte enregistré')
    wrapper.unmount()
  })

  it('offers to retry when the post cannot be loaded', async () => {
    const getContent = vi.spyOn(useContentStore(), 'getContent').mockRejectedValueOnce('Network Error')
    const wrapper = await mountEditor()
    await flushPromises()
    expect(wrapper.get('.load-error').text()).toContain('Impossible de charger ce contenu')

    getContent.mockResolvedValueOnce({ id: 5, title: 'La TVA', content_body: '<p>Retrouvé</p>', type: 'article',
      format: 'text', status: 'draft', tags: [] })
    await wrapper.get('.btn-retry').trigger('click')
    await flushPromises()
    expect(wrapper.find('.ProseMirror').text()).toContain('Retrouvé')
    wrapper.unmount()
  })
})
