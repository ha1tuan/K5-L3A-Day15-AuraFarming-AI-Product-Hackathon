import { describe, expect, it } from 'vitest';
import { renderToString } from 'react-dom/server';
import { CostChart } from './CostChart';
import { CostSplit } from './CostSplit';
import type { Package, Plan, TripEcho } from '../api/types';

const li = (category: string, amount: number) => ({ category, description: category, qty: 1, unit: 'x', unit_price: amount, amount, estimated: true });
const pkg = (tier: Package['tier'], total: number, over: number | null): Package => ({
  tier, total, per_person: total / 40, over_budget: over, recommended: tier === 'can_bang',
  summary: { transport: '', lodging: '', rooms: '', meals: '', gala: '', activities: '' },
  line_items: [li('Di chuyển', total * 0.2), li('Lưu trú', total * 0.4), li('Ăn uống', total * 0.25), li('Hoạt động', total * 0.1), li('Phát sinh', total * 0.05)],
});

describe('công cụ trang kế hoạch', () => {
  it('biểu đồ 3 gói có vạch ngân sách và nhãn vượt', () => {
    const html = renderToString(<CostChart packages={[pkg('tiet_kiem', 100e6, null), pkg('can_bang', 150e6, null), pkg('cao_cap', 250e6, 100e6)]} budget={150e6} />);
    expect(html).toContain('Ngân sách');
    expect(html).toContain('Cao cấp');
    expect(html).toContain('150 tr');
  });
  it('chia tiền: công ty trả nhân viên, người thân tự đóng', () => {
    const plan = { tier: 'can_bang', destination: 'Hạ Long', total: 120e6, per_person: 3e6, estimate_total: 120e6, over_budget: null, days: [] } as Plan;
    const req = { headcount: 40, days: 3, nights: 2, start_date: '2026-12-04', end_date: '2026-12-06', origin: 'Hà Nội', purpose: 'gan_ket', budget: null, entry: 'C' } as TripEcho;
    const html = renderToString(<CostSplit plan={plan} request={req} />);
    expect(html).toContain('120.000.000');
  });
});
