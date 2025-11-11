// setupTests.js (safe, CJS-friendly)
require('@testing-library/jest-dom');
require('whatwg-fetch');

// TextEncoder/TextDecoder (needed by react-router, etc.)
const { TextEncoder, TextDecoder } = require('util');
if (!global.TextEncoder) global.TextEncoder = TextEncoder;
if (!global.TextDecoder) global.TextDecoder = TextDecoder;

// crypto.getRandomValues (some libs need it)
if (!global.crypto) {
  global.crypto = require('crypto').webcrypto;
}

// matchMedia (for components using it)
if (!window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    media: '',
    onchange: null,
    addListener: () => {}, // deprecated but sometimes used
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  });
}

// URL.createObjectURL stub (file inputs, images, etc.)
if (!window.URL.createObjectURL) {
  window.URL.createObjectURL = () => 'blob:jest-mock';
}

// Vite-like env defaults WITHOUT touching import.meta
// Your code can keep using import.meta.env once we transform it (next section),
// but tests also sometimes read process.env directly, so set safe defaults here.
process.env.VITE_API_URL = process.env.VITE_API_URL || 'http://test';
process.env.VITE_SOME_FLAG = process.env.VITE_SOME_FLAG || 'false';

// Mock IntersectionObserver globally for tests
class IntersectionObserverMock {
  constructor(callback, options) {
    this.callback = callback;
    this.options = options;
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.IntersectionObserver = IntersectionObserverMock;


