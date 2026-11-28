import { useState } from 'react';
import { viDate } from '../lib/format';
const THU = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
const weekday = (iso: string) => { const d = new Date(iso + 'T00:00:00'); return isNaN(d.getTime()) ? '' : THU[d.getDay()]; };
import { Bus, BedDouble, Utensils, Users, Sparkles, Camera, Moon, ExternalLink } from 'lucide-react';
import type { Day, Menu, Slot, SlotKind } from '../api/types';
import { formatVnd } from '../lib/format';
import { Flag } from './ui';
import s from './DayTimeline.module.scss';

const ICON: Record<SlotKind, typeof Bus> = { travel: Bus, hotel: BedDouble, meal: Utensils, activity: Users, gala: Sparkles, sight: Camera, rest: Moon };
const DETAIL_LABEL: Partial<Record<SlotKind, string>> = {
  meal: 'Xem thực đơn & giá / suất', gala: 'Xem chương trình gala & thực đơn', activity: 'Xem chương trình & giá',
  sight: 'Xem giá vé & giờ mở cửa',
};

function MenuBlock({ m }: { m: Menu }) {
  return (
    <div>
      <p className="mb-1 font-medium">
        {m.name}{m.price_per_pax > 0 && <> · <span className={m.estimated ? 'est-value' : ''}>{formatVnd(m.price_per_pax)}</span>/suất</>}
        {m.table_size && <> · bàn {m.table_size} người</>}
      </p>
      <ul className="grid list-disc gap-0.5 pl-5">{m.dishes.map(d => <li key={d}>{d}</li>)}</ul>
      {m.drinks_note && <p className="mt-1 text-muted">{m.drinks_note}</p>}
      <p className={`mt-2 text-xs ${m.estimated ? 'text-est' : 'text-muted'}`}>
        {m.source_url
          ? <>Thực đơn theo <a href={m.source_url} target="_blank" rel="noreferrer" className="text-accent underline">trang nhà hàng</a></>
          : <>Thực đơn mẫu theo mức gói — <b>ước tính</b>, cần chốt với nhà hàng</>}
      </p>
    </div>
  );
}

function SlotDetail({ slot }: { slot: Slot }) {
  const hasDetail = slot.menu || slot.program || slot.details || slot.sources?.length;
  if (!hasDetail) return null;
  return (
    <details className="mt-2 text-sm" data-print-open>
      <summary className="inline-flex cursor-pointer items-center gap-1 font-medium text-accent">{DETAIL_LABEL[slot.kind] ?? 'Xem chi tiết'}</summary>
      <div className={`${s.detail} grid gap-3`}>
        {slot.details && <p>{slot.details}</p>}
        {slot.program && (
          <div>
            {slot.program.title && <p className="mb-1 font-medium">{slot.program.title}</p>}
            {slot.kind === 'gala' && !slot.program.title && <p className="mb-1 font-medium">Chương trình</p>}
            <ol className={s.program}>
              {slot.program.steps.map(st => <li key={st.start}><time>{st.start}–{st.end}</time><span>{st.text}</span></li>)}
            </ol>
            {slot.program.includes && <p className="mt-2 text-xs text-muted">Gồm: {slot.program.includes}</p>}
            {slot.program.fallback && <p className="mt-1 text-xs text-muted">{slot.program.fallback}</p>}
          </div>
        )}
        {slot.menu && <MenuBlock m={slot.menu} />}
        {!!slot.places?.length && (
          <div>
            <p className="mb-1 font-medium">Quán thật gần trung tâm để hỏi set menu đoàn</p>
            <ul className="flex flex-wrap gap-1.5">
              {slot.places.map(p => (
                <li key={p.url}><a href={p.url} target="_blank" rel="noreferrer"
                  className="inline-flex items-center gap-1 rounded-full bg-soft px-2.5 py-1 text-xs hover:bg-accent-soft hover:text-accent">
                  {p.name}{p.km != null && <span className="text-muted">· {String(p.km).replace('.', ',')} km</span>}<ExternalLink className="size-3" aria-hidden /></a></li>
              ))}
            </ul>
            <p className="mt-1 text-xs text-muted">Từ bản đồ mở OpenStreetMap — chưa kiểm thực đơn, giá, có nhận đoàn không.</p>
          </div>
        )}
        {!!slot.sources?.length && (
          <div>
            <p className="mb-1 font-medium">Nguồn & tra cứu</p>
            <ul className="grid gap-1">
              {slot.sources.map(x => (
                <li key={x.url}><a href={x.url} target="_blank" rel="noreferrer" className="inline-flex items-start gap-1 text-accent hover:underline">
                  <ExternalLink className="mt-0.5 size-3.5 shrink-0" aria-hidden /><span>{x.label}</span></a></li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </details>
  );
}

export function DayTimeline({ days }: { days: Day[] }) {
  const [active, setActive] = useState(0);
  return (
    <div>
      <div role="tablist" aria-label="Chọn ngày" className="no-print mb-4 flex flex-wrap gap-2">
        {days.map((d, i) => (
          <button key={d.label} role="tab" type="button" aria-selected={i === active} aria-controls={`day-${i}`}
            className={`h-10 cursor-pointer rounded-lg border px-3 text-sm transition ${i === active ? 'border-primary bg-primary text-white' : 'border-line bg-card hover:bg-soft'}`}
            onClick={() => setActive(i)}>
            {d.label} · {weekday(d.date)} {viDate(d.date)}
          </button>
        ))}
      </div>
      {days.map((d, i) => (
        <div key={d.label} id={`day-${i}`} role="tabpanel" className={`rounded-xl border border-line bg-card ${i === active ? '' : 'hidden print-open'}`}>
          <h3 className="hidden px-5 pt-4 font-semibold print:block">{d.label} · {weekday(d.date)} {viDate(d.date)}</h3>
          <ol className={s.list}>
            {d.slots.map((slot, k) => {
              const Icon = ICON[slot.kind];
              return (
                <li key={k} className={s.item}>
                  <span className={s.dot} data-kind={slot.kind}><Icon className="size-3" aria-hidden /></span>
                  <div className="flex gap-3">
                    <time className="w-12 shrink-0 font-semibold">{slot.start}</time>
                    <div className="min-w-0">
                      <p className="font-medium">
                        {slot.title}{' '}
                        {slot.source_url && (
                          <a href={slot.source_url} target="_blank" rel="noreferrer" className="inline-flex text-accent align-middle" aria-label={`Nguồn: ${slot.title}`}>
                            <ExternalLink className="size-3.5" aria-hidden />
                          </a>
                        )}
                      </p>
                      {slot.note && <p className="text-sm text-muted">{slot.note}</p>}
                      {slot.flags && <div className="mt-1 flex flex-wrap gap-1">{slot.flags.map(f => <Flag key={f} kind={f} />)}</div>}
                      <SlotDetail slot={slot} />
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </div>
      ))}
    </div>
  );
}
