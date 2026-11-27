import { TriangleAlert } from 'lucide-react';
import type { Explanation, Tier } from '../api/types';
import { formatVnd, formatVndShort, TIER_LABEL } from '../lib/format';

/** Chữ và số lấy nguyên từ máy chủ — web không tự tính. */
export function OverBudget({ tier, ex, budget }: { tier: Tier; ex: Explanation; budget: number }) {
  return (
    <section className="rounded-xl border border-over bg-over-bg p-5" aria-labelledby={`ob-${tier}`}>
      <h3 id={`ob-${tier}`} className="flex items-center gap-2 font-semibold text-over">
        <TriangleAlert className="size-5" aria-hidden />Vì sao gói {TIER_LABEL[tier]} vượt ngân sách?
      </h3>
      <p className="mt-1">Vượt <b>{formatVnd(ex.over_amount)} ({ex.over_pct}%)</b> so với ngân sách {formatVnd(budget)}.</p>
      {ex.min_budget !== undefined && (
        <p className="mt-1 text-sm">Không gói nào nằm trong ngân sách. Ngân sách tối thiểu cần có: <b>{formatVnd(ex.min_budget)}</b>.</p>
      )}
      <div className="mt-4 grid gap-6 text-sm md:grid-cols-2">
        <div>
          <p className="mb-2 font-medium">Nguyên nhân chính{ex.compared_to ? ` so với gói ${TIER_LABEL[ex.compared_to]}` : ''}</p>
          <ul className="grid gap-2">
            {ex.drivers.map(d => (
              <li key={d.label} className="flex justify-between gap-3 rounded-lg bg-card px-3 py-2"><span>{d.label}</span><b className="shrink-0">+{formatVnd(d.amount)}</b></li>
            ))}
          </ul>
        </div>
        <div>
          <p className="mb-2 font-medium">Cách đưa về gần ngân sách</p>
          <ul className="grid gap-2">
            {ex.cuts.map(c => (
              <li key={c.label} className="flex justify-between gap-3 rounded-lg bg-card px-3 py-2">
                <span>{c.label}</span>
                <span className="shrink-0 text-right">
                  <b className="text-ok">−{formatVnd(c.saving)}</b><br />
                  <span className="text-xs text-muted">còn {formatVndShort(c.total_after)}{c.total_after > budget ? ` · vẫn vượt ${formatVndShort(c.total_after - budget)}` : ' · vừa ngân sách'}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
