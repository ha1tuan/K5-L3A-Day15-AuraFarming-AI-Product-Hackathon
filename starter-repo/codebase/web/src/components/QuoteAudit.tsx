import { useRef, useState } from 'react';
import { ClipboardPaste, FileSearch, Printer, ReceiptText, ShieldCheck, MessageCircleQuestion, FileText, TriangleAlert, CircleCheck } from 'lucide-react';
import type { QuoteResult } from '../api/types';
import { auditQuote } from '../api/client';
import { formatVnd, formatVndShort } from '../lib/format';
import { SAMPLE_QUOTE, SAMPLE_QUOTE_URL } from '../lib/sampleQuote';
import { InlineMd } from './InlineMd';
import { Notice, btnGhost, btnPrimary } from './ui';

function Section({ icon: Icon, title, children }: { icon: typeof FileText; title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-card p-5">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold"><Icon className="size-5 text-accent" aria-hidden />{title}</h2>
      {children}
    </section>
  );
}

export function QuoteAudit() {
  const [text, setText] = useState('');
  const [res, setRes] = useState<QuoteResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const abort = useRef<AbortController | null>(null);

  async function run() {
    abort.current?.abort();
    const ctl = new AbortController();
    abort.current = ctl;
    setBusy(true); setErr(null); setRes(null);
    try {
      setRes(await auditQuote(text, ctl.signal));
    } catch (e) {
      if ((e as Error).name !== 'AbortError') setErr((e as Error).message || 'Không kết nối được máy chủ.');
    } finally { setBusy(false); }
  }

  const over = !!res?.vuot;
  return (
    <div className="grid gap-6">
      <section aria-labelledby="qa-h">
        <h1 id="qa-h" className="text-2xl font-bold">Soát báo giá tour đoàn</h1>
        <p className="mt-1 max-w-3xl text-muted">
          Dán báo giá công ty tour gửi (giá / khách, mục <i>bao gồm</i> và <i>không bao gồm</i>) kèm <b>số người</b> và <b>ngân sách</b>.
          Hệ thống cộng các khoản ngoài giá (VAT, vé, tip, vé máy bay…) ra <b>tổng chi thật</b>, soát hoá đơn / chuyển khoản để kế toán duyệt được.
        </p>
        <textarea value={text} onChange={e => setText(e.target.value)} rows={12} aria-label="Nội dung báo giá"
          placeholder={'Công ty 45 người, ngân sách 45 triệu.\nGiá: 950.000 đ/khách\nGiá tour bao gồm:\n- Xe đưa đón…\nGiá tour không bao gồm:\n- Thuế VAT 10%…'}
          className="mt-4 w-full rounded-lg border border-line bg-card p-3 font-mono text-sm focus:border-accent" />
        <div className="mt-3 flex flex-wrap gap-3">
          <button type="button" className={btnPrimary} disabled={busy || text.trim().length < 20} onClick={run}>
            <FileSearch className="size-4" aria-hidden />{busy ? 'Đang soát…' : 'Soát báo giá'}
          </button>
          <button type="button" className={btnGhost} onClick={() => { setText(SAMPLE_QUOTE); setRes(null); }}>
            <ClipboardPaste className="size-4" aria-hidden />Dán báo giá mẫu (thật)
          </button>
          <a href={SAMPLE_QUOTE_URL} target="_blank" rel="noreferrer" className="self-center text-sm text-accent hover:underline">nguồn báo giá mẫu</a>
        </div>
      </section>

      {err && <Notice tone="error" title="Có lỗi">{err}</Notice>}
      {res?.status === 'ask_back' && <Notice tone="ask" title="Cần thêm thông tin">{res.message}</Notice>}

      {res?.status === 'ok' && res.dong && (
        <>
          <div className="grid gap-4 rounded-xl border border-line bg-card p-5 sm:grid-cols-4">
            <div><p className="text-sm text-muted">Giá báo ({res.so_nguoi} khách)</p><p className="text-2xl font-bold">{formatVndShort(res.gia_bao!)}</p></div>
            <div>
              <p className="text-sm text-muted">Tổng chi thật</p>
              <p className="text-2xl font-bold text-over">{formatVndShort(res.tong!)}</p>
              <p className="text-sm text-over">+{res.chenh_pct}% so với giá báo</p>
            </div>
            <div><p className="text-sm text-muted">Mỗi người</p><p className="text-2xl font-bold">{formatVndShort(res.moi_nguoi!)}</p></div>
            {res.ngan_sach ? (
              <div>
                <p className="text-sm text-muted">Ngân sách {formatVndShort(res.ngan_sach)}</p>
                <p className={`mt-1 flex items-center gap-1 font-semibold ${over ? 'text-over' : 'text-ok'}`}>
                  {over ? <TriangleAlert className="size-4" aria-hidden /> : <CircleCheck className="size-4" aria-hidden />}
                  {over ? `Vượt ${formatVndShort(res.vuot!)}` : 'Trong ngân sách'}
                </p>
              </div>
            ) : <div className="text-sm text-muted">Chưa có ngân sách để so.</div>}
          </div>

          <Section icon={ReceiptText} title="Tổng chi thật ước tính">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-line text-left text-muted">
                  <th className="py-2 pr-3">Hạng mục</th><th className="py-2 pr-3 text-right">Số lượng</th>
                  <th className="py-2 pr-3 text-right">Đơn giá</th><th className="py-2 text-right">Thành tiền</th></tr></thead>
                <tbody>
                  {res.dong.map((d, i) => (
                    <tr key={i} className="border-b border-line/60">
                      <td className="py-2 pr-3">{d.ten}{/ước tính|tạm tính/.test(d.ten) && <span className="ml-2 rounded bg-est-bg px-1.5 py-0.5 text-xs text-est">ước tính</span>}</td>
                      <td className="py-2 pr-3 text-right">{d.so_luong.toLocaleString('vi-VN')} {d.don_vi}</td>
                      <td className="py-2 pr-3 text-right">{formatVnd(d.don_gia)}</td>
                      <td className="py-2 text-right font-medium">{formatVnd(d.thanh_tien)}</td>
                    </tr>
                  ))}
                  <tr><td className="py-2 font-bold" colSpan={3}>Tổng cả đoàn</td><td className="py-2 text-right font-bold">{formatVnd(res.tong!)}</td></tr>
                </tbody>
              </table>
            </div>
            {res.vi_sao_vuot && res.vi_sao_vuot.length > 0 && (
              <ul className="mt-4 grid gap-1 rounded-lg bg-over-bg p-4 text-sm">
                {res.vi_sao_vuot.map((x, i) => <li key={i}><InlineMd text={x} /></li>)}
              </ul>
            )}
            {res.tham_chieu && <p className="mt-3 text-sm text-muted"><InlineMd text={res.tham_chieu} /></p>}
            {res.ca_nhan && res.ca_nhan.length > 0 && (
              <p className="mt-3 text-sm text-muted">Khoản cá nhân, công ty không phải chịu (không cộng vào tổng): {res.ca_nhan.join('; ')}</p>
            )}
          </Section>

          <Section icon={ShieldCheck} title="Soát chứng từ / hoá đơn (để kế toán duyệt được)">
            <ul className="grid gap-2 text-sm">{res.chung_tu!.map((x, i) => <li key={i} className="leading-relaxed"><InlineMd text={x} /></li>)}</ul>
          </Section>

          <Section icon={MessageCircleQuestion} title="Câu cần hỏi lại công ty tour trước khi duyệt">
            <ol className="ml-5 grid list-decimal gap-1 text-sm">{res.cau_hoi!.map((x, i) => <li key={i}><InlineMd text={x} /></li>)}</ol>
          </Section>

          <Section icon={FileText} title="Tờ trình (nháp)">
            <p className="text-sm leading-relaxed"><InlineMd text={res.to_trinh!} /></p>
            <div className="no-print mt-4 flex gap-3">
              <button type="button" className={btnGhost} onClick={() => navigator.clipboard?.writeText(res.to_trinh!.replace(/\*\*/g, ''))}>Chép tờ trình</button>
              <button type="button" className={btnGhost} onClick={() => window.print()}><Printer className="size-4" aria-hidden />In / lưu PDF</button>
            </div>
          </Section>
          <p className="text-xs text-muted">Hệ thống chỉ soát và dự trù, không đặt tour, không thanh toán; không phải tư vấn thuế — kế toán đối chiếu văn bản hiện hành.</p>
        </>
      )}
    </div>
  );
}
