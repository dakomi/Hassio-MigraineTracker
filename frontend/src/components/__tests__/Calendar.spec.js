import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Calendar from '@/components/Calendar.vue'

describe('Calendar.vue', () => {
  it('renders the calendar heading', () => {
    const wrapper = mount(Calendar)
    const date = new Date()
    const month = date.toLocaleString('default', { month: 'long' })
    const year = date.getFullYear()
    expect(wrapper.find('h2').text()).toBe(`${month} ${year}`)
  })

  it('displays the correct number of days for a month', async () => {
    const wrapper = mount(Calendar)
    const date = new Date()
    const year = date.getFullYear()
    const month = date.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()

    // The number of day elements should be equal to the number of days in the month
    // plus the number of blank days at the beginning of the month.
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = daysInMonth + firstDay;

    const dayElements = wrapper.findAll('.day')
    expect(dayElements.length).toBe(totalDays)
  })
})
