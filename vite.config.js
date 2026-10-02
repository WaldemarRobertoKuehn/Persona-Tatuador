import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { apiMiddleware } from './api-middleware.js'

function apiPlugin() {
  return {
    name: 'api-server',
    configureServer(server) {
      server.middlewares.use(apiMiddleware)
    },
    configurePreviewServer(server) {
      server.middlewares.use(apiMiddleware)
    },
  }
}

export default defineConfig({
  plugins: [react(), apiPlugin()],
  publicDir: 'docs/marca',
  server: {
    host: '0.0.0.0',
    port: 3000,
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
  },
})
