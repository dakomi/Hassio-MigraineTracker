import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LogMigraineForm from '@/components/LogMigraineForm.vue'
import VueMultiselect from 'vue-multiselect'
import axios from 'axios'

vi.mock('axios')

describe('LogMigraineForm.vue', () => {
  it('renders the form heading', () => {
    const wrapper = mount(LogMigraineForm)
    expect(wrapper.find('h2').text()).toBe('Log New Migraine')
  })

  it('enables the submit button when the form is valid', async () => {
    const wrapper = mount(LogMigraineForm, {
      global: {
        components: {
          VueMultiselect
        }
      },
      props: {
        painLocationOptions: ['Test Location'],
        symptomOptions: ['Test Symptom'],
        triggerOptions: ['Test Trigger'],
      }
    })

    // Initially, the button is not disabled
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()

    // Fill in the form
    const multiselect = wrapper.findComponent(VueMultiselect)
    await multiselect.vm.select('Test Location')

    // The button should still be enabled
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
  })
})
