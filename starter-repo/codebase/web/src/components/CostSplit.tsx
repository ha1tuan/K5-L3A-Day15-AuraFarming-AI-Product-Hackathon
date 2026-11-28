import { useState } from 'react';
import { Info } from 'lucide-react';
import type { Plan, TripEcho } from '../api/types';
import { formatVnd } from '../lib/format';
import { inputCls } from './ui';

/** Chia tiền: công ty trả cho nhân viên, người thân tự đóng (trẻ em theo tuổi). Tính trên giá / người của gói đang xem. */
export function CostSplit({ plan, request }: { plan: Plan; request: TripEcho }) {
  const [staff, setStaff] = useState(String(request.headcount));
  const [adults, setAdults] = useState('0');
  const [kids, setKids] = useState('0');
  const [babies, setBabies] = useState('0');
  const [support, setSupport] = useState('0');
  const n = (s: string) => Math.max(0, Math.floor(Number(s) || 0));
  const s = n(staff), a = n(adults), k = n(kids), b = n(babies), sp = Math.min(100, n(support));
  const unit = plan.per_person;
  const kid = Math.round(unit * 0.5 / 1000) * 1000;
  const fam = a * unit + k * kid;
  const companyFam = Math.round(fam * sp / 100 / 1000) * 1000;
  const company = s * unit + companyFam;
  const people = s + a + k + b;
  const mismatch = s + a + k !== request.headcount;
  const field = (label: string, v: string, set: (x: string) => void, hint?: string) => (
    <label className="grid gap-1 text-sm">
      <span className="font-medium">{label}</span>
      <input type="number" min={0} className={`${inputCls} w-full`} value={v} onChange={e => set(e.target.value)} />
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </label>
  );
  return (
    <div className="grid gap-5">
      <div className="grid gap-4 sm:grid-cols-5">
        {field('Nhân viên', staff, setStaff, 'công ty trả')}
        {field('Người thân (người lớn)', adults, setAdults, 'giá như người lớn')}
        {field('Trẻ 5–11 tuổi', kids, setKids, 'tạm tính 50%')}
        {field('Trẻ dưới 5 tuổi', babies, setBabies, 'tạm tính miễn phí')}
        {field('Công ty hỗ trợ người thân', support, setSupport, '% (0–100)')}
      </div>
      {mismatch && (
        <p className="flex gap-2 rounded-xl bg-est-bg px-3 py-2 text-xs text-est">
          <Info className="size-4 shrink-0" aria-hidden />
          Kế hoạch đang tính cho {request.headcount} người, còn ở đây là {s + a + k} người trả phí. Nếu người thân đi cùng, hãy sửa số người ở mục "Tùy chỉnh" để tiền phòng, xe tính đúng.
        </p>
      )}
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl bg-accent-soft p-4"><p className="text-xs text-muted">Công ty chi</p><p className="text-2xl font-extrabold text-accent-dark">{formatVnd(company)}</p>
          <p className="text-xs text-muted">{s} nhân viên × {formatVnd(unit)}{companyFam ? ` + hỗ trợ ${sp}% người thân` : ''}</p></div>
        <div className="rounded-2xl bg-sun-soft p-4"><p className="text-xs text-muted">Người thân tự đóng</p><p className="text-2xl font-extrabold text-sun-dark">{formatVnd(fam - companyFam)}</p>
          <p className="text-xs text-muted">mỗi người lớn {formatVnd(Math.round(unit * (100 - sp) / 100 / 1000) * 1000)} · mỗi trẻ 5–11 {formatVnd(Math.round(kid * (100 - sp) / 100 / 1000) * 1000)}</p></div>
        <div className="rounded-2xl bg-soft p-4"><p className="text-xs text-muted">Tổng người đi</p><p className="text-2xl font-extrabold">{people} người</p>
          <p className="text-xs text-muted">{b ? `${b} trẻ dưới 5 tuổi miễn phí` : 'chưa có trẻ dưới 5 tuổi'}</p></div>
      </div>
      <p className="text-xs text-muted">Giá / người lấy từ gói đang xem ({formatVnd(unit)}). Mức trẻ em 50% / miễn phí là quy ước tạm tính — mỗi công ty tour, khách sạn có chính sách riêng, cần hỏi lại.</p>
    </div>
  );
}
