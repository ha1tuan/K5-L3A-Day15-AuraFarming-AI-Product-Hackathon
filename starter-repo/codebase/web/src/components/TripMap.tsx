import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { TripView } from '../api/types';

const pin = (color: string, label: string) => L.divIcon({
  className: '',
  html: `<div style="display:flex;flex-direction:column;align-items:center;transform:translateY(-100%)">
    <span style="background:${color};color:#fff;font:600 12px 'Be Vietnam Pro',sans-serif;padding:3px 8px;border-radius:999px;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.25)">${label}</span>
    <span style="width:12px;height:12px;border-radius:999px;background:${color};border:3px solid #fff;margin-top:3px;box-shadow:0 2px 6px rgba(0,0,0,.3)"></span></div>`,
  iconSize: [0, 0],
});

/** Bản đồ lộ trình nơi xuất phát → điểm đến (OpenStreetMap). Nét liền: đường bộ · nét đứt: bay. */
export function TripMap({ map }: { map: NonNullable<TripView['map']> }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const m = L.map(ref.current, { scrollWheelZoom: false, attributionControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(m);
    const a: L.LatLngExpression = [map.origin.lat, map.origin.lon];
    const b: L.LatLngExpression = [map.dest.lat, map.dest.lon];
    const same = map.origin.lat === map.dest.lat && map.origin.lon === map.dest.lon;
    L.marker(b, { icon: pin('#f97316', map.dest.name) }).addTo(m);
    if (!same) {
      L.marker(a, { icon: pin('#0e7490', map.origin.name) }).addTo(m);
      L.polyline([a, b], { color: '#0e7490', weight: 4, opacity: .85, dashArray: map.mode === 'plane' ? '10 10' : undefined }).addTo(m);
      m.fitBounds(L.latLngBounds([a, b]), { padding: [60, 60] });
    } else {
      m.setView(b, 11);
    }
    return () => { m.remove(); };
  }, [map]);
  return (
    <figure className="overflow-hidden rounded-3xl bg-card shadow-sm ring-1 ring-black/5">
      <div ref={ref} className="h-72 w-full sm:h-80" role="img" aria-label={`Bản đồ: ${map.origin.name} → ${map.dest.name}`} />
      <figcaption className="flex items-center gap-3 px-4 py-2.5 text-xs text-muted">
        <span className="inline-flex items-center gap-1.5"><span className="inline-block h-0.5 w-5 bg-accent" />{map.mode === 'plane' ? 'Bay (nét đứt: đường chim bay)' : 'Đường bộ (đường thẳng minh hoạ)'}</span>
        <span className="ml-auto">Bản đồ © OpenStreetMap</span>
      </figcaption>
    </figure>
  );
}
