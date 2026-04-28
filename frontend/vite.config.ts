import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load env so VITE_PROXY_TARGET is available at config time
  const env = loadEnv(mode, process.cwd(), '');
  const proxyTarget = env.VITE_PROXY_TARGET ?? 'http://localhost:8000';

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/auth': proxyTarget,
        '/conversations': proxyTarget,
        '/ws': { target: proxyTarget.replace(/^http/, 'ws'), ws: true },
      },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/__tests__/setup.ts'],
      globals: true,
    },
  };
});
