import { useId } from 'react';
import { ArrowRight, Users, Palmtree, Sparkles, Route } from 'lucide-react';
import type { Field, Purpose } from '../api/types';
import { groupDigits } from '../lib/format';
import { btnPrimary, inputCls, Notice } from './ui';

export interface FormState {
  headcount: string;
  days: number;
  start_date: string;
  origin: string;
  purpose: Purpose | null;
  budget: string;
  budget_per_person: boolean;
  destination: string;
}

const PURPOSES: { v: Purpose; label: string; Icon: typeof Users }[] = [
  { v: 'gan_ket', label: 'Gắn kết đội', Icon: Users },
  { v: 'nghi_duong', label: 'Nghỉ dưỡng', Icon: Palmtree },
  { v: 'ca_hai', label: 'Cả hai', Icon: Sparkles },
];

export function entryHint(f: FormState): { ok: boolean; text: string } {
  const b = !!f.budget.trim(), d = !!f.destination.trim();
  if (b && d) return { ok: true, text: 'Có cả kinh phí và địa điểm → lập luôn 3 kế hoạch chi tiết (tiết kiệm · cân bằng · cao cấp), không cần duyệt.' };
  if (b) return { ok: true, text: 'Chỉ có kinh phí → gợi ý 2–3 địa điểm kèm chi phí 3 gói; bạn chọn rồi mới lập kế hoạch.' };
  if (d) return { ok: true, text: 'Chỉ có địa điểm → dự trù kinh phí 3 gói; bạn chọn gói rồi mới lập kế hoạch.' };
  return { ok: false, text: 'Cần nhập kinh phí hoặc địa điểm (ít nhất một).' };
}

/** Lỗi phía trình duyệt; máy chủ vẫn kiểm lại. */
export function validate(f: FormState): Field[] {
  const out: Field[] = [];
  const n = Number(f.headcount);
  if (!f.headcount || !Number.isInteger(n) || n < 5 || n > 500) out.push('headcount');
  if (!f.origin.trim()) out.push('origin');
  if (!f.purpose) out.push('purpose');
  if (!f.budget.trim() && !f.destination.trim()) out.push('budget_or_destination');
  return out;
}

const ERR: Record<Field, string> = {
  headcount: 'Nhập số người từ 5 đến 500',
  days: 'Chọn số ngày',
  origin: 'Nhập nơi xuất phát',
  purpose: 'Chọn mục đích chuyến đi',
  budget_or_destination: 'Nhập kinh phí hoặc địa điểm',
};

export function TripForm({ value, onChange, onSubmit, errors, askBack }: {
  value: FormState;
  onChange: (f: FormState) => void;
  onSubmit: () => void;
  errors: Field[];
  askBack: boolean;
}) {
  const id = useId();
  const set = <K extends keyof FormState>(k: K, v: FormState[K]) => onChange({ ...value, [k]: v });
  const has = (f: Field) => errors.includes(f);
  const hint = entryHint(value);
  const err = (f: Field) => has(f) && <p id={`${id}-${f}-err`} className="mt-1 text-xs text-over">{ERR[f]}</p>;
  const label = 'mb-1 block text-sm font-medium';

  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold">Lập kế hoạch chuyến đi công ty</h1>
      <p className="mb-6 text-muted">Điền thông tin cơ bản. Có kinh phí, có địa điểm, hoặc cả hai đều được.</p>
      {askBack && errors.length > 0 && (
        <div className="mb-6">
          <Notice tone="ask" title="Cần thêm thông tin trước khi lập kế hoạch">
            Cho mình biết: {errors.map(f => ERR[f].replace(/^Nhập |^Chọn /, '').toLowerCase()).join(', ')}. Các ô cần điền đã được đánh dấu.
          </Notice>
        </div>
      )}
      <form
        noValidate
        className="grid gap-5 rounded-xl border border-line bg-card p-6 shadow-sm"
        onSubmit={e => { e.preventDefault(); onSubmit(); }}
      >
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor={`${id}-hc`} className={label}>Số người <span className="text-over">*</span></label>
            <input id={`${id}-hc`} type="number" inputMode="numeric" min={5} max={500} className={inputCls}
              value={value.headcount} onChange={e => set('headcount', e.target.value)}
              aria-invalid={has('headcount')} aria-describedby={has('headcount') ? `${id}-headcount-err` : undefined} />
            {err('headcount')}
          </div>
          <div>
            <label htmlFor={`${id}-days`} className={label}>Số ngày <span className="text-over">*</span></label>
            <select id={`${id}-days`} className={inputCls} value={value.days} onChange={e => set('days', Number(e.target.value))}>
              {[1, 2, 3, 4, 5].map(d => <option key={d} value={d}>{d === 1 ? '1 ngày (đi về trong ngày)' : `${d} ngày ${d - 1} đêm`}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor={`${id}-date`} className={label}>Ngày đi</label>
            <input id={`${id}-date`} type="date" className={inputCls} value={value.start_date} onChange={e => set('start_date', e.target.value)} />
            <p className="mt-1 text-xs text-muted">Để trống: thứ Sáu gần nhất</p>
          </div>
        </div>

        <div>
          <label htmlFor={`${id}-origin`} className={label}>Xuất phát từ <span className="text-over">*</span></label>
          <input id={`${id}-origin`} className={inputCls} placeholder="vd: Hà Nội" value={value.origin} onChange={e => set('origin', e.target.value)}
            aria-invalid={has('origin')} aria-describedby={has('origin') ? `${id}-origin-err` : undefined} />
          {err('origin')}
        </div>

        <fieldset aria-invalid={has('purpose')}>
          <legend className="mb-2 text-sm font-medium">Mục đích chính <span className="text-over">*</span></legend>
          <div className="flex flex-wrap gap-2">
            {PURPOSES.map(({ v, label: l, Icon }) => (
              <label key={v} className="cursor-pointer">
                <input type="radio" name={`${id}-purpose`} className="peer sr-only" checked={value.purpose === v} onChange={() => set('purpose', v)} />
                <span className={`inline-flex h-11 items-center gap-2 rounded-lg border px-4 transition peer-checked:border-accent peer-checked:bg-accent-soft peer-checked:text-accent peer-focus-visible:outline-3 peer-focus-visible:outline-accent ${has('purpose') ? 'border-over' : 'border-line'}`}>
                  <Icon className="size-4" aria-hidden />{l}
                </span>
              </label>
            ))}
          </div>
          {err('purpose')}
        </fieldset>

        <div className="border-t border-line pt-5">
          <p className="mb-3 text-sm font-semibold">Bạn đã có gì? <span className="font-normal text-muted">(ít nhất một)</span></p>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor={`${id}-budget`} className={label}>Kinh phí dự trù</label>
              <div className="flex">
                <input id={`${id}-budget`} inputMode="numeric" className={`${inputCls} rounded-r-none`} placeholder="vd: 150.000.000"
                  value={value.budget} onChange={e => set('budget', groupDigits(e.target.value))} aria-invalid={has('budget_or_destination')} />
                <span className="grid h-11 place-items-center rounded-r-lg border border-l-0 border-line bg-soft px-3">đ</span>
              </div>
              <div className="mt-2 flex gap-4 text-sm" role="radiogroup" aria-label="Kinh phí tính cho">
                <label className="flex items-center gap-1.5"><input type="radio" checked={!value.budget_per_person} onChange={() => set('budget_per_person', false)} /> tổng đoàn</label>
                <label className="flex items-center gap-1.5"><input type="radio" checked={value.budget_per_person} onChange={() => set('budget_per_person', true)} /> mỗi người</label>
              </div>
            </div>
            <div>
              <label htmlFor={`${id}-dest`} className={label}>Địa điểm</label>
              <input id={`${id}-dest`} className={inputCls} placeholder="vd: Hạ Long" value={value.destination}
                onChange={e => set('destination', e.target.value)} aria-invalid={has('budget_or_destination')} />
              <p className="mt-2 text-xs text-muted">Để trống nếu muốn được gợi ý.</p>
            </div>
          </div>
          {err('budget_or_destination')}
        </div>

        <div className={`flex gap-2 rounded-lg border p-3 text-sm ${hint.ok ? 'border-accent/30 bg-accent-soft' : 'border-over/40 bg-over-bg text-over'}`} aria-live="polite">
          <Route className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
          <span>Hệ thống sẽ: {hint.text}</span>
        </div>

        <div className="flex justify-end">
          <button type="submit" className={btnPrimary}>Lập kế hoạch <ArrowRight className="size-4" aria-hidden /></button>
        </div>
      </form>
    </div>
  );
}
