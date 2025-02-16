import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      outDir: '../backend/static',
      emptyOutDir: true,
      assetsDir: 'assets',
    },
    server: {
      port: parseInt(env.FRONTEND_PORT || 5173),
      proxy: {
        '/api': {
          target: `http://localhost:${env.BACKEND_PORT || 8000}`,
          changeOrigin: true,
        },
        '/token': {
          target: `http://localhost:${env.BACKEND_PORT || 8000}`,
          changeOrigin: true,
        },
        '/register': {
          target: `http://localhost:${env.BACKEND_PORT || 8000}`,
          changeOrigin: true,
        },
      },
    },
  }
})
