import { ExternalLink } from 'lucide-react';
import type { Package } from '../api/types';
import { formatVnd } from '../lib/format';
import { Flag } from './ui';

export function CostTable({ pkg, headcount, budget }: { pkg: Package; headcount: number; budget: number | null }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[680px] text-sm">
        <caption className="sr-only">Chi phí từng khoản</caption>
        <thead>
          <tr className="border-b border-line text-left text-muted [&_th]:py-2 [&_th]:pr-3 [&_th]:font-medium">
            <th scope="col">Hạng mục</th><th scope="col">Mô tả</th><th scope="col" className="text-right">Số lượng</th>
            <th scope="col" className="text-right">Đơn giá</th><th scope="col" className="text-right">Thành tiền</th><th scope="col">Nguồn</th>
          </tr>
        </thead>
        <tbody className="[&_td]:py-2 [&_td]:pr-3 [&_tr]:border-b [&_tr]:border-line">
          {pkg.line_items.map((r, i) => (
            <tr key={i}>
              <td>{r.category}</td>
              <td>{r.description}</td>
              <td className="text-right">{r.qty ? `${r.qty} ${r.unit}` : <span className="text-muted">{r.unit}</span>}</td>
              <td className="text-right">
                {r.qty ? <span className={r.estimated ? 'est-value' : ''}>{formatVnd(r.unit_price)}</span> : '—'}
                {r.estimated && r.qty > 0 && <> <Flag kind="estimate" /></>}
              </td>
              <td className="text-right font-medium">{formatVnd(r.amount)}</td>
              <td>
                {r.source_url
                  ? <a href={r.source_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-accent hover:underline">bài viết<ExternalLink className="size-3" aria-hidden /></a>
                  : <span className="text-muted">—</span>}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot className="[&_td]:py-2 [&_td]:pr-3">
          <tr className="text-base font-bold"><td colSpan={4}>Tổng cả đoàn ({headcount} người)</td><td className="text-right">{formatVnd(pkg.total)}</td><td /></tr>
          <tr><td colSpan={4} className="text-muted">Mỗi người</td><td className="text-right">{formatVnd(pkg.per_person)}</td><td /></tr>
          {budget !== null && pkg.over_budget !== null && (
            <tr>
              <td colSpan={4} className="text-muted">Ngân sách · chênh lệch</td>
              <td className={`text-right ${pkg.over_budget > 0 ? 'text-over' : 'text-ok'}`}>
                {formatVnd(budget)} · {pkg.over_budget > 0 ? `vượt ${formatVnd(pkg.over_budget)}` : `còn ${formatVnd(-pkg.over_budget)}`}
              </td><td />
            </tr>
          )}
        </tfoot>
      </table>
      <p className="mt-2 text-xs text-muted">
        Giá tham khảo. Hệ thống không đặt chỗ — <b>cần xác nhận số phòng còn trống</b> và sức chứa nhà hàng trực tiếp.
      </p>
    </div>
  );
}
