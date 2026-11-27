import { describe, expect, it } from 'vitest';
import { renderToString } from 'react-dom/server';
import { Landing } from './Landing';
import { FEATURED } from '../lib/featured';

describe('Landing', () => {
  it('render được hero, số liệu và thẻ điểm đến có ảnh video', () => {
    const html = renderToString(<Landing onStart={() => {}} onQuote={() => {}} />);
    expect(html).toContain('đúng tiền, đủ hoá đơn');
    expect(html).toContain('83%');
    expect(html).toContain('Hạ Long');
    expect(html).toContain('i.ytimg.com/vi/');
  });
  it('mọi điểm đến có giá tham khảo > 0 và video có mã 11 ký tự', () => {
    expect(FEATURED).toHaveLength(24);
    for (const f of FEATURED) {
      expect(f.price_from).toBeGreaterThan(0);
      for (const v of f.videos) expect(v.id).toMatch(/^[\w-]{11}$/);
    }
  });
});
