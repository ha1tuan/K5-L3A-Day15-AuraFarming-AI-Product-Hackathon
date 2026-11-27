import type { TripEcho } from '../api/types';
import { formatVnd, PURPOSE_LABEL } from '../lib/format';

export function nightsText(e: TripEcho) {
  return e.days === 1 ? 'đi về trong ngày' : `${e.days} ngày ${e.nights} đêm`;
}

export function TripEchoLine({ e }: { e: TripEcho }) {
  return (
    <p className="text-muted">
      Đã hiểu: <b className="text-primary">{e.headcount} người</b> · {nightsText(e)} · từ {e.origin} · {PURPOSE_LABEL[e.purpose]}
      {e.budget !== null && <> · ngân sách <b className="text-primary">{formatVnd(e.budget)}</b> tổng đoàn</>}
    </p>
  );
}
