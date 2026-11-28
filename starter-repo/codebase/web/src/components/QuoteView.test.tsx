import { describe, expect, it } from 'vitest';
import { renderToString } from 'react-dom/server';
import { QuoteResultView, messageToTour } from './QuoteAudit';
import type { QuoteResult } from '../api/types';

const res: QuoteResult = {
  status: 'ok', so_nguoi: 45, dia_diem: null, gia_moi_khach: 950000, gia_bao: 42750000, tong: 49275000, moi_nguoi: 1095000,
  ngan_sach: 45000000, vuot: 4275000, chenh_pct: 15.3,
  dong: [{ ten: 'Giá tour theo báo giá', so_luong: 45, don_vi: 'khách', don_gia: 950000, thanh_tien: 42750000 }],
  vi_sao_vuot: ['- **Vượt ngân sách 4.275.000đ**'], tham_chieu: '',
  chung_tu: ['**Hoá đơn VAT:** báo giá ghi VAT 10% *không bao gồm* → phải trả thêm. ([nguồn](https://a.vn))', '**Chuyển khoản:** tổng ≥ 5.000.000đ', '*Không phải tư vấn thuế*'],
  ca_nhan: [], cau_hoi: ['Khoản "Vé hồ bơi" chưa có số tiền — hỏi giá cụ thể cho 45 người.'], to_trinh: 'Đề xuất duyệt **49.275.000đ**',
};

describe('kết quả soát báo giá', () => {
  it('có thẻ kết luận, nút chép tin nhắn, chứng từ dạng ✓/⚠', () => {
    const html = renderToString(<QuoteResultView res={res} />);
    expect(html).toContain('Đừng duyệt theo giá báo');
    expect(html).toContain('Chép tin nhắn gửi công ty tour');
    expect(html).toContain('Cần làm');
    expect(html).toContain('Lưu ý');
  });
  it('tin nhắn gửi công ty tour: lịch sự, bỏ định dạng, kèm yêu cầu hoá đơn', () => {
    const m = messageToTour(res);
    expect(m).toContain('đoàn 45 khách');
    expect(m).toContain('1. Khoản "Vé hồ bơi"');
    expect(m).toContain('xuất hoá đơn VAT ghi tên công ty');
    expect(m).not.toContain('**');
  });
});
