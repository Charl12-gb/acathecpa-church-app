import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ContentEditor from '../../src/components/content/ContentEditor.vue'
import ContentEditorPage from '../../src/views/dashboard/content/ContentEditorPage.vue'
import { useContentStore } from '../../src/stores/content'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() } }))

// ProseMirror measures the DOM; jsdom has no layout.
beforeEach(() => {
  setActivePinia(createPinia())
  window.scrollTo = (() => undefined) as any
  ;(document as any).elementFromPoint = () => null
  Range.prototype.getClientRects = () => ({ length: 0, item: () => null, [Symbol.iterator]: [][Symbol.iterator] }) as any
  Range.prototype.getBoundingClientRect = () => ({ top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0 }) as any
})

describe('ContentEditor tables', () => {
  it('inserts a table and edits rows from the table toolbar', async () => {
    const wrapper = mount(ContentEditor, { props: { modelValue: '<p>Intro</p>' }, attachTo: document.body })
    await flushPromises()
    expect(wrapper.find('.table-toolbar').exists()).toBe(false)

    await wrapper.get('button[aria-label="Insérer un tableau"]').trigger('click')
    await flushPromises()
    const html = () => wrapper.emitted('update:modelValue')!.at(-1)![0] as string
    expect(html()).toContain('<table')
    expect((html().match(/<tr>/g) || []).length).toBe(3)
    expect(html()).toContain('<th')

    // The cursor is in the new table: its toolbar is shown.
    expect(wrapper.find('.table-toolbar').exists()).toBe(true)
    await wrapper.findAll('.tt-btn').find(b => b.text() === '+ Ligne')!.trigger('click')
    expect((html().match(/<tr>/g) || []).length).toBe(4)
    await wrapper.findAll('.tt-btn').find(b => b.text() === 'Supprimer le tableau')!.trigger('click')
    expect(html()).not.toContain('<table')
    wrapper.unmount()
  })

  it('shows an existing table loaded from the server', async () => {
    const wrapper = mount(ContentEditor, { props: { modelValue: '' }, attachTo: document.body })
    await wrapper.setProps({ modelValue: '<table><tbody><tr><th><p>Taux</p></th></tr><tr><td><p>18 %</p></td></tr></tbody></table>' })
    await flushPromises()
    expect(wrapper.find('.ProseMirror table').exists()).toBe(true)
    expect(wrapper.find('.ProseMirror').text()).toContain('18 %')
    wrapper.unmount()
  })
})

describe('ContentEditorPage', () => {
  const apiContent = {
    id: 5, title: 'La TVA', description: 'Résumé', content_body: '<p>Texte existant de l’article</p>',
    type: 'article', format: 'text', media_url: null, is_premium: true, price: 1500,
    status: 'draft', tags: ['fiscalité'],
  }

  it('loads the saved text into the editor and updates the same content', async () => {
    const store = useContentStore()
    vi.spyOn(store, 'getContent').mockResolvedValue(apiContent as any)
    const save = vi.spyOn(store, 'saveContent').mockResolvedValue({} as any)
    const router = await makeRouter(ContentEditorPage, [{ path: '/content/editor/:id?' }, { path: '/my-content' }], '/content/editor/5')
    const wrapper = mount(ContentEditorPage, { global: { plugins: [router] }, attachTo: document.body })
    await flushPromises()

    expect(wrapper.find('.ProseMirror').text()).toContain('Texte existant de l’article')

    await wrapper.get('.btn-next').trigger('click')
    await wrapper.findAll('.btn-save')[0].trigger('click')
    await flushPromises()
    expect(save).toHaveBeenCalledWith(expect.objectContaining({
      title: 'La TVA', content_body: '<p>Texte existant de l’article</p>', is_premium: true, price: 1500,
      media_url: null, tags: ['fiscalité'],
    }), 5)
    wrapper.unmount()
  })
})
