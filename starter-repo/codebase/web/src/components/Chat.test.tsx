import { describe, expect, it } from 'vitest';
import { renderToString } from 'react-dom/server';
import { ChatWidget } from './ChatWidget';
import { Markdown } from './Markdown';
import { Logo } from './Brand';
import { Robot } from './Robot';

describe('Aura + thương hiệu', () => {
  it('robot nổi và logo render được', () => {
    const html = renderToString(<><ChatWidget /><Logo /><Robot talking /></>);
    expect(html).toContain('Mở trợ lý Aura');
    expect(html).toContain('Farming');
    expect(html).toContain('robot-eyes');
  });
  it('markdown của agent: tiêu đề, bảng, danh sách, đậm, link', () => {
    const md = '## Kế hoạch\n\n| Hạng mục | Số lượng | Đơn giá | Thành tiền |\n|---|---|---|---|\n| Xe | 2 xe | 1.000đ | 2.000đ |\n\n- **Vượt** 5đ\n- [nguồn](https://a.vn)\n\n> lưu ý';
    const html = renderToString(<Markdown text={md} />);
    expect(html).toContain('<table');
    expect(html).toContain('2.000đ');
    expect(html).toContain('<b>Vượt</b>');
    expect(html).toContain('href="https://a.vn"');
    expect(html).not.toContain('|---');
  });
});
