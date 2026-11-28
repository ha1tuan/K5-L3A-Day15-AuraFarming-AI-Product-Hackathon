import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { SlidersHorizontal, FileSearch, Users, FileSpreadsheet, Link2, Check, Map as MapIcon, RotateCcw, Loader2, X, MoreHorizontal, BarChart3, CircleCheck, TriangleAlert } from 'lucide-react';
import type { QuoteResult, Tier, TripView } from '../api/types';
import { exportUrl, quoteForTrip, recalcTrip } from '../api/client';
import { formatVnd, formatVndShort, TIER_LABEL } from '../lib/format';
import { SAMPLE_QUOTE } from '../lib/sampleQuote';
import { CostChart } from './CostChart';
import { CostSplit } from './CostSplit';
import { PlanView } from './PlanView';
import { QuoteResultView } from './QuoteAudit';
import { InlineMd } from './InlineMd';
import { btnGhost, btnPrimary, inputCls, Notice } from './ui';

type Panel = 'edit' | 'quote' | 'split' | 'map' | null;
const PANEL_TITLE: Record<Exclude<Panel, null>, string> = { edit: 'Tùy chỉnh chuyến đi', quote: 'Đối chiếu báo giá tour', split: 'Chia tiền công ty / người thân', map: 'Bản đồ lộ trình' };

/** Ngăn kéo trượt từ cạnh phải — lịch phía dưới giữ nguyên chỗ đang đọc. */
function Drawer({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', k); document.body.style.overflow = ''; };
  }, [onClose]);
  return (
    <div className="backdrop-in fixed inset-0 z-50 flex justify-end bg-ocean/40 backdrop-blur-sm" onClick={onClose} role="dialog" aria-modal="true" aria-label={title}>
      <aside className="drawer flex h-full w-full max-w-2xl flex-col bg-bg shadow-2xl" onClick={e => e.stopPropagation()}>
        <header className="app-hero flex items-center gap-3 px-5 py-4 text-white">
          <h2 className="text-lg font-bold">{title}</h2>
          <button type="button" onClick={onClose} className="ml-auto grid size-9 cursor-pointer place-items-center rounded-full hover:bg-white/15" aria-label="Đóng"><X className="size-5" /></button>
        </header>
        <div className="flex-1 overflow-y-auto p-5 sm:p-6">{children}</div>
      </aside>
    </div>
  );
}
const TripMap = lazy(() => import('./TripMap').then(m => ({ default: m.TripMap })));   // Leaflet chỉ tải khi mở bản đồ

/** Trang kế hoạch: biểu đồ 3 gói + thanh công cụ (tùy chỉnh, đối chiếu báo giá, chia tiền, bản đồ, Excel, link) + kế hoạch. */
export function PlanWorkspace({ view, onView }: { view: TripView; onView: (v: TripView) => void }) {
  const [panel, setPanel] = useState<Panel>(null);
  const [copied, setCopied] = useState(false);
  const [more, setMore] = useState(false);
  const [chart, setChart] = useState(true);
  const plans = view.plans ?? [];
  const req = view.request!;
  const [active, setActive] = useState<Tier>(() => {
    const within = plans.filter(p => p.over_budget === null || p.over_budget <= 0);
    return (within.length ? within[within.length - 1] : plans[0])?.tier ?? 'can_bang';
  });

  // --- tùy chỉnh
  const cz = view.customize;
  const [removed, setRemoved] = useState<string[]>(cz?.removed ?? []);
  const [hc, setHc] = useState(String(cz?.headcount ?? req.headcount));
  const [days, setDays] = useState(cz?.days ?? req.days);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const hcN = Number(hc);
  const dirty = cz && (hcN !== cz.headcount || days !== cz.days || [...removed].sort().join('|') !== [...cz.removed].sort().join('|'));
  async function apply(body?: { removed: string[] }) {
    setBusy(true); setErr(null);
    try {
      onView(await recalcTrip(view.trip_id, body ?? { headcount: hcN, days, removed }));
    } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  // --- đối chiếu báo giá
  const defTier: Tier = plans.length === 1 ? plans[0].tier : (view.packages?.find(p => p.recommended)?.tier ?? 'can_bang');
  const [qTier, setQTier] = useState<Tier>(plans.length > 1 ? active : defTier);
  const [qText, setQText] = useState('');
  const [qRes, setQRes] = useState<QuoteResult | null>(null);
  async function compare() {
    setBusy(true); setErr(null); setQRes(null);
    try { setQRes(await quoteForTrip(view.trip_id, qText, qTier)); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  const shareUrl = useMemo(() => {
    const u = new URL(window.location.href);
    u.search = '';
    u.searchParams.set('tab', 'lap-ke-hoach');
    u.searchParams.set('trip', view.trip_id);
    return u.toString();
  }, [view.trip_id]);
  const splitPlan = plans.find(p => p.tier === active) ?? plans[0];

  const tool = (id: Exclude<Panel, null>, label: string, Icon: typeof MapIcon) => (
    <button type="button" onClick={() => { setPanel(id); setMore(false); }}
      className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-card px-3.5 py-2 text-sm font-semibold ring-1 ring-line transition hover:ring-accent">
      <Icon className="size-4 text-accent" aria-hidden /><span className="hidden sm:inline">{label}</span>
    </button>
  );
  const pkgOf = (t: Tier) => view.packages?.find(p => p.tier === t);

  return (
    <div className="grid gap-6">
      {/* Thanh tóm tắt dính đầu trang: chọn gói + công cụ */}
      <div className="no-print sticky top-16 z-30 -mx-1 rounded-3xl bg-bg/90 p-2 shadow-lg ring-1 ring-black/5 backdrop-blur-md sm:p-3">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex flex-1 flex-wrap gap-2" role="tablist" aria-label="Chọn gói">
            {plans.map(p => {
              const over = p.over_budget !== null && p.over_budget > 0;
              const sel = plans.length > 1 ? p.tier === active : true;
              return (
                <button key={p.tier} type="button" role="tab" aria-selected={sel} onClick={() => setActive(p.tier)}
                  className={`min-w-[9.5rem] flex-1 cursor-pointer rounded-2xl px-3.5 py-2 text-left transition sm:flex-none ${sel ? 'bg-ocean text-white shadow-lg' : 'bg-card ring-1 ring-line hover:ring-accent'}`}>
                  <span className="flex items-center gap-1.5 text-xs font-semibold">
                    {TIER_LABEL[p.tier]}
                    {pkgOf(p.tier)?.recommended && <span className={`rounded-full px-1.5 text-[10px] ${sel ? 'bg-sun text-white' : 'bg-sun-soft text-sun-dark'}`}>Gợi ý</span>}
                    {req.budget !== null && (over ? <TriangleAlert className={`ml-auto size-3.5 ${sel ? 'text-orange-300' : 'text-over'}`} aria-label="vượt ngân sách" />
                      : <CircleCheck className={`ml-auto size-3.5 ${sel ? 'text-emerald-300' : 'text-ok'}`} aria-label="trong ngân sách" />)}
                  </span>
                  <span className="block text-lg font-extrabold leading-tight">{formatVndShort(p.total)}</span>
                  <span className={`block text-[11px] ${sel ? 'text-white/70' : 'text-muted'}`}>{formatVndShort(p.per_person)}/người{over ? ` · vượt ${formatVndShort(p.over_budget!)}` : ''}</span>
                </button>
              );
            })}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {cz && tool('edit', 'Tùy chỉnh', SlidersHorizontal)}
            {tool('quote', 'Đối chiếu báo giá', FileSearch)}
            {splitPlan && tool('split', 'Chia tiền', Users)}
            <div className="relative">
              <button type="button" onClick={() => setMore(m => !m)} aria-expanded={more} aria-label="Thêm"
                className="grid size-10 cursor-pointer place-items-center rounded-full bg-card ring-1 ring-line hover:ring-accent"><MoreHorizontal className="size-5" /></button>
              {more && (
                <div className="fade-up absolute right-0 top-12 z-40 grid w-60 gap-1 rounded-2xl bg-card p-2 shadow-2xl ring-1 ring-black/10">
                  {view.map && <button type="button" onClick={() => { setPanel('map'); setMore(false); }} className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-left text-sm hover:bg-soft"><MapIcon className="size-4 text-accent" />Bản đồ lộ trình</button>}
                  <a href={exportUrl(view.trip_id)} download onClick={() => setMore(false)} className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm hover:bg-soft"><FileSpreadsheet className="size-4 text-accent" />Tải tờ trình Excel</a>
                  <button type="button" onClick={() => { navigator.clipboard?.writeText(shareUrl); setCopied(true); setTimeout(() => setCopied(false), 2500); }}
                    className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-left text-sm hover:bg-soft">
                    {copied ? <Check className="size-4 text-ok" /> : <Link2 className="size-4 text-accent" />}{copied ? 'Đã chép link' : 'Chép link gửi sếp'}</button>
                  <button type="button" onClick={() => { setChart(c => !c); setMore(false); }} className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-left text-sm hover:bg-soft"><BarChart3 className="size-4 text-accent" />{chart ? 'Ẩn' : 'Hiện'} biểu đồ so sánh</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {chart && view.packages && view.packages.length > 1 && <CostChart packages={view.packages} budget={req.budget} />}

      {err && <Notice tone="error" title="Có lỗi">{err}</Notice>}

      {panel && (
        <Drawer title={PANEL_TITLE[panel]} onClose={() => setPanel(null)}>
      {panel === 'edit' && cz && (
        <section>
          <p className="mb-4 text-sm text-muted">Bỏ chọn khoản không muốn, sửa số người hoặc số ngày rồi bấm Tính lại — tiền, phòng, xe và lịch được tính lại ngay.</p>
          <div className="grid gap-5 lg:grid-cols-[14rem_1fr]">
            <div className="grid content-start gap-3">
              <label className="grid gap-1 text-sm font-medium">Số người
                <input type="number" min={5} max={500} className={inputCls} value={hc} onChange={e => setHc(e.target.value)} />
              </label>
              <label className="grid gap-1 text-sm font-medium">Số ngày
                <select className={inputCls} value={days} onChange={e => setDays(Number(e.target.value))}>
                  {[1, 2, 3, 4, 5].map(d => <option key={d} value={d}>{d === 1 ? '1 ngày (về trong ngày)' : `${d} ngày ${d - 1} đêm`}</option>)}
                </select>
              </label>
            </div>
            <fieldset>
              <legend className="mb-2 text-sm font-medium">Hoạt động & dịch vụ (bỏ chọn để bỏ khỏi mọi gói)</legend>
              <div className="flex flex-wrap gap-2">
                {cz.options.map(o => {
                  const on = !removed.includes(o);
                  return (
                    <label key={o} className={`inline-flex cursor-pointer items-center gap-2 rounded-full px-3.5 py-2 text-sm ring-1 transition ${on ? 'bg-accent-soft text-accent-dark ring-accent/30' : 'bg-soft text-muted line-through ring-line'}`}>
                      <input type="checkbox" className="size-4" checked={on} onChange={() => setRemoved(r => on ? [...r, o] : r.filter(x => x !== o))} />{o}
                    </label>
                  );
                })}
              </div>
            </fieldset>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="button" className={btnPrimary} disabled={busy || !dirty || !(hcN >= 5 && hcN <= 500)} onClick={() => apply()}>
              {busy ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <SlidersHorizontal className="size-4" aria-hidden />}Tính lại
            </button>
            {cz.removed.length > 0 && (
              <button type="button" className={btnGhost} disabled={busy} onClick={() => { setRemoved([]); apply({ removed: [] }); }}>
                <RotateCcw className="size-4" aria-hidden />Khôi phục đủ khoản
              </button>
            )}
          </div>
        </section>
      )}

      {panel === 'quote' && (
        <section>
          <p className="mb-4 text-sm text-muted">Dán báo giá công ty tour gửi. Hệ thống cộng các khoản "không bao gồm" ra tổng chi thật rồi đặt cạnh gói bạn chọn — biết ngay tour đắt hay rẻ hơn dự trù, thiếu khoản gì để thương lượng.</p>
          <div className="mb-3 flex flex-wrap items-center gap-2 text-sm">
            <span className="font-medium">So với gói:</span>
            {(view.packages ?? []).map(p => (
              <button key={p.tier} type="button" onClick={() => setQTier(p.tier)}
                className={`cursor-pointer rounded-full px-3.5 py-1.5 font-medium ring-1 ${qTier === p.tier ? 'bg-ocean text-white ring-ocean' : 'bg-card ring-line'}`}>
                {TIER_LABEL[p.tier]} · {formatVndShort(p.total)}
              </button>
            ))}
          </div>
          <textarea value={qText} onChange={e => setQText(e.target.value)} rows={8} aria-label="Báo giá tour"
            placeholder={'Giá: 950.000 đ/khách\nGiá tour bao gồm:\n- …\nGiá tour không bao gồm:\n- Thuế VAT 10% …'}
            className="w-full rounded-2xl border border-line bg-bg p-3 font-mono text-sm focus:border-accent" />
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className={btnPrimary} disabled={busy || qText.trim().length < 20} onClick={compare}>
              {busy ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <FileSearch className="size-4" aria-hidden />}Đối chiếu
            </button>
            <button type="button" className={btnGhost} onClick={() => setQText(SAMPLE_QUOTE.split('\n').slice(1).join('\n'))}>Dán báo giá mẫu</button>
          </div>
          {qRes?.status === 'ask_back' && <div className="mt-4"><Notice tone="ask" title="Cần thêm thông tin">{qRes.message}</Notice></div>}
          {qRes?.status === 'ok' && (
            <div className="mt-6 grid gap-6">
              {qRes.doi_chieu && (
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-2xl bg-soft p-4"><p className="text-xs text-muted">Dự trù gói {TIER_LABEL[qRes.doi_chieu.tier]}</p><p className="text-2xl font-extrabold">{formatVnd(qRes.doi_chieu.ke_hoach)}</p></div>
                  <div className="rounded-2xl bg-sun-soft p-4"><p className="text-xs text-muted">Báo giá tour — tổng chi thật</p><p className="text-2xl font-extrabold text-sun-dark">{formatVnd(qRes.doi_chieu.bao_gia_that)}</p></div>
                  <div className={`rounded-2xl p-4 ${qRes.doi_chieu.chenh > 0 ? 'bg-over-bg' : 'bg-ok-bg'}`}><p className="text-xs text-muted">Chênh lệch</p>
                    <p className={`text-2xl font-extrabold ${qRes.doi_chieu.chenh > 0 ? 'text-over' : 'text-ok'}`}>{qRes.doi_chieu.chenh > 0 ? '+' : '−'}{formatVnd(Math.abs(qRes.doi_chieu.chenh))} ({qRes.doi_chieu.chenh_pct > 0 ? '+' : ''}{qRes.doi_chieu.chenh_pct}%)</p></div>
                  <p className="text-sm sm:col-span-3"><InlineMd text={qRes.doi_chieu.nhan_xet} /></p>
                </div>
              )}
              <QuoteResultView res={qRes} />
            </div>
          )}
        </section>
      )}

      {panel === 'split' && splitPlan && (
        <section>
          <p className="mb-4 text-sm text-muted">Theo gói {TIER_LABEL[splitPlan.tier]} ({formatVnd(splitPlan.per_person)}/người).</p>
          <CostSplit plan={splitPlan} request={req} />
        </section>
      )}

      {panel === 'map' && view.map && <Suspense fallback={<div className="h-80 animate-pulse rounded-3xl bg-soft" />}><TripMap map={view.map} tier={active} /></Suspense>}
        </Drawer>
      )}

      <PlanView plans={plans} request={req} activeTier={plans.length > 1 ? active : undefined} />
    </div>
  );
}
