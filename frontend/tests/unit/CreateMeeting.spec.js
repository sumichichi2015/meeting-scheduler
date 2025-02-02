import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CreateMeeting from '@/components/CreateMeeting.vue';

describe('CreateMeeting', () => {
  it('コンポーネントが正しくマウントされること', () => {
    const wrapper = mount(CreateMeeting);
    expect(wrapper.exists()).toBe(true);
  });

  it('タイトルの入力フィールドが存在すること', () => {
    const wrapper = mount(CreateMeeting);
    const titleInput = wrapper.find('input[name="title"]');
    expect(titleInput.exists()).toBe(true);
  });

  it('説明の入力フィールドが存在すること', () => {
    const wrapper = mount(CreateMeeting);
    const descriptionInput = wrapper.find('textarea[name="description"]');
    expect(descriptionInput.exists()).toBe(true);
  });
});
