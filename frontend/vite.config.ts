import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  // 加载根目录下的 .env(.development/.production) 文件
  const env = loadEnv(mode, process.cwd(), '')

  return {
    base: './',
    build: {
      assetsDir: 'assets',  // 明确指定 assets 目录
    },
    plugins: [
      vue(),
      // vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      // 在本地部署和虚拟机部署的时候切换
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        }
        // '/api': {
        //   target: 'http://172.20.41.146:5000',
        //   changeOrigin: true,
        // }
      }
    }
  }
})
