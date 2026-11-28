import { useRef, useState } from 'react';
import {
  ClipboardPaste, FileSearch, Printer, ReceiptText, ShieldCheck, MessageCircleQuestion, FileText, TriangleAlert,
  CircleCheck, Copy, Check, ChevronDown, ScanSearch, Loader2,
} from 'lucide-react';
import type { QuoteResult } from '../api/types';
import { auditQuote } from '../api/client';
import { formatVnd, formatVndShort } from '../lib/format';
import { SAMPLE_QUOTE, SAMPLE_QUOTE_URL } from '../lib/sampleQuote';
import { InlineMd } from './InlineMd';
import { Notice, btnGhost, btnPrimary } from './ui';

function Section({ icon: Icon, title, children, action }: { icon: typeof FileText; title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <section className="rounded-3xl bg-card p-5 shadow-sm ring-1 ring-black/5 sm:p-6">
      <div className="mb-3 flex flex-wrap items-center gap-3">
        <h3 className="flex items-center gap-2 text-lg font-bold"><Icon className="size-5 text-accent" aria-hidden />{title}</h3>
        {action && <div className="ml-auto">{action}</div>}
      </div>
      {children}
    </section>
  );
}

function CopyBtn({ text, label }: { text: string; label: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button type="button" className={btnGhost} onClick={() => { navigator.clipboard?.writeText(text); setOk(true); setTimeout(() => setOk(false), 2500); }}>
      {ok ? <Check className="size-4 text-ok" aria-hidden /> : <Copy className="size-4" aria-hidden />}{ok ? 'Đã chép' : label}
    </button>
  );
}

const plain = (s: string) => s.replace(/\*\*|\*|`/g, '').replace(/\s*\(\[nguồn\]\([^)]*\)\)/g, '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1');

/** Tin nhắn gửi công ty tour: các câu cần hỏi lại + yêu cầu hoá đơn — dán thẳng vào Zalo / email. */
export function messageToTour(res: QuoteResult) {
  const qs = (res.cau_hoi ?? []).map((q, i) => `${i + 1}. ${plain(q)}`);
  return [
    `Chào anh/chị, công ty em đang xem báo giá tour cho đoàn ${res.so_nguoi} khách${res.dia_diem ? ` đi ${res.dia_diem}` : ''}. Nhờ anh/chị làm rõ giúp em:`,
    ...qs,
    `${qs.length + 1}. Báo giá cuối cùng đã gồm VAT và xuất hoá đơn VAT ghi tên công ty chưa? Công ty sẽ thanh toán bằng chuyển khoản.`,
    'Em cảm ơn ạ.',
  ].join('\n');
}

function Verdict({ res }: { res: QuoteResult }) {
  const over = !!res.vuot;
  const noBudget = !res.ngan_sach;
  const tone = noBudget ? 'bg-accent-soft ring-accent/30 text-accent-dark' : over ? 'bg-over-bg ring-over/30 text-over' : 'bg-ok-bg ring-ok/30 text-ok';
  const Icon = over ? TriangleAlert : CircleCheck;
  const title = noBudget
    ? `Tổng chi thật ≈ ${formatVndShort(res.tong!)} — cao hơn giá báo ${res.chenh_pct}%`
    : over
      ? `Đừng duyệt theo giá báo — tổng chi thật vượt ngân sách ${formatVndShort(res.vuot!)}`
      : `Vừa ngân sách — tổng chi thật ${formatVndShort(res.tong!)}, còn dư ${formatVndShort(res.ngan_sach! - res.tong!)}`;
  const sub = `Giá báo ${formatVndShort(res.gia_bao!)} (${formatVnd(res.gia_moi_khach!)}/khách × ${res.so_nguoi}) + các khoản "không bao gồm" = ${formatVndShort(res.tong!)} (+${res.chenh_pct}%).`;
  return (
    <div className={`fade-up flex gap-4 rounded-3xl p-5 ring-1 sm:p-6 ${tone}`} role="status">
      <span className="grid size-12 shrink-0 place-items-center rounded-2xl bg-white/70"><Icon className="size-6" aria-hidden /></span>
      <div>
        <p className="text-xl font-extrabold leading-snug sm:text-2xl">{title}</p>
        <p className="mt-1 text-sm text-primary/80">{sub}</p>
      </div>
    </div>
  );
}

/** Mỗi mục chứng từ: ✓ ổn / ⚠ cần làm — bấm mở chi tiết + nguồn. */
function Checklist({ items }: { items: string[] }) {
  return (
    <ul className="grid gap-2">
      {items.map((x, i) => {
        const m = /^\*\*([^*]+?)\*\*:?\s*([\s\S]*)$/.exec(x);
        if (!m) return <li key={i} className="px-1 text-xs text-muted"><InlineMd text={x} /></li>;
        const head = m[1].replace(/:$/, '');
        const body = m[2];
        const warn = /không nói|không bao gồm|vượt trần|khó có hoá đơn|phải trả thêm|cho mình lương/i.test(head + ' ' + body);
        return (
          <li key={i}>
            <details className="group rounded-2xl bg-soft/70 ring-1 ring-line open:bg-card">
              <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-3">
                {warn ? <TriangleAlert className="size-5 shrink-0 text-est" aria-label="cần xử lý" /> : <CircleCheck className="size-5 shrink-0 text-ok" aria-label="ổn" />}
                <span className="font-semibold">{head}</span>
                <span className={`ml-auto shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold ${warn ? 'bg-est-bg text-est' : 'bg-ok-bg text-ok'}`}>{warn ? 'Cần làm' : 'Lưu ý'}</span>
                <ChevronDown className="size-4 shrink-0 text-muted transition group-open:rotate-180" aria-hidden />
              </summary>
              <div className="px-4 pb-4 pl-12 text-sm leading-relaxed text-muted"><InlineMd text={body} /></div>
            </details>
          </li>
        );
      })}
    </ul>
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

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)] lg:items-start">
      {/* Trái: báo giá (đứng yên khi cuộn kết quả) */}
      <section aria-labelledby="qa-h" className="lg:sticky lg:top-24">
        <h2 id="qa-h" className="text-xl font-bold">Dán báo giá của công ty tour</h2>
        <p className="mt-1 text-sm text-muted">
          Gồm <b>giá / khách</b>, mục <i>bao gồm</i>, <i>không bao gồm</i>, kèm <b>số người</b> và <b>ngân sách</b>.
        </p>
        <textarea value={text} onChange={e => setText(e.target.value)} rows={16} aria-label="Nội dung báo giá"
          placeholder={'Công ty 45 người, ngân sách 45 triệu.\nGiá: 950.000 đ/khách\nGiá tour bao gồm:\n- Xe đưa đón…\nGiá tour không bao gồm:\n- Thuế VAT 10%…'}
          className="mt-3 w-full rounded-2xl border border-line bg-bg p-3 font-mono text-sm leading-relaxed focus:border-accent focus:ring-4 focus:ring-accent/10" />
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className={btnPrimary} disabled={busy || text.trim().length < 20} onClick={run}>
            {busy ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <FileSearch className="size-4" aria-hidden />}{busy ? 'Đang soát…' : 'Soát báo giá'}
          </button>
          <button type="button" className={btnGhost} onClick={() => { setText(SAMPLE_QUOTE); setRes(null); }}>
            <ClipboardPaste className="size-4" aria-hidden />Dán báo giá mẫu
          </button>
        </div>
        <a href={SAMPLE_QUOTE_URL} target="_blank" rel="noreferrer" className="mt-2 inline-block text-xs text-accent hover:underline">Nguồn báo giá mẫu (công khai)</a>
      </section>

      {/* Phải: kết quả */}
      <div className="grid gap-5">
        {err && <Notice tone="error" title="Có lỗi">{err}</Notice>}
        {res?.status === 'ask_back' && <Notice tone="ask" title="Cần thêm thông tin">{res.message}</Notice>}
        {busy && (
          <div className="grid gap-4" aria-hidden>
            <div className="h-28 animate-pulse rounded-3xl bg-soft" />
            <div className="h-64 animate-pulse rounded-3xl bg-soft" />
            <div className="h-40 animate-pulse rounded-3xl bg-soft" />
          </div>
        )}
        {res?.status === 'ok' && res.dong && <QuoteResultView res={res} />}
        {!busy && !res && !err && (
          <div className="grid place-items-center rounded-3xl border-2 border-dashed border-line px-6 py-16 text-center">
            <ScanSearch className="size-12 text-accent/60" aria-hidden />
            <p className="mt-3 text-lg font-bold">Kết quả soát sẽ hiện ở đây</p>
            <p className="mt-1 max-w-md text-sm text-muted">Tổng chi thật (VAT, vé, tip, vé máy bay ngoài giá), so ngân sách, việc cần làm với hoá đơn và tin nhắn hỏi lại công ty tour. Chưa có báo giá? Bấm "Dán báo giá mẫu".</p>
          </div>
        )}
      </div>
    </div>
  );
}

/** Kết quả soát báo giá (tab Soát báo giá và khung đối chiếu trong trang kế hoạch). */
export function QuoteResultView({ res }: { res: QuoteResult }) {
  const over = !!res.vuot;
  return (
    <div className="grid gap-5">
      <Verdict res={res} />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          ['Giá báo', formatVndShort(res.gia_bao!), `${res.so_nguoi} khách`],
          ['Tổng chi thật', formatVndShort(res.tong!), `+${res.chenh_pct}% so với giá báo`],
          ['Mỗi người', formatVndShort(res.moi_nguoi!), 'đã gồm khoản ngoài giá'],
          ['Ngân sách', res.ngan_sach ? formatVndShort(res.ngan_sach) : '—', res.ngan_sach ? (over ? `vượt ${formatVndShort(res.vuot!)}` : 'trong ngân sách') : 'chưa nhập'],
        ].map(([l, v, s], k) => (
          <div key={l} className="rounded-2xl bg-card p-4 shadow-sm ring-1 ring-black/5">
            <p className="text-xs text-muted">{l}</p>
            <p className={`text-2xl font-extrabold ${k === 1 ? 'text-sun-dark' : k === 3 && over ? 'text-over' : ''}`}>{v}</p>
            <p className={`text-xs ${k === 3 && over ? 'text-over' : 'text-muted'}`}>{s}</p>
          </div>
        ))}
      </div>

      <Section icon={MessageCircleQuestion} title="Hỏi lại công ty tour trước khi duyệt"
        action={<CopyBtn text={messageToTour(res)} label="Chép tin nhắn gửi công ty tour" />}>
        <ol className="ml-5 grid list-decimal gap-1.5 text-sm">{(res.cau_hoi ?? []).map((x, i) => <li key={i}><InlineMd text={x} /></li>)}</ol>
        <p className="mt-3 text-xs text-muted">Bấm nút để chép sẵn thành tin nhắn lịch sự (kèm yêu cầu hoá đơn VAT) — dán vào Zalo / email gửi công ty tour.</p>
      </Section>

      <Section icon={ReceiptText} title="Tổng chi thật ước tính">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-line text-left text-muted">
              <th className="py-2 pr-3">Hạng mục</th><th className="py-2 pr-3 text-right">Số lượng</th>
              <th className="py-2 pr-3 text-right">Đơn giá</th><th className="py-2 text-right">Thành tiền</th></tr></thead>
            <tbody>
              {(res.dong ?? []).map((d, i) => (
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
          <ul className="mt-4 grid gap-1 rounded-2xl bg-over-bg p-4 text-sm">
            {res.vi_sao_vuot.map((x, i) => <li key={i} className={x.startsWith('  ') ? 'ml-4' : ''}><InlineMd text={x.replace(/^\s*-\s*/, '')} /></li>)}
          </ul>
        )}
        {res.tham_chieu && <p className="mt-3 text-sm text-muted"><InlineMd text={res.tham_chieu} /></p>}
        {res.ca_nhan && res.ca_nhan.length > 0 && (
          <p className="mt-3 text-sm text-muted">Khoản cá nhân, công ty không phải chịu (không cộng vào tổng): {res.ca_nhan.join('; ')}</p>
        )}
      </Section>

      <Section icon={ShieldCheck} title="Hoá đơn & chứng từ — để kế toán duyệt được">
        <Checklist items={res.chung_tu ?? []} />
      </Section>

      <Section icon={FileText} title="Tờ trình (nháp)"
        action={<div className="no-print flex flex-wrap gap-2"><CopyBtn text={plain(res.to_trinh ?? '')} label="Chép tờ trình" />
          <button type="button" className={btnGhost} onClick={() => window.print()}><Printer className="size-4" aria-hidden />In / PDF</button></div>}>
        <p className="text-sm leading-relaxed"><InlineMd text={res.to_trinh ?? ''} /></p>
      </Section>
      <p className="text-xs text-muted">Hệ thống chỉ soát và dự trù, không đặt tour, không thanh toán; không phải tư vấn thuế — kế toán đối chiếu văn bản hiện hành.</p>
    </div>
  );
}
