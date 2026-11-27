# Web — Kế hoạch du lịch công ty

Vite + React 19 + TypeScript · Tailwind CSS v4 (bố cục, khoảng cách) · SCSS (token màu/chữ, dòng thời gian, bảng so gói, in ấn).
Thiết kế: [`docs/superpowers/specs/2026-11-27-web-ui-design.md`](../../docs/superpowers/specs/2026-11-27-web-ui-design.md).

```bash
npm install
npm run dev            # http://localhost:5173 · /api proxy → :8000 (python run.py)
                       # chưa có backend: mở http://localhost:5173/?demo=1
npm test               # vitest
npm run build          # → dist/ (không commit) — deploy tĩnh, đặt VITE_API_URL trỏ tới backend
```

- **Kết nối backend chỉ qua API.** Dev: proxy `/api` → `BACKEND_URL` (mặc định `http://localhost:8000`). Deploy: `VITE_API_URL=https://api.example.com npm run build`; backend đặt `WEB_ORIGINS` cho CORS. Xem `.env.example`.
- Màu chỉ khai báo ở `src/styles/_tokens.scss`; `src/index.css` đưa chúng vào Tailwind (`bg-accent`, `text-over`…). Component không viết mã hex.
- Kiểu dữ liệu API: `src/api/types.ts` (khớp `codebase/backend/src/api/schemas.py`).
- Chế độ demo (`?demo=1` hoặc `VITE_DEMO=1`): `src/api/demo.ts` giả lập API trong trình duyệt, số tiền vẫn tính bằng code.
