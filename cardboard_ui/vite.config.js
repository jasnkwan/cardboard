import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(
    {
      // Disable React Strict Mode in development
      //reactStrictMode: false,
    }
  )],
  server: {
    host: "127.0.0.1",
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  //build: {
  //  outDir: '../cardboard/resources'
  //},
  resolve: {
    alias: {
      '@': '/src',
    }
  }


})
