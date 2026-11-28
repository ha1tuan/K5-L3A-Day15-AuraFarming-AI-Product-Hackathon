import { useState } from 'react';
import { Printer, CircleCheck, TriangleAlert, SkipForward } from 'lucide-react';
import { InlineMd } from './InlineMd';
import { TripExtras } from './TripExtras';
import { RouteMapCard } from './RouteMapCard';
import type { Plan, TripEcho, TripView } from '../api/types';
import { formatVndShort, PURPOSE_LABEL, TIER_LABEL } from '../lib/format';
import { btnGhost } from './ui';
import { OverBudget } from './OverBudget';
import { DayTimeline } from './DayTimeline';

function dateRange(e: TripEcho) {
  const f = (iso: string) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;
  return e.days === 1 ? `${f(e.start_date)}/${e.start_date.slice(0, 4)}` : `${f(e.start_date)}–${f(e.end_date)}/${e.end_date.slice(0, 4)}`;
}

function OnePlan({ plan, request, map }: { plan: Plan; request: TripEcho; map?: TripView['map'] }) {
  const over = plan.over_budget !== null && plan.over_budget > 0;
  return (
    <>
      <div className="mb-5 flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-2xl font-bold">{plan.destination} · gói {TIER_LABEL[plan.tier]}</h1>
          <p className="text-muted">{request.headcount} người · {dateRange(request)} · từ {request.origin} · {PURPOSE_LABEL[request.purpose]}</p>
        </div>
        <button type="button" className={`${btnGhost} no-print ml-auto`} onClick={() => window.print()}>
          <Printer className="size-4" aria-hidden />In / lưu PDF
        </button>
      </div>

      <div className="mb-6 grid gap-4 rounded-xl border border-line bg-card p-5 sm:grid-cols-3">
        <div>
          <p className="text-sm text-muted">Tổng cả đoàn</p>
          <p className="text-2xl font-bold">{formatVndShort(plan.total)}</p>
          {plan.over_budget !== null && request.budget !== null && (
            <p className={`flex items-center gap-1 text-sm ${over ? 'text-over' : 'text-ok'}`}>
              {over ? <TriangleAlert className="size-4" aria-hidden /> : <CircleCheck className="size-4" aria-hidden />}
              {over ? `vượt ${formatVndShort(plan.over_budget!)}` : `trong ngân sách ${formatVndShort(request.budget)}`}
            </p>
          )}
        </div>
        <div>
          <p className="text-sm text-muted">Mỗi người</p>
          <p className="text-2xl font-bold">{formatVndShort(plan.per_person)}</p>
        </div>
        {plan.estimate_total !== plan.total && (
          <div className="text-sm">
            <p className="text-muted">Dự trù → theo kế hoạch</p>
            <p className="mt-1">{formatVndShort(plan.estimate_total)} → <b>{formatVndShort(plan.total)}</b></p>
            {plan.estimate_note && <p className="text-xs text-muted">{plan.estimate_note}</p>}
          </div>
        )}
      </div>

      {over && plan.explanation && request.budget !== null && (
        <div className="mb-6"><OverBudget tier={plan.tier} ex={plan.explanation} budget={request.budget} /></div>
      )}

      {plan.notes && plan.notes.length > 0 && (
        <ul className="mb-6 grid gap-1 rounded-xl border border-est bg-est-bg p-4 text-sm">
          {plan.notes.map((n, i) => <li key={i} className="flex gap-2"><TriangleAlert className="mt-0.5 size-4 shrink-0 text-est" aria-hidden /><InlineMd text={n} /></li>)}
        </ul>
      )}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <div>
          <DayTimeline days={plan.days} />
          {map && <RouteMapCard map={map} tier={plan.tier} />}
        </div>
        <TripExtras plan={plan} />
      </div>
    </>
  );
}

export function PlanView({ plans, request, activeTier, map }: { plans: Plan[]; request: TripEcho; activeTier?: Plan['tier']; map?: TripView['map'] }) {
  const [active, setActive] = useState(() => {
    const within = plans.map((p, i) => [p, i] as const).filter(([p]) => p.over_budget === null || p.over_budget <= 0);
    return within.length ? within[within.length - 1][1] : 0;
  });
  if (plans.length === 1) return <OnePlan plan={plans[0]} request={request} map={map} />;
  const chosen = activeTier ? plans.find(p => p.tier === activeTier) : undefined;   // gói do thanh tóm tắt chọn (PlanWorkspace)
  if (chosen) return <OnePlan key={chosen.tier} plan={chosen} request={request} map={map} />;
  return (
    <>
      <p className="no-print mb-3 flex items-center gap-2 text-sm text-muted">
        <SkipForward className="size-4" aria-hidden />Bỏ qua bước duyệt vì đã có cả kinh phí và địa điểm — đây là 3 phương án để bạn so.
      </p>
      <div role="tablist" aria-label="Chọn gói" className="no-print mb-6 flex gap-2 border-b border-line">
        {plans.map((p, i) => {
          const over = p.over_budget !== null && p.over_budget > 0;
          return (
            <button key={p.tier} role="tab" type="button" aria-selected={i === active}
              className={`-mb-px inline-flex cursor-pointer items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium ${i === active ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-primary'}`}
              onClick={() => setActive(i)}>
              {TIER_LABEL[p.tier]}
              {over ? <TriangleAlert className="size-4 text-over" aria-label="vượt ngân sách" /> : <CircleCheck className="size-4 text-ok" aria-label="trong ngân sách" />}
            </button>
          );
        })}
      </div>
      <OnePlan key={plans[active].tier} plan={plans[active]} request={request} map={map} />
    </>
  );
}
