import type { ReactNode } from 'react';
import { CircleCheck, TriangleAlert, Info, MessageCircleQuestion, OctagonX } from 'lucide-react';
import { formatVndShort } from '../lib/format';

export function BudgetBadge({ over, size = 'sm' }: { over: number | null; size?: 'sm' | 'md' }) {
  if (over === null) return null;
  const cls = size === 'md' ? 'text-sm px-2.5 py-1' : 'text-xs px-2 py-0.5';
  return over <= 0 ? (
    <span className={`inline-flex items-center gap-1 rounded-full bg-ok-bg text-ok font-medium ${cls}`}>
      <CircleCheck className="size-3.5" aria-hidden /> Trong ngân sách
    </span>
  ) : (
    <span className={`inline-flex items-center gap-1 rounded-full bg-over-bg text-over font-medium ${cls}`}>
      <TriangleAlert className="size-3.5" aria-hidden /> Vượt {formatVndShort(over)}
    </span>
  );
}

const FLAG_TEXT = { estimate: 'ước tính', confirm_rooms: 'cần xác nhận số phòng', confirm_capacity: 'cần xác nhận sức chứa' } as const;
export function Flag({ kind }: { kind: keyof typeof FLAG_TEXT }) {
  return <span className="inline-block rounded bg-est-bg px-1.5 py-0.5 text-xs font-medium text-est">{FLAG_TEXT[kind]}</span>;
}

const TONES = {
  info: { box: 'border-accent/40 bg-accent-soft', icon: Info, color: 'text-accent' },
  ask: { box: 'border-est bg-est-bg', icon: MessageCircleQuestion, color: 'text-est' },
  error: { box: 'border-over bg-over-bg', icon: OctagonX, color: 'text-over' },
} as const;
export function Notice({ tone, title, children, action }: { tone: keyof typeof TONES; title: string; children?: ReactNode; action?: ReactNode }) {
  const t = TONES[tone];
  const Icon = t.icon;
  return (
    <div className={`flex gap-3 rounded-xl border p-4 ${t.box}`} role={tone === 'error' ? 'alert' : 'status'}>
      <Icon className={`mt-0.5 size-5 shrink-0 ${t.color}`} aria-hidden />
      <div className="grid gap-1">
        <p className="font-semibold">{title}</p>
        {children && <div className="text-sm text-muted">{children}</div>}
        {action && <div className="mt-2">{action}</div>}
      </div>
    </div>
  );
}

export const btnPrimary =
  'inline-flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg bg-accent px-6 font-semibold text-white transition hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-60';
export const btnGhost =
  'inline-flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg border border-line bg-card px-4 text-sm font-medium transition hover:bg-soft';
export const inputCls =
  'h-11 w-full rounded-lg border border-line bg-card px-3 transition focus:border-accent aria-[invalid=true]:border-over aria-[invalid=true]:bg-over-bg';
