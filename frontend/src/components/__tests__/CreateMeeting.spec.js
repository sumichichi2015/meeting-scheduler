import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import CreateMeeting from '../CreateMeeting.vue'
import { useMeetingStore } from '../../stores/meetingStore'

describe('CreateMeeting', () => {
  const mountComponent = () => {
    return mount(CreateMeeting, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            meeting: {
              meetings: [],
              loading: false,
              error: null
            }
          }
        })]
      }
    })
  }

  it('初期状態でフォームが空であること', () => {
    const wrapper = mountComponent()
    const titleInput = wrapper.find('input[name="title"]')
    expect(titleInput.element.value).toBe('')
  })

  it('必須項目が未入力の場合、エラーが表示されること', async () => {
    const wrapper = mountComponent()
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('必須項目')
  })

  it('会議作成が成功した場合、ストアのcreateメソッドが呼ばれること', async () => {
    const wrapper = mountComponent()
    const store = useMeetingStore()
    
    await wrapper.find('input[name="title"]').setValue('テスト会議')
    await wrapper.find('form').trigger('submit.prevent')
    
    expect(store.createMeeting).toHaveBeenCalledWith({
      title: 'テスト会議'
    })
  })
})
