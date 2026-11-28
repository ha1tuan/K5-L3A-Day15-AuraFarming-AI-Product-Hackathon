import { useEffect, useState } from 'react';
import { CircleCheck, Circle, LoaderCircle } from 'lucide-react';
import { btnGhost } from './ui';

const Bone = ({ className }: { className: string }) => <div className={`animate-pulse rounded-2xl bg-soft ${className}`} />;

/** Tiến độ ước lượng theo thời gian (API đồng bộ, không báo bước thật) + khung xương đúng bố cục trang kết quả. */
export function LoadingSteps({ steps, onCancel }: { steps: string[]; onCancel: () => void }) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI(x => Math.min(x + 1, steps.length - 1)), 2500);
    return () => clearInterval(t);
  }, [steps.length]);
  return (
    <div className="grid gap-6" role="status" aria-live="polite">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 rounded-3xl bg-card p-5 shadow-sm ring-1 ring-black/5">
        <p className="font-bold">Đang lập kế hoạch…</p>
        <ul className="flex flex-1 flex-wrap gap-x-5 gap-y-2 text-sm">
          {steps.map((s, k) => (
            <li key={s} className={`flex items-center gap-2 ${k === i ? 'font-semibold' : k > i ? 'text-muted' : ''}`}>
              {k < i ? <CircleCheck className="size-4 text-ok" aria-hidden />
                : k === i ? <LoaderCircle className="size-4 animate-spin text-accent" aria-hidden />
                : <Circle className="size-4" aria-hidden />}
              {s}
            </li>
          ))}
        </ul>
        <button type="button" className={btnGhost} onClick={onCancel}>Huỷ</button>
      </div>
      <div aria-hidden className="grid gap-6">
        <div className="flex flex-wrap gap-2 rounded-3xl bg-card p-3 ring-1 ring-black/5">
          <Bone className="h-16 w-40" /><Bone className="h-16 w-40" /><Bone className="h-16 w-40" />
          <div className="ml-auto flex gap-2"><Bone className="h-10 w-28 rounded-full" /><Bone className="h-10 w-28 rounded-full" /></div>
        </div>
        <Bone className="h-44 w-full rounded-3xl" />
        <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
          <div className="grid gap-3">{[0, 1, 2, 3, 4].map(k => <Bone key={k} className="h-14 w-full" />)}</div>
          <div className="grid content-start gap-3"><Bone className="h-64 w-full rounded-3xl" /><Bone className="h-40 w-full rounded-3xl" /></div>
        </div>
      </div>
    </div>
  );
}
