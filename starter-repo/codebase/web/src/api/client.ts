import type { ApproveInput, QuoteResult, RecalcInput, Tier, TripInput, TripView } from './types';
import * as demo from './demo';

/** Địa chỉ backend FastAPI. Trống = cùng origin (dev dùng proxy /api của Vite). vd: VITE_API_URL=http://localhost:8000 */
const API = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

/** ?demo=1 hoặc VITE_DEMO=1: chạy bằng dữ liệu mẫu trong trình duyệt (khi backend chưa xong). */
export const DEMO =
  (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('demo') === '1') || import.meta.env.VITE_DEMO === '1';

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

export type ChatMsg = { role: 'user' | 'assistant'; content: string };
/** Trợ lý Aura (POST /api/chat): báo giá → soát; yêu cầu chuyến đi → agent; còn lại → hỏi đáp. */
export function chat(messages: ChatMsg[], signal?: AbortSignal): Promise<{ reply: string; kind: string }> {
  if (DEMO) return Promise.resolve({ reply: 'Chế độ demo chưa nối trợ lý — chạy cùng máy chủ để trò chuyện với Aura.', kind: 'faq' });
  return post(`${API}/api/chat`, { messages }, signal);
}

/** Sửa gói ngay trên trang kế hoạch → tính lại (trả view mới, trip_id mới). */
export function recalcTrip(id: string, body: RecalcInput, signal?: AbortSignal): Promise<TripView> {
  return post(`${API}/api/trips/${id}/recalc`, body, signal);
}

/** Đối chiếu báo giá tour với gói đã lập. */
export function quoteForTrip(id: string, text: string, tier: Tier, signal?: AbortSignal): Promise<QuoteResult> {
  return post(`${API}/api/trips/${id}/quote`, { text, tier }, signal);
}

export const exportUrl = (id: string) => `${API}/api/trips/${id}/export.xlsx`;

export interface Estimate { status: 'ok' | 'skip'; origin?: string; destination?: string; tiers?: { tier: Tier; total: number; per_person: number }[] }
export async function estimate(q: { origin: string; destination: string; headcount: number; days: number; purpose?: string | null }, signal?: AbortSignal): Promise<Estimate> {
  if (DEMO) return { status: 'skip' };
  const p = new URLSearchParams({ origin: q.origin, destination: q.destination, headcount: String(q.headcount), days: String(q.days), purpose: q.purpose ?? 'ca_hai' });
  const res = await fetch(`${API}/api/estimate?${p}`, { signal });
  return res.ok ? res.json() : { status: 'skip' };
}
