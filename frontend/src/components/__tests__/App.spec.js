import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import App from '../../App.vue'

describe('App.vue', () => {
  it('renders the sidebar and navigation links', () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>'
          },
          RouterView: true
        }
      }
    })

    expect(wrapper.find('.sidebar').exists()).toBe(true)
    expect(wrapper.text()).toContain('YT Music Sync')
    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('Playlists')
    expect(wrapper.text()).toContain('Settings')
  })
})
