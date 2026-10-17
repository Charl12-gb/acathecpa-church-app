import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CertificateVerifyPage from '../../src/views/public/CertificateVerifyPage.vue'
import * as api from '../../src/services/api/course'
import { makeRouter } from './helpers'

vi.mock('../../src/services/api/course', () => ({ verifyCertificate: vi.fn() }))
const mocked = vi.mocked(api)

const routes = [{ path: '/certificates/verify/:code?', name: 'certificate-verify' }]

async function mountAt(path: string) {
  const router = await makeRouter(CertificateVerifyPage, routes, path)
  const wrapper = mount(CertificateVerifyPage, { global: { plugins: [router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('CertificateVerifyPage', () => {
  it('confirms a valid certificate from the link', async () => {
    mocked.verifyCertificate.mockResolvedValue({
      verification_code: 'CERT-3F9A2C71B0', holder_name: 'Awa Koné',
      course_title: 'Comptabilité OHADA', issue_date: '2026-10-17T09:00:00Z', valid: true,
    })
    const { wrapper } = await mountAt('/certificates/verify/CERT-3F9A2C71B0')

    expect(mocked.verifyCertificate).toHaveBeenCalledWith('CERT-3F9A2C71B0')
    expect(wrapper.text()).toContain('Certificat authentique')
    expect(wrapper.text()).toContain('Awa Koné')
    expect(wrapper.text()).toContain('Comptabilité OHADA')
    expect(wrapper.text()).toContain('17 octobre 2026')
  })

  it('says when no certificate matches', async () => {
    mocked.verifyCertificate.mockRejectedValue({ response: { status: 404 } })
    const { wrapper } = await mountAt('/certificates/verify/CERT-FAUX')
    expect(wrapper.get('.alert-danger').text()).toContain('Aucun certificat ne correspond au code « CERT-FAUX »')
  })

  it('puts a typed code in the URL so the result can be shared', async () => {
    mocked.verifyCertificate.mockRejectedValue({ response: { status: 404 } })
    const { wrapper, router } = await mountAt('/certificates/verify')
    expect(mocked.verifyCertificate).not.toHaveBeenCalled()

    await wrapper.get('#cert-code').setValue('CERT-ABC')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/certificates/verify/CERT-ABC')
    expect(mocked.verifyCertificate).toHaveBeenCalledWith('CERT-ABC')
  })
})
