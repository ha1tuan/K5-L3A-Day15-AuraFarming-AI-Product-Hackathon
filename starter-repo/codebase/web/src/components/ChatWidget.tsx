import { useEffect, useRef, useState } from 'react';
import { Send, X, RotateCcw, Sparkles } from 'lucide-react';
import { chat, type ChatMsg } from '../api/client';
import { Robot } from './Robot';
import { Markdown } from './Markdown';

const HELLO: ChatMsg = {
  role: 'assistant',
  content: 'Chào bạn! Mình là **Aura** 🤖 — trợ lý của **AuraFarming**.\n\nNhắn cho mình **số người, số ngày, nơi xuất phát, mục đích** và **ngân sách / địa điểm** để có 3 gói chi phí + lịch từng giờ. Hoặc **dán báo giá tour** để mình tính tổng chi thật.',
};
const GOI_Y = [
  '50 người từ Đà Nẵng, 2 ngày 1 đêm, gắn kết, ngân sách 200 triệu',
  '40 người từ Hà Nội đi Hạ Long 3 ngày 2 đêm, nghỉ dưỡng',
  'Dữ liệu giá lấy từ đâu?',
  'Bạn có đặt phòng giúp không?',
];
const KEY = 'aura-chat-v1';

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [hint, setHint] = useState(true);
  const [msgs, setMsgs] = useState<ChatMsg[]>(() => {
    try { const s = sessionStorage.getItem(KEY); return s ? JSON.parse(s) : [HELLO]; } catch { return [HELLO]; }
  });
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { try { sessionStorage.setItem(KEY, JSON.stringify(msgs.slice(-30))); } catch { /* bỏ qua */ } }, [msgs]);
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs, busy, open]);
  useEffect(() => { if (open) { setHint(false); setTimeout(() => input.current?.focus(), 200); } }, [open]);
  useEffect(() => { const t = setTimeout(() => setHint(false), 12000); return () => clearTimeout(t); }, []);

  async function send(t: string) {
    const content = t.trim();
    if (!content || busy) return;
    const next = [...msgs, { role: 'user' as const, content }];
    setMsgs(next); setText(''); setBusy(true);
    try {
      const r = await chat(next.filter(m => m !== HELLO));
      setMsgs(m => [...m, { role: 'assistant', content: r.reply }]);
    } catch (e) {
      setMsgs(m => [...m, { role: 'assistant', content: `Xin lỗi, mình chưa kết nối được máy chủ (${(e as Error).message}). Bạn thử lại nhé.` }]);
    } finally { setBusy(false); }
  }

  return (
    <div className="no-print">
      {/* Robot nổi góc phải */}
      {!open && (
        <div className="fixed bottom-4 right-4 z-40 flex items-end gap-2 sm:bottom-6 sm:right-6">
          {hint && (
            <button type="button" onClick={() => setOpen(true)}
              className="fade-up mb-16 max-w-[13rem] cursor-pointer rounded-2xl rounded-br-sm bg-card px-4 py-2.5 text-left text-sm shadow-xl ring-1 ring-black/5">
              <b>Xin chào! Mình là Aura</b><br /><span className="text-muted">Hỏi mình về chuyến đi của công ty nhé ✨</span>
            </button>
          )}
          <button type="button" onClick={() => setOpen(true)} aria-label="Mở trợ lý Aura"
            className="group relative grid size-24 cursor-pointer place-items-center rounded-full sm:size-28">
            <span className="absolute inset-3 rounded-full bg-gradient-to-br from-sun/40 to-accent/40 blur-xl transition group-hover:from-sun/70" aria-hidden />
            <Robot className="relative size-24 transition group-hover:scale-110 sm:size-28" waving />
          </button>
        </div>
      )}

      {/* Khung chat */}
      {open && (
        <section aria-label="Trò chuyện với Aura"
          className="fade-up fixed inset-x-2 bottom-2 z-50 flex h-[min(42rem,calc(100dvh-1rem))] flex-col overflow-hidden rounded-3xl bg-bg shadow-2xl ring-1 ring-black/10 sm:inset-x-auto sm:bottom-6 sm:right-6 sm:w-[26rem]">
          <header className="app-hero relative flex items-center gap-3 px-4 py-3 text-white">
            <div className="-my-4 -ml-1"><Robot className="size-16" talking={busy} /></div>
            <div className="leading-tight">
              <p className="font-extrabold">Aura <span className="font-normal text-white/70">· trợ lý AuraFarming</span></p>
              <p className="flex items-center gap-1.5 text-xs text-white/80"><span className="size-2 rounded-full bg-emerald-400" />{busy ? 'Đang tính…' : 'Sẵn sàng · tiền được tính từng dòng, không đoán'}</p>
            </div>
            <button type="button" onClick={() => setMsgs([HELLO])} className="ml-auto grid size-8 cursor-pointer place-items-center rounded-full hover:bg-white/15" aria-label="Cuộc trò chuyện mới" title="Cuộc trò chuyện mới"><RotateCcw className="size-4" /></button>
            <button type="button" onClick={() => setOpen(false)} className="grid size-8 cursor-pointer place-items-center rounded-full hover:bg-white/15" aria-label="Đóng"><X className="size-5" /></button>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4" aria-live="polite">
            {msgs.map((m, i) => m.role === 'user' ? (
              <div key={i} className="ml-10 whitespace-pre-wrap rounded-2xl rounded-br-sm bg-ocean px-3.5 py-2.5 text-sm text-white shadow">{m.content}</div>
            ) : (
              <div key={i} className="mr-4 flex gap-2">
                <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-sun-soft"><Sparkles className="size-3.5 text-sun" aria-hidden /></span>
                <div className="min-w-0 flex-1 rounded-2xl rounded-tl-sm bg-card px-3.5 py-2.5 shadow-sm ring-1 ring-black/5"><Markdown text={m.content} /></div>
              </div>
            ))}
            {busy && (
              <div className="mr-4 flex gap-2">
                <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-sun-soft"><Sparkles className="size-3.5 text-sun" aria-hidden /></span>
                <div className="flex gap-1 rounded-2xl bg-card px-4 py-3 shadow-sm ring-1 ring-black/5" aria-label="Aura đang trả lời">
                  {[0, 1, 2].map(d => <span key={d} className="typing-dot size-2 rounded-full bg-accent" style={{ animationDelay: `${d * 0.15}s` }} />)}
                </div>
              </div>
            )}
            {msgs.length <= 1 && !busy && (
              <div className="flex flex-wrap gap-2 pl-9">
                {GOI_Y.map(g => (
                  <button key={g} type="button" onClick={() => send(g)}
                    className="cursor-pointer rounded-full bg-card px-3 py-1.5 text-left text-xs text-accent-dark ring-1 ring-accent/25 transition hover:bg-accent-soft">{g}</button>
                ))}
              </div>
            )}
            <div ref={end} />
          </div>

          <form className="flex items-end gap-2 border-t border-line bg-card p-3" onSubmit={e => { e.preventDefault(); send(text); }}>
            <textarea ref={input} value={text} onChange={e => setText(e.target.value)} rows={1} placeholder="Nhắn cho Aura… (Enter để gửi, Shift+Enter xuống dòng)"
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(text); } }}
              className="max-h-36 min-h-11 flex-1 resize-y rounded-2xl border border-line bg-bg px-3 py-2.5 text-sm focus:border-accent focus:ring-4 focus:ring-accent/10" aria-label="Tin nhắn" />
            <button type="submit" disabled={busy || !text.trim()} aria-label="Gửi"
              className="grid size-11 shrink-0 cursor-pointer place-items-center rounded-full bg-sun text-white shadow-lg shadow-sun/30 transition hover:bg-sun-dark disabled:cursor-not-allowed disabled:opacity-50">
              <Send className="size-4" />
            </button>
          </form>
        </section>
      )}
    </div>
  );
}
