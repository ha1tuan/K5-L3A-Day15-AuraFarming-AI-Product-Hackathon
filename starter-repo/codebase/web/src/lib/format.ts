/** Tiền đầy đủ: 1.250.000đ */
export function formatVnd(n: number): string {
  return Math.round(n).toLocaleString('vi-VN') + 'đ';
}

/** Tiền gọn: 146,2 tr · 1,2 tỷ */
export function formatVndShort(n: number): string {
  const abs = Math.abs(n);
  if (abs >= 1e9) return (n / 1e9).toLocaleString('vi-VN', { maximumFractionDigits: 2 }) + ' tỷ';
  if (abs >= 1e6) return (n / 1e6).toLocaleString('vi-VN', { maximumFractionDigits: 1 }) + ' tr';
  return formatVnd(n);
}

/** "150.000.000" ← "150000000" khi gõ; trả số hoặc null. */
export function parseVnd(s: string): number | null {
  const digits = s.replace(/[^0-9]/g, '');
  return digits ? Number(digits) : null;
}

export function groupDigits(s: string): string {
  const n = parseVnd(s);
  return n === null ? '' : n.toLocaleString('vi-VN');
}

export const TIER_LABEL = { tiet_kiem: 'Tiết kiệm', can_bang: 'Cân bằng', cao_cap: 'Cao cấp' } as const;
export const PURPOSE_LABEL = { gan_ket: 'gắn kết', nghi_duong: 'nghỉ dưỡng', ca_hai: 'nghỉ dưỡng & gắn kết' } as const;

/** yyyy-mm-dd theo giờ máy người dùng. */
export function isoDate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Ngày đi sớm nhất: hôm nay nếu chưa quá 6:00 (kịp xuất phát 7:00), không thì ngày mai. Xa nhất: 1 năm tới. Máy chủ kiểm lại theo giờ VN. */
export function startDateRange(now = new Date()): { min: string; max: string } {
  const min = new Date(now);
  if (now.getHours() >= 6) min.setDate(min.getDate() + 1);
  const max = new Date(now);
  max.setFullYear(max.getFullYear() + 1);
  return { min: isoDate(min), max: isoDate(max) };
}

/** "2026-11-04" → "04/11/2026" */
export function viDate(iso: string): string {
  return iso.length >= 10 ? `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}` : iso;
}
