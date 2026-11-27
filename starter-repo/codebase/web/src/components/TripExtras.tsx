import { useEffect, useState } from 'react';
import { Bus, BedDouble, Sun, MapPin, Info, Play, X, ExternalLink, CloudRain } from 'lucide-react';
import type { Plan } from '../api/types';

const ytId = (url: string) => /[?&]v=([\w-]{11})/.exec(url)?.[1] ?? '';

function Row({ icon: Icon, label, children }: { icon: typeof Bus; label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent"><Icon className="size-4.5" aria-hidden /></span>
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
        <div className="mt-0.5 text-sm">{children}</div>
      </div>
    </div>
  );
}

/** Cột "Thông tin chuyến đi" + "Video" ở trang kế hoạch — chữ thường cho người dùng, video có ảnh, xem ngay trong trang. */
export function TripExtras({ plan }: { plan: Plan }) {
  const [play, setPlay] = useState<{ id: string; title: string } | null>(null);
  useEffect(() => {
    if (!play) return;
    const k = (e: KeyboardEvent) => e.key === 'Escape' && setPlay(null);
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [play]);
  const x = plan.extra;
  const vids = (plan.videos ?? []).map(v => ({ ...v, id: ytId(v.url) })).filter(v => v.id);
  if (!x && !vids.length) return null;

  return (
    <aside className="grid content-start gap-5">
      {x && (
        <div className="rounded-3xl bg-card p-5 shadow-sm ring-1 ring-black/5">
          <p className="mb-4 text-base font-bold">Thông tin chuyến đi · {plan.destination}</p>
          <div className="grid gap-4">
            <Row icon={Bus} label="Cách đi">{x.travel}</Row>
            <Row icon={BedDouble} label="Nơi ở">{x.lodging}</Row>
            <Row icon={x.season.in_season ? Sun : CloudRain} label="Thời điểm đẹp">
              Tháng {x.season.months}
              {!x.season.in_season && (
                <p className="mt-1 rounded-lg bg-est-bg px-2.5 py-1.5 text-xs text-est">
                  Ngày đi rơi vào tháng {x.season.month_now} — ngoài mùa đẹp, nên xem dự báo thời tiết hoặc cân nhắc dời ngày.
                </p>
              )}
            </Row>
            {x.sights.length > 0 && (
              <Row icon={MapPin} label="Điểm tham quan trong lịch">
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {x.sights.map(s => <span key={s} className="rounded-full bg-soft px-2.5 py-1 text-xs">{s}</span>)}
                </div>
              </Row>
            )}
          </div>
          <div className="mt-5 flex gap-2.5 rounded-2xl bg-sun-soft p-3.5 text-xs leading-relaxed text-primary">
            <Info className="mt-0.5 size-4 shrink-0 text-sun" aria-hidden />
            <p><b>Về giá:</b> {x.price_note}</p>
          </div>
        </div>
      )}

      {vids.length > 0 && (
        <div className="rounded-3xl bg-card p-5 shadow-sm ring-1 ring-black/5">
          <p className="text-base font-bold">Xem trước {plan.destination}</p>
          <p className="mb-4 text-xs text-muted">Video thật trên YouTube — review của khách du lịch và chương trình team building đã tổ chức.</p>
          <div className="grid gap-3">
            {vids.map(v => (
              <button key={v.id} type="button" onClick={() => setPlay({ id: v.id, title: v.title })}
                className="group flex cursor-pointer gap-3 rounded-2xl p-1.5 text-left transition hover:bg-soft">
                <span className="relative aspect-video w-32 shrink-0 overflow-hidden rounded-xl bg-ocean">
                  <img src={`https://i.ytimg.com/vi/${v.id}/mqdefault.jpg`} alt="" loading="lazy" className="size-full object-cover transition duration-500 group-hover:scale-110" />
                  <span className="absolute inset-0 grid place-items-center bg-black/20">
                    <span className="grid size-8 place-items-center rounded-full bg-white/90 text-ocean shadow transition group-hover:scale-110 group-hover:bg-sun group-hover:text-white">
                      <Play className="ml-0.5 size-3.5 fill-current" aria-hidden />
                    </span>
                  </span>
                </span>
                <span className="min-w-0">
                  {v.kind && <span className="mb-1 inline-block rounded-full bg-accent-soft px-2 py-0.5 text-[10px] font-semibold text-accent">{v.kind}</span>}
                  <span className="line-clamp-2 block text-sm font-medium leading-snug">{v.title}</span>
                  <span className="mt-0.5 block truncate text-xs text-muted">{v.channel}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {play && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-ocean/85 p-4 backdrop-blur-md" role="dialog" aria-modal="true" aria-label={play.title} onClick={() => setPlay(null)}>
          <div className="fade-up w-full max-w-4xl overflow-hidden rounded-3xl bg-black shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="relative aspect-video">
              <iframe className="absolute inset-0 size-full" title={play.title} src={`https://www.youtube-nocookie.com/embed/${play.id}?autoplay=1&rel=0`}
                allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen />
            </div>
            <div className="flex items-center gap-3 px-4 py-3 text-sm text-white/80">
              <span className="truncate">{play.title}</span>
              <a href={`https://www.youtube.com/watch?v=${play.id}`} target="_blank" rel="noreferrer" className="ml-auto inline-flex shrink-0 items-center gap-1 text-white hover:underline">YouTube <ExternalLink className="size-3.5" aria-hidden /></a>
              <button type="button" onClick={() => setPlay(null)} className="grid size-8 cursor-pointer place-items-center rounded-full hover:bg-white/15" aria-label="Đóng"><X className="size-5" /></button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
