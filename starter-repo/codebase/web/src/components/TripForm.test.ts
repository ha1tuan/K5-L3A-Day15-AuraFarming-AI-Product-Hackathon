import { describe, expect, it } from 'vitest';
import { entryHint, validate, type FormState } from './TripForm';

const base: FormState = { headcount: '60', days: 3, start_date: '', origin: 'Hà Nội', purpose: 'gan_ket', budget: '', budget_per_person: false, destination: '' };

describe('entryHint', () => {
  it('A: budget only', () => expect(entryHint({ ...base, budget: '150.000.000' }).text).toMatch(/gợi ý 2–3 địa điểm/));
  it('B: destination only', () => expect(entryHint({ ...base, destination: 'Hạ Long' }).text).toMatch(/dự trù kinh phí 3 gói/));
  it('C: both', () => expect(entryHint({ ...base, budget: '1', destination: 'Hạ Long' }).text).toMatch(/3 kế hoạch chi tiết/));
  it('neither', () => expect(entryHint(base).ok).toBe(false));
});

describe('validate', () => {
  it('flags missing fields', () => {
    expect(validate({ ...base, headcount: '', origin: '', purpose: null })).toEqual(['headcount', 'origin', 'purpose', 'budget_or_destination']);
  });
  it('rejects headcount out of 5–500', () => {
    expect(validate({ ...base, headcount: '800', budget: '1' })).toContain('headcount');
    expect(validate({ ...base, headcount: '4', budget: '1' })).toContain('headcount');
  });
  it('passes a full form', () => expect(validate({ ...base, budget: '150.000.000' })).toEqual([]));
});
