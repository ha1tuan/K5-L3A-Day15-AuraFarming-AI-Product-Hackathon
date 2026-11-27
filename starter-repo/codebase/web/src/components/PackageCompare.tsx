import { useState } from 'react';
import { ArrowLeft, Check, Receipt } from 'lucide-react';
import type { ApproveInput, Package, Tier, TripEcho } from '../api/types';
import { formatVndShort, TIER_LABEL } from '../lib/format';
import { BudgetBadge, btnPrimary, inputCls } from './ui';
import { CostTable } from './CostTable';
import { OverBudget } from './OverBudget';
import { nightsText } from './TripEchoLine';
import s from './PackageCompare.module.scss';

const ROWS: { key: keyof Package['summary']; label: string }[] = [
  { key: 'transport', label: 'Di chuyển' },
  { key: 'lodging', label: 'Lưu trú' },
  { key: 'rooms', label: 'Xếp phòng' },
  { key: 'meals', label: 'Ăn uống' },
  { key: 'gala', label: 'Gala tối' },
  { key: 'activities', label: 'Hoạt động' },
];

export function PackageCompare({ request, destination, packages, onApprove, onBack }: {
  request: TripEcho;
  destination: string;
  packages: Package[];
  onApprove: (body: ApproveInput) => void;
  onBack?: () => void;
}) {
  const [tier, setTier] = useState<Tier>(packages.find(p => p.recommended)?.tier ?? 'can_bang');
  const [headcount, setHeadcount] = useState(String(request.headcount));
  const [removeGala, setRemoveGala] = useState(false);
  const [removeTb, setRemoveTb] = useState(false);
  const chosen = packages.find(p => p.tier === tier)!;
  const cell = (t: Tier, first = false, last = false) =>
    t === tier ? `${s.selected} ${first ? s.selectedTop : ''} ${last ? s.selectedBottom : ''}` : '';
  const hc = Number(headcount);
  const hcValid = Number.isInteger(hc) && hc >= 5 && hc <= 500;

  const approve = () => {
    const remove_items: ApproveInput['remove_items'] = [];
    if (removeGala) remove_items.push('gala');
    if (removeTb) remove_items.push('team_building');
    onApprove({ destination, package: tier, headcount: hc !== request.headcount ? hc : undefined, remove_items: remove_items.length ? remove_items : undefined });
  };

  return (
    <section aria-labelledby="pkg-h">
      <div className="mb-6 flex flex-wrap items-end gap-3">
        <div>
          <h1 id="pkg-h" className="text-2xl font-bold">{destination} · so sánh 3 gói</h1>
          <p className="mt-1 text-muted">
            {request.headcount} người · {nightsText(request)} · từ {request.origin}
            {request.budget !== null && <> · ngân sách {formatVndShort(request.budget)}</>}
          </p>
        </div>
        {onBack && (
          <button type="button" className="ml-auto inline-flex cursor-pointer items-center gap-1 text-sm text-accent hover:underline" onClick={onBack}>
            <ArrowLeft className="size-4" aria-hidden />Đổi địa điểm
          </button>
        )}
      </div>

      <div className="overflow-x-auto rounded-xl border border-line bg-card shadow-sm">
        <table className={s.table}>
          <caption className="sr-only">So sánh 3 gói</caption>
          <thead>
            <tr>
              <td />
              {packages.map(p => (
                <th key={p.tier} scope="col" className={cell(p.tier, true)}>
                  <span className="flex items-center gap-2 text-base font-semibold">
                    {TIER_LABEL[p.tier]}
                    {p.recommended && <span className="rounded-full bg-accent px-2 py-0.5 text-xs font-medium text-white">Gợi ý</span>}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(r => (
              <tr key={r.key}>
                <th scope="row">{r.label}</th>
                {packages.map(p => <td key={p.tier} className={cell(p.tier)}>{p.summary[r.key]}</td>)}
              </tr>
            ))}
            <tr className={s.total}>
              <th scope="row" className="!text-primary !font-semibold">Tổng đoàn</th>
              {packages.map(p => (
                <td key={p.tier} className={cell(p.tier)}>
                  <div className="font-bold">{formatVndShort(p.total)}</div>
                  <div className="mt-1"><BudgetBadge over={p.over_budget} /></div>
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Mỗi người</th>
              {packages.map(p => <td key={p.tier} className={cell(p.tier)}>{formatVndShort(p.per_person)}</td>)}
            </tr>
            <tr>
              <th scope="row">Chọn gói</th>
              {packages.map(p => (
                <td key={p.tier} className={cell(p.tier, false, true)}>
                  <label className="inline-flex cursor-pointer items-center gap-2">
                    <input type="radio" name="pkg" className="size-4" checked={tier === p.tier} onChange={() => setTier(p.tier)} />
                    {TIER_LABEL[p.tier]}
                  </label>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      <details className="mt-4 rounded-xl border border-line bg-card">
        <summary className="flex cursor-pointer items-center gap-2 p-4 font-medium">
          <Receipt className="size-4" aria-hidden />Chi tiết từng khoản — gói {TIER_LABEL[tier]}
        </summary>
        <div className="px-4 pb-4"><CostTable pkg={chosen} headcount={request.headcount} budget={request.budget} /></div>
      </details>

      {request.budget !== null && packages.filter(p => p.explanation).map(p => (
        <div key={p.tier} className="mt-4"><OverBudget tier={p.tier} ex={p.explanation!} budget={request.budget!} /></div>
      ))}

      <div className="mt-6 rounded-xl border border-line bg-card p-5">
        <h2 className="mb-3 font-semibold">Chỉnh trước khi duyệt</h2>
        <div className="flex flex-wrap items-end gap-6">
          <div>
            <label htmlFor="hc2" className="mb-1 block text-sm font-medium">Số người</label>
            <input id="hc2" type="number" min={5} max={500} className={`${inputCls} w-28`} value={headcount}
              onChange={e => setHeadcount(e.target.value)} aria-invalid={!hcValid} />
          </div>
          <fieldset>
            <legend className="mb-1 text-sm font-medium">Bỏ hạng mục</legend>
            <div className="flex h-11 items-center gap-4 text-sm">
              <label className="flex items-center gap-2"><input type="checkbox" className="size-4" checked={removeGala} onChange={e => setRemoveGala(e.target.checked)} />Gala tối</label>
              <label className="flex items-center gap-2"><input type="checkbox" className="size-4" checked={removeTb} onChange={e => setRemoveTb(e.target.checked)} />Team building</label>
            </div>
          </fieldset>
          <button type="button" className={`${btnPrimary} ml-auto`} disabled={!hcValid} onClick={approve}>
            <Check className="size-4" aria-hidden />Duyệt gói {TIER_LABEL[tier]} & lập kế hoạch
          </button>
        </div>
        <p className="mt-3 text-xs text-muted">Nếu sửa số người hoặc bỏ hạng mục, chi phí sẽ được tính lại khi bấm Duyệt.</p>
      </div>
    </section>
  );
}
