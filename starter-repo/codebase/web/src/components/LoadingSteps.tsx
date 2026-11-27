import { useEffect, useState } from 'react';
import { CircleCheck, Circle, LoaderCircle } from 'lucide-react';
import { btnGhost } from './ui';

/** Tiến độ ước lượng theo thời gian (API đồng bộ, không báo bước thật). */
export function LoadingSteps({ steps, onCancel }: { steps: string[]; onCancel: () => void }) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI(x => Math.min(x + 1, steps.length - 1)), 6000);
    return () => clearInterval(t);
  }, [steps.length]);
  return (
    <div className="mx-auto max-w-xl rounded-xl border border-line bg-card p-8 shadow-sm" role="status" aria-live="polite">
      <h2 className="mb-1 text-lg font-semibold">Đang xử lý…</h2>
      <p className="mb-6 text-sm text-muted">Thường mất 20–60 giây. Các bước dưới đây chỉ là tiến độ ước lượng.</p>
      <ul className="grid gap-3 text-sm">
        {steps.map((s, k) => (
          <li key={s} className={`flex items-center gap-3 ${k === i ? 'font-medium' : k > i ? 'text-muted' : ''}`}>
            {k < i ? <CircleCheck className="size-5 text-ok" aria-hidden />
              : k === i ? <LoaderCircle className="size-5 animate-spin text-accent" aria-hidden />
              : <Circle className="size-5" aria-hidden />}
            {s}
          </li>
        ))}
      </ul>
      <button type="button" className={`${btnGhost} mt-6`} onClick={onCancel}>Huỷ</button>
    </div>
  );
}
