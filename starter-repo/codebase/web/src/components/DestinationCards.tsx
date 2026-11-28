import { Bus, Plane, PlayCircle, Info, RefreshCw, RotateCcw } from 'lucide-react';
import type { DestinationOption, TripEcho } from '../api/types';
import { formatVndShort, TIER_LABEL } from '../lib/format';
import { BudgetBadge, btnGhost, btnPrimary } from './ui';
import { TripEchoLine } from './TripEchoLine';

export function DestinationCards({ request, destinations, onChoose, onMore, seen = [], hasMore = false, message }: {
  request: TripEcho; destinations: DestinationOption[]; onChoose: (name: string) => void;
  /** Gọi lại gợi ý, bỏ các nơi trong danh sách (rỗng = xem lại từ đầu). Không có = ẩn nút (chế độ demo). */
  onMore?: (exclude: string[]) => void; seen?: string[]; hasMore?: boolean; message?: string;
}) {
  const earlier = seen.filter(n => !destinations.some(d => d.name === n));
  return (
    <section aria-labelledby="dest-h">
      <div className="flex flex-wrap items-center gap-3">
        <h1 id="dest-h" className="text-2xl font-bold">Gợi ý địa điểm</h1>
        {onMore && destinations.length > 0 && (
          <button type="button" className={`ml-auto ${btnGhost}`} disabled={!hasMore} onClick={() => onMore(seen)}
            title={hasMore ? 'Bỏ các nơi đang xem, gợi ý 3 nơi khác vẫn hợp ngân sách và mục đích' : 'Đã gợi ý hết các nơi phù hợp trong dữ liệu'}>
            <RefreshCw className="size-4" aria-hidden />{hasMore ? 'Gợi ý nơi khác' : 'Hết nơi phù hợp'}
          </button>
        )}
      </div>
      {earlier.length > 0 && (
        <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-muted">
          Đã xem trước: {earlier.join(', ')}
          {onMore && <button type="button" className="inline-flex cursor-pointer items-center gap-1 font-medium text-accent hover:underline" onClick={() => onMore([])}>
            <RotateCcw className="size-3.5" aria-hidden />Xem lại từ đầu</button>}
        </p>
      )}
      {destinations.length === 0 && (
        <div className="mt-4 rounded-xl bg-soft p-5 text-sm">
          <p>{message}</p>
          {onMore && <button type="button" className={`mt-3 ${btnPrimary}`} onClick={() => onMore([])}><RotateCcw className="size-4" aria-hidden />Xem lại từ đầu</button>}
        </div>
      )}
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
