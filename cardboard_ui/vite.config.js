import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
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
  build: {
    manifest: true,
    lib: {
      // Entry point for your library
      entry: path.resolve(__dirname, 'src/index.jsx'), // Replace with your entry file
      name: 'cardboard-ui',  // Global name for UMD builds
      formats: ['es', 'umd'], // ES module and UMD formats
      fileName: (format) => `cardboard-ui.${format}.js`
    },
    rollupOptions: {
      // Externalize peer dependencies
      external: ['react', 'react-dom', 'axios', 'plotly.js', 'react-plotly.js'],
      output: {
        globals: {
          'react': 'React',
          'react-dom': 'ReactDOM',
          'axios': 'axios',
          'react-plotly.js': 'Plot', 
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    }
  }


})
