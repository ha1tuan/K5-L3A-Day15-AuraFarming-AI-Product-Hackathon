import { describe, expect, it } from 'vitest';
import { approveTrip, createTrip } from './demo';
import type { TripInput } from './types';

const input: TripInput = { headcount: 60, days: 3, start_date: '2026-12-11', origin: 'Hà Nội', purpose: 'gan_ket', budget: 150_000_000, budget_per_person: false, destination: '' };

// Dữ liệu demo phải tự nhất quán như dữ liệu thật: dòng = SL × đơn giá, tổng = cộng dòng.
describe('demo adapter', () => {
  it('A: destinations with consistent packages', async () => {
    const v = await createTrip(input);
    expect(v.status).toBe('choose_destination');
    for (const d of v.destinations!) for (const p of d.packages) {
      for (const li of p.line_items) expect(li.amount).toBe(li.qty * li.unit_price);
      expect(p.total).toBe(p.line_items.reduce((s, li) => s + li.amount, 0));
      expect(p.over_budget).toBe(p.total - 150_000_000);
      if (p.over_budget! > 0) expect(p.explanation?.drivers.length).toBeGreaterThan(0);
    }
  }, 10000);
  it('B then approve → one plan', async () => {
    const v = await createTrip({ ...input, budget: null, destination: 'Hạ Long' });
    expect(v.status).toBe('choose_package');
    const ok = await approveTrip(v.trip_id, { destination: 'Hạ Long', package: 'can_bang', remove_items: ['gala'] });
    expect(ok.plans).toHaveLength(1);
    expect(ok.plans![0].days.flatMap(d => d.slots).some(s => s.kind === 'gala')).toBe(false);
  }, 10000);
  it('C → three plans', async () => {
    const v = await createTrip({ ...input, destination: 'Hạ Long' });
    expect(v.status).toBe('ok');
    expect(v.plans!.map(p => p.tier)).toEqual(['tiet_kiem', 'can_bang', 'cao_cap']);
  }, 10000);
  it('per-person budget is multiplied', async () => {
    const v = await createTrip({ ...input, budget: 3_000_000, budget_per_person: true, destination: 'Hạ Long' });
    expect(v.request!.budget).toBe(180_000_000);
  }, 10000);
});
