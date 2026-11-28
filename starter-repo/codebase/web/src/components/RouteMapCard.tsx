import { lazy, Suspense, useEffect, useState } from 'react';
import { Maximize2, X, Bus, Plane } from 'lucide-react';
import type { Tier, TripView } from '../api/types';
import { TIER_LABEL } from '../lib/format';

const TripMap = lazy(() => import('./TripMap').then(m => ({ default: m.TripMap })));   // Leaflet chỉ tải khi có bản đồ
const Skeleton = ({ h }: { h: string }) => <div className={`${h} w-full animate-pulse rounded-3xl bg-soft`} />;

/** Bản đồ lộ trình thu nhỏ dưới lịch trình; bấm để phóng to ở giữa màn hình (kèm danh sách chặng). */
export function RouteMapCard({ map, tier }: { map: NonNullable<TripView['map']>; tier: Tier }) {
  const [big, setBig] = useState(false);
  const legs = map.routes?.[tier] ?? [];
  useEffect(() => {
    if (!big) return;
    const k = (e: KeyboardEvent) => e.key === 'Escape' && setBig(false);
    window.addEventListener('keydown', k);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', k); document.body.style.overflow = ''; };
  }, [big]);
  const flight = legs.some(l => l.mode === 'flight');
  const km = legs.reduce((s, l) => s + (l.vehicle.startsWith('Tự') ? 0 : l.km ?? 0), 0);

  return (
    <section className="no-print mt-6">
      <div className="mb-3 flex items-end gap-3">
        <div>
          <h3 className="text-lg font-bold">Bản đồ lộ trình</h3>
          <p className="flex items-center gap-1.5 text-sm text-muted">
            {flight ? <Plane className="size-4" aria-hidden /> : <Bus className="size-4" aria-hidden />}
            {map.origin.name} → {map.dest.name} · {legs.length} chặng{km ? ` · ~${km.toLocaleString('vi-VN')} km` : ''} · gói {TIER_LABEL[tier]}
          </p>
        </div>
      </div>
      <button type="button" onClick={() => setBig(true)} aria-label="Phóng to bản đồ lộ trình"
        className="group relative isolate block w-full cursor-zoom-in overflow-hidden rounded-3xl text-left ring-1 ring-black/5 transition hover:shadow-xl">
        <Suspense fallback={<Skeleton h="h-72" />}><TripMap map={map} tier={tier} compact /></Suspense>
        <span className="pointer-events-none absolute inset-0 z-[500] bg-gradient-to-t from-ocean/50 via-transparent to-transparent opacity-80 transition group-hover:opacity-100" />
        <span className="pointer-events-none absolute bottom-4 right-4 z-[700] inline-flex items-center gap-2 rounded-full bg-white/95 px-4 py-2 text-sm font-semibold text-ocean shadow-lg transition group-hover:scale-105">
          <Maximize2 className="size-4" aria-hidden />Bấm để phóng to
        </span>
      </button>

      {big && (
        <div className="backdrop-in fixed inset-0 z-[1000] grid place-items-center bg-ocean/70 p-3 backdrop-blur-sm sm:p-6" role="dialog" aria-modal="true"
          aria-label="Bản đồ lộ trình" onClick={() => setBig(false)}>
          <div className="fade-up flex max-h-full w-full max-w-6xl flex-col overflow-hidden rounded-3xl bg-bg shadow-2xl" onClick={e => e.stopPropagation()}>
            <header className="app-hero flex items-center gap-3 px-5 py-3.5 text-white">
              <h2 className="font-bold">Lộ trình {map.origin.name} → {map.dest.name} · gói {TIER_LABEL[tier]}</h2>
              <button type="button" onClick={() => setBig(false)} className="ml-auto grid size-9 cursor-pointer place-items-center rounded-full hover:bg-white/15" aria-label="Đóng"><X className="size-5" /></button>
            </header>
            <div className="overflow-y-auto p-4 sm:p-5">
              <Suspense fallback={<Skeleton h="h-[55vh]" />}><TripMap map={map} tier={tier} /></Suspense>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
