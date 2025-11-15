import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Settings from '@/components/Settings.vue'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn((url) => {
      if (url === '/api/settings/') {
        return Promise.resolve({ data: { tomorrow_io_api_key: 'test-key' } })
      }
      if (url === '/api/ha_entities/') {
        return Promise.resolve({ data: [] })
      }
      return Promise.resolve({ data: [] })
    }),
  },
}));

describe('Settings.vue', () => {
  it('renders the settings heading', () => {
    const wrapper = mount(Settings)
    expect(wrapper.find('h2').text()).toBe('Settings')
  })

  it.skip('fetches and displays the settings', async () => {
    const wrapper = mount(Settings)
    await wrapper.vm.$nextTick() // Wait for the component to update
    await wrapper.vm.$nextTick() // Wait again for the async call to resolve

    const input = wrapper.find('input[type="text"]')
    await input.setValue('new-key')

    expect(input.element.value).toBe('new-key')
  })
})
