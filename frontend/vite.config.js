import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            // 后端断开时吞掉错误，防止 Vite 进程崩溃
            if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET') {
              console.warn('[proxy] backend unavailable:', err.code)
            } else {
              console.error('[proxy] error:', err.message)
            }
          })
        }
      },
      '/socket.io': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET') {
              console.warn('[ws-proxy] backend unavailable:', err.code)
            } else {
              console.error('[ws-proxy] error:', err.message)
            }
          })
        }
      }
    }
  }
})
