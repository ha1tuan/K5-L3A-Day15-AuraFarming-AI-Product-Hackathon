import type { Package } from '../api/types';
import { formatVndShort, TIER_LABEL } from '../lib/format';

const GROUPS = [
  { key: 'Di chuyển', color: '#0e7490' },
  { key: 'Lưu trú', color: '#22a3c4' },
  { key: 'Ăn uống', color: '#f97316' },
  { key: 'Hoạt động', color: '#fbbf24' },
  { key: 'Phát sinh', color: '#94a3b8' },
] as const;

/** Biểu đồ cột chồng so 3 gói theo hạng mục + vạch ngân sách — nhìn một lần thấy gói nào vượt, vượt vì khoản nào. */
export function CostChart({ packages, budget }: { packages: Package[]; budget: number | null }) {
  const rows = packages.map(p => {
    const by: Record<string, number> = {};
    for (const li of p.line_items) {
      const k = GROUPS.find(g => li.category.startsWith(g.key))?.key ?? 'Hoạt động';
      by[k] = (by[k] ?? 0) + li.amount;
    }
    return { p, by };
  });
  const max = Math.max(...packages.map(p => p.total), budget ?? 0) * 1.08 || 1;
  const pct = (v: number) => `${(100 * v) / max}%`;

  return (
    <figure className="rounded-3xl bg-card p-5 shadow-sm ring-1 ring-black/5 sm:p-6">
      <figcaption className="mb-4 flex flex-wrap items-center gap-x-5 gap-y-2">
        <span className="text-base font-bold">So sánh 3 gói theo hạng mục</span>
        <span className="flex flex-wrap gap-3 text-xs text-muted">
          {GROUPS.map(g => <span key={g.key} className="inline-flex items-center gap-1.5"><span className="size-2.5 rounded-sm" style={{ background: g.color }} />{g.key}</span>)}
          {budget !== null && <span className="inline-flex items-center gap-1.5"><span className="h-3 w-0.5 bg-over" />Ngân sách</span>}
        </span>
      </figcaption>
      <div className="relative grid gap-4">
        {budget !== null && (
          <div className="pointer-events-none absolute inset-y-0 z-10 ml-[6.5rem] w-[calc(100%-6.5rem)]" aria-hidden>
            <div className="absolute inset-y-[-6px] w-0.5 bg-over" style={{ left: pct(budget) }}>
              <span className="absolute -top-5 -translate-x-1/2 whitespace-nowrap rounded bg-over px-1.5 text-[10px] font-semibold text-white">{formatVndShort(budget)}</span>
            </div>
          </div>
        )}
        {rows.map(({ p, by }) => {
          const over = p.over_budget !== null && p.over_budget > 0;
          return (
            <div key={p.tier} className="grid grid-cols-[6rem_1fr] items-center gap-2">
              <div className="text-sm">
                <p className="font-semibold">{TIER_LABEL[p.tier]}</p>
                <p className={`text-xs ${over ? 'text-over' : 'text-muted'}`}>{formatVndShort(p.total)}</p>
              </div>
              <div className="flex h-9 overflow-hidden rounded-xl bg-soft" role="img"
                aria-label={`${TIER_LABEL[p.tier]}: ${GROUPS.map(g => `${g.key} ${formatVndShort(by[g.key] ?? 0)}`).join(', ')}`}>
                {GROUPS.map(g => (by[g.key] ?? 0) > 0 && (
                  <div key={g.key} className="group relative h-full transition-all duration-700" style={{ width: pct(by[g.key]), background: g.color }}
                    title={`${g.key}: ${formatVndShort(by[g.key])}`}>
                    {(by[g.key] / max) > 0.09 && <span className="absolute inset-0 grid place-items-center truncate px-1 text-[10px] font-semibold text-white">{formatVndShort(by[g.key])}</span>}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </figure>
  );
}
