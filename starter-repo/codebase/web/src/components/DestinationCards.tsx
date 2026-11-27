import { Bus, Plane, PlayCircle, Info } from 'lucide-react';
import type { DestinationOption, TripEcho } from '../api/types';
import { formatVndShort, TIER_LABEL } from '../lib/format';
import { BudgetBadge, btnGhost, btnPrimary } from './ui';
import { TripEchoLine } from './TripEchoLine';

export function DestinationCards({ request, destinations, onChoose }: {
  request: TripEcho; destinations: DestinationOption[]; onChoose: (name: string) => void;
}) {
  return (
    <section aria-labelledby="dest-h">
      <h1 id="dest-h" className="text-2xl font-bold">Gợi ý địa điểm</h1>
      <div className="mb-2 mt-1"><TripEchoLine e={request} /></div>
      <p className="mb-6 flex items-center gap-2 text-sm text-muted">
        <Info className="size-4" aria-hidden />Chi phí là dự trù cho cả đoàn, đã gồm di chuyển, lưu trú, ăn uống, hoạt động và 5% phát sinh.
      </p>
      <div className="grid gap-5 md:grid-cols-3">
        {destinations.map(d => {
          const Icon = d.transport === 'bus' ? Bus : Plane;
          return (
            <article key={d.name} className={`flex flex-col rounded-xl border bg-card p-5 shadow-sm ${d.recommended ? 'border-accent ring-2 ring-accent/15' : 'border-line'}`}>
              <div className="mb-1 flex items-center gap-2">
                <h2 className="text-lg font-bold">{d.name}</h2>
                {d.recommended && <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-white">Hợp nhất</span>}
              </div>
              <p className="mb-4 flex items-center gap-1 text-sm text-muted"><Icon className="size-4" aria-hidden />{d.travel_time}</p>
              <dl className="mb-4 grid gap-2 text-sm">
                {d.packages.map(p => (
                  <div key={p.tier} className="flex items-center justify-between gap-2">
                    <dt className="text-muted">{TIER_LABEL[p.tier]}</dt>
                    <dd className="flex items-center gap-2 text-right"><b>{formatVndShort(p.total)}</b><BudgetBadge over={p.over_budget} /></dd>
                  </div>
                ))}
              </dl>
              <p className="mb-3 text-sm"><span className="font-medium">Vì sao hợp:</span> {d.why}</p>
              {d.refs.url && (
                <a href={d.refs.url} target="_blank" rel="noreferrer" className="mb-5 inline-flex items-center gap-1 text-sm text-accent hover:underline">
                  <PlayCircle className="size-4" aria-hidden />Tham khảo: {d.refs.articles} bài viết · {d.refs.videos} video
                </a>
              )}
              <button type="button" className={`mt-auto ${d.recommended ? btnPrimary : btnGhost}`} onClick={() => onChoose(d.name)}>
                Chọn {d.name}
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}
