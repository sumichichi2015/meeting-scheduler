import { expect, afterEach } from 'vitest';
import { cleanup } from '@vue/test-utils';
import matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
