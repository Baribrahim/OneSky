// frontend/jest.config.cjs
module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.[jt]sx?$': ['@swc/jest', {
      jsc: {
        target: 'es2020',
        parser: {
          syntax: 'ecmascript',   // or 'typescript' if you use TS
          jsx: true,              // <-- critical for .jsx
          // tsx: true,           // <-- use this instead of jsx if TSX
        },
        transform: {
          react: { runtime: 'automatic' },
        },
      },
    }],
  },
  moduleNameMapper: {
    '\\.(css|less|sass|scss)$': 'identity-obj-proxy',
  },
  setupFilesAfterEnv: ['<rootDir>/setupTests.cjs'],
};