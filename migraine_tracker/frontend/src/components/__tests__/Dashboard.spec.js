import { mount } from '@vue/test-utils'
import Dashboard from '../Dashboard.vue'
import { describe, it, expect } from 'vitest'

describe('Dashboard.vue', () => {
  it('renders the dashboard', () => {
    const wrapper = mount(Dashboard)
    expect(wrapper.find('h1').text()).toBe('Dashboard')
  })
})
