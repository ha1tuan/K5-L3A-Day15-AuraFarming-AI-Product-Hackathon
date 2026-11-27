import { Check } from 'lucide-react';

const STEPS = ['Thông tin', 'Chọn & duyệt', 'Kế hoạch'];

export function StepBar({ step, skipped }: { step: 1 | 2 | 3; skipped?: boolean }) {
  return (
    <nav aria-label="Các bước" className="no-print bg-card">
      <ol className="mx-auto flex max-w-6xl flex-wrap gap-x-6 gap-y-2 px-4 py-3 text-sm">
        {STEPS.map((label, i) => {
          const n = i + 1;
          const done = n < step, current = n === step;
          const isSkipped = skipped && n === 2;
          return (
            <li key={label} className={`flex items-center gap-2 ${current ? 'font-semibold' : 'text-muted'}`} aria-current={current ? 'step' : undefined}>
              <span className={`grid size-6 place-items-center rounded-full border text-xs ${
                done ? 'border-ok bg-ok text-white' : current ? 'border-accent bg-accent text-white' : 'border-line'}`}>
                {done ? <Check className="size-3.5" aria-hidden /> : n}
              </span>
              {label}
              {isSkipped && <span className="text-xs font-normal text-muted">(bỏ qua — đã có cả kinh phí và địa điểm)</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
