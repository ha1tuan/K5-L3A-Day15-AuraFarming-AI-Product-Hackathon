import type { ApproveInput, QuoteResult, TripInput, TripView } from './types';
import * as demo from './demo';

/** Địa chỉ backend FastAPI. Trống = cùng origin (dev dùng proxy /api của Vite). vd: VITE_API_URL=http://localhost:8000 */
const API = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

/** ?demo=1 hoặc VITE_DEMO=1: chạy bằng dữ liệu mẫu trong trình duyệt (khi backend chưa xong). */
export const DEMO =
  new URLSearchParams(window.location.search).get('demo') === '1' || import.meta.env.VITE_DEMO === '1';

async function post<T>(url: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) throw new Error(`Máy chủ trả lỗi ${res.status}`);
  return res.json() as Promise<T>;
}

export function createTrip(input: TripInput, signal?: AbortSignal): Promise<TripView> {
  return DEMO ? demo.createTrip(input, signal) : post(`${API}/api/trips`, input, signal);
}

export function approveTrip(id: string, body: ApproveInput, signal?: AbortSignal): Promise<TripView> {
  return DEMO ? demo.approveTrip(id, body, signal) : post(`${API}/api/trips/${id}/approve`, body, signal);
}

export async function getTrip(id: string): Promise<TripView> {
  if (DEMO) return demo.getTrip(id);
  const res = await fetch(`${API}/api/trips/${id}`);
  if (!res.ok) throw new Error(`Máy chủ trả lỗi ${res.status}`);
  return res.json() as Promise<TripView>;
}

export function auditQuote(text: string, signal?: AbortSignal): Promise<QuoteResult> {
  if (DEMO) return Promise.reject(new Error('Soát báo giá cần máy chủ (chế độ demo không có).'));
  return post(`${API}/api/quote-audit`, { text }, signal);
}
