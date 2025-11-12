import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 81
  },
  preview: {
    host: '0.0.0.0',
    port: 81
  }
  // test: {
  //   environment: 'jsdom',
  //   globals: true
  // } 
})
