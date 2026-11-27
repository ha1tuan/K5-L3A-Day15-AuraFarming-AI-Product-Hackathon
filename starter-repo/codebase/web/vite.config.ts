import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// Web chạy riêng, nói chuyện với backend FastAPI chỉ qua API.
// dev: proxy /api → BACKEND_URL (mặc định :8000). build → dist/ (không commit), deploy tĩnh; đặt VITE_API_URL trỏ tới backend.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { proxy: { '/api': process.env.BACKEND_URL ?? 'http://localhost:8000' } },
  build: { outDir: 'dist', emptyOutDir: true },
});
