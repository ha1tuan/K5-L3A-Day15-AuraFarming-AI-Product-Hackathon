import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Bus, Plane, Car, Ship } from 'lucide-react';
import type { RouteLeg, Tier, TripView } from '../api/types';
import { TIER_LABEL } from '../lib/format';

const COLOR = { road: '#0e7490', flight: '#f97316', self: '#94a3b8' } as const;
const legColor = (l: RouteLeg) => (l.mode === 'flight' ? COLOR.flight : l.vehicle.startsWith('Tự') ? COLOR.self : COLOR.road);
const gio = (h: number | null) => (h == null ? '' : ` · ~${String(h).replace('.', ',')} giờ`);

const pin = (color: string, label: string, small = false) => L.divIcon({
  className: '',
  html: `<div style="display:flex;flex-direction:column;align-items:center;transform:translateY(-100%)">
    <span style="background:${color};color:#fff;font:600 ${small ? 11 : 12}px 'Be Vietnam Pro',sans-serif;padding:${small ? '2px 6px' : '3px 8px'};border-radius:999px;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.25)">${label}</span>
    <span style="width:${small ? 9 : 12}px;height:${small ? 9 : 12}px;border-radius:999px;background:${color};border:3px solid #fff;margin-top:3px;box-shadow:0 2px 6px rgba(0,0,0,.3)"></span></div>`,
  iconSize: [0, 0],
});

const num = (n: number, color: string) => L.divIcon({
  className: '',
  html: `<span style="display:grid;place-items:center;width:22px;height:22px;border-radius:999px;background:#fff;color:${color};border:2px solid ${color};font:700 11px 'Be Vietnam Pro',sans-serif;transform:translate(-50%,-50%);box-shadow:0 2px 6px rgba(0,0,0,.25)">${n}</span>`,
  iconSize: [0, 0],
});

/** Bản đồ lộ trình theo gói: từng chặng (đường bộ theo bản đồ thật, chặng bay vẽ cung) + danh sách chặng có phương tiện, km, giờ. */
export function TripMap({ map, tier }: { map: NonNullable<TripView['map']>; tier: Tier }) {
  const ref = useRef<HTMLDivElement>(null);
  const legs = map.routes?.[tier] ?? [];
  useEffect(() => {
    if (!ref.current) return;
    const m = L.map(ref.current, { scrollWheelZoom: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · đường: OSRM',
    }).addTo(m);
    const pts: L.LatLngExpression[] = [];
    legs.forEach((l, i) => {
      const c = legColor(l);
      const line = L.polyline(l.path, { color: c, weight: l.mode === 'flight' ? 3 : 5, opacity: .9, dashArray: l.mode === 'flight' ? '8 10' : undefined }).addTo(m);
      line.bindTooltip(`${i + 1}. ${l.from} → ${l.to}<br>${l.vehicle}${l.km ? ` · ${l.km} km` : ''}${gio(l.hours)}`, { sticky: true });
      const mid = l.path[Math.floor(l.path.length / 2)];
      L.marker(mid, { icon: num(i + 1, c), interactive: false }).addTo(m);
      if (i > 0 && i < legs.length) L.marker(l.path[0], { icon: pin(c === COLOR.self ? COLOR.flight : c, l.from, true) }).addTo(m);
      pts.push(...l.path);
    });
    const A: L.LatLngExpression = [map.origin.lat, map.origin.lon], B: L.LatLngExpression = [map.dest.lat, map.dest.lon];
    L.marker(B, { icon: pin('#ea580c', map.dest.name) }).addTo(m);
    if (legs.length) L.marker(A, { icon: pin('#06263a', map.origin.name) }).addTo(m);
    if (pts.length) m.fitBounds(L.latLngBounds(pts), { padding: [50, 50] });
    else m.setView(B, 11);
    return () => { m.remove(); };
  }, [map, tier, legs]);

  return (
    <div className="grid gap-4">
      <figure className="overflow-hidden rounded-3xl bg-card shadow-sm ring-1 ring-black/5">
        <div ref={ref} className="h-80 w-full sm:h-[26rem]" role="img" aria-label={`Bản đồ lộ trình ${map.origin.name} → ${map.dest.name}`} />
      </figure>
      <div className="rounded-3xl bg-card p-4 ring-1 ring-black/5">
        <p className="mb-3 text-sm font-bold">Các chặng đi — gói {TIER_LABEL[tier]}</p>
        {legs.length === 0 ? <p className="text-sm text-muted">Đi lại trong thành phố — không có chặng đi xa.</p> : (
          <ol className="grid gap-2">
            {legs.map((l, i) => {
              const Icon = l.mode === 'flight' ? Plane : l.vehicle.startsWith('Tự') ? Car : Bus;
              return (
                <li key={i} className="flex gap-3 rounded-2xl bg-soft/70 p-3">
                  <span className="grid size-9 shrink-0 place-items-center rounded-xl text-white" style={{ background: legColor(l) }}><Icon className="size-4" aria-hidden /></span>
                  <div className="min-w-0 text-sm">
                    <p className="font-semibold">{i + 1}. {l.from} → {l.to}</p>
                    <p className="text-muted">{l.vehicle}{l.km ? ` · ${l.km} km` : ''}{gio(l.hours)}</p>
                    {l.ferry && <p className="mt-0.5 flex items-center gap-1 text-xs text-accent"><Ship className="size-3.5" aria-hidden />Có đoạn đi phà</p>}
                    {l.approx && <p className="mt-0.5 text-xs text-est">Chưa tải được đường thật — đang vẽ đường thẳng minh hoạ.</p>}
                  </div>
                </li>
              );
            })}
          </ol>
        )}
        <p className="mt-3 text-[11px] leading-relaxed text-muted">Đường bộ vẽ theo bản đồ thật (OSRM, dữ liệu OpenStreetMap); km chặng bộ theo bản đồ. Giờ đi dự trù theo tốc độ xe đoàn có nghỉ giữa chặng — chậm hơn xe con.</p>
      </div>
    </div>
  );
}
