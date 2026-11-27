import { useEffect, useRef, useState } from 'react';
import { CalendarRange, FileSearch, Home } from 'lucide-react';
import { Landing } from './components/Landing';
import { ChatWidget } from './components/ChatWidget';
import { Logo } from './components/Brand';
import { useScroll } from './components/motion';
import { QuoteAudit } from './components/QuoteAudit';
import type { ApproveInput, Field, TripView } from './api/types';
import { approveTrip, createTrip, DEMO, getTrip } from './api/client';
import { parseVnd } from './lib/format';
import { StepBar } from './components/StepBar';
import { TripForm, validate, type FormState } from './components/TripForm';
import { LoadingSteps } from './components/LoadingSteps';
import { DestinationCards } from './components/DestinationCards';
import { PackageCompare } from './components/PackageCompare';
import { PlanView } from './components/PlanView';
import { Notice, btnGhost } from './components/ui';

const EMPTY: FormState = { headcount: '', days: 3, start_date: '', origin: '', purpose: null, budget: '', budget_per_person: false, destination: '' };

type Screen =
  | { kind: 'form'; errors: Field[]; askBack: boolean }
  | { kind: 'loading'; steps: string[] }
  | { kind: 'view'; view: TripView; chosenDest?: string };

const CREATE_STEPS = ['Hiểu yêu cầu', 'Chọn địa điểm, chỗ ở, ăn uống, hoạt động từ dữ liệu', 'Tính chi phí 3 gói cho cả đoàn', 'Xếp lịch từng giờ & kiểm tra'];
const APPROVE_STEPS = ['Tính lại theo lựa chọn', 'Chọn khách sạn, nhà hàng, hoạt động', 'Xếp lịch từng giờ & kiểm tra'];

function setTripInUrl(id: string | null) {
  const u = new URL(window.location.href);
  if (id) u.searchParams.set('trip', id); else u.searchParams.delete('trip');
  window.history.replaceState(null, '', u);
}

type Tab = 'home' | 'plan' | 'quote';
const TAB_PARAM: Record<Tab, string | null> = { home: null, plan: 'lap-ke-hoach', quote: 'bao-gia' };

export default function App() {
  const sc = useScroll();
  const [tab, setTab] = useState<Tab>(() => {
    const q = new URLSearchParams(window.location.search);
    return q.get('tab') === 'bao-gia' ? 'quote' : (q.get('tab') === 'lap-ke-hoach' || q.get('trip')) ? 'plan' : 'home';
  });
  const switchTab = (t: Tab) => {
    const u = new URL(window.location.href);
    if (TAB_PARAM[t]) u.searchParams.set('tab', TAB_PARAM[t]!); else u.searchParams.delete('tab');
    window.history.replaceState(null, '', u);
    setTab(t);
    window.scrollTo(0, 0);
  };
  const [form, setForm] = useState<FormState>(EMPTY);
  const [screen, setScreen] = useState<Screen>({ kind: 'form', errors: [], askBack: false });
  const [error, setError] = useState<string | null>(null);
  const abort = useRef<AbortController | null>(null);

  // Tải lại trang không mất chuyến đi: ?trip=<id>
  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get('trip');
    if (!id) return;
    setScreen({ kind: 'loading', steps: ['Tải lại chuyến đi'] });
    getTrip(id).then(v => setScreen({ kind: 'view', view: v })).catch(e => { setError(String(e.message ?? e)); setScreen({ kind: 'form', errors: [], askBack: false }); });
  }, []);

  async function run(steps: string[], call: (signal: AbortSignal) => Promise<TripView>, back: Screen) {
    abort.current?.abort();
    const ctl = new AbortController();
    abort.current = ctl;
    setError(null);
    setScreen({ kind: 'loading', steps });
    try {
      const v = await call(ctl.signal);
      if (v.status === 'ask_back') {
        setTripInUrl(null);
        setScreen({ kind: 'form', errors: v.missing_fields ?? [], askBack: true });
      } else {
        setTripInUrl(v.trip_id);
        setScreen({ kind: 'view', view: v });
      }
      window.scrollTo(0, 0);
    } catch (e) {
      if ((e as Error).name === 'AbortError') { setScreen(back); return; }
      setError((e as Error).message || 'Không kết nối được máy chủ.');
      setScreen(back);
    }
  }

  function submit() {
    const errors = validate(form);
    if (errors.length) { setScreen({ kind: 'form', errors, askBack: false }); return; }
    run(CREATE_STEPS, signal => createTrip({
      headcount: Number(form.headcount),
      days: form.days,
      start_date: form.start_date || null,
      origin: form.origin.trim(),
      purpose: form.purpose,
      budget: parseVnd(form.budget),
      budget_per_person: form.budget_per_person,
      destination: form.destination.trim(),
    }, signal), { kind: 'form', errors: [], askBack: false });
  }

  function approve(view: TripView, body: ApproveInput) {
    run(APPROVE_STEPS, signal => approveTrip(view.trip_id, body, signal), screen);
  }

  function restart() {
    setTripInUrl(null);
    setScreen({ kind: 'form', errors: [], askBack: false });
  }

  let step: 1 | 2 | 3 = 1, skipped = false, body: React.ReactNode = null;
  if (screen.kind === 'form') {
    body = <TripForm value={form} onChange={setForm} onSubmit={submit} errors={screen.errors} askBack={screen.askBack} />;
  } else if (screen.kind === 'loading') {
    body = <LoadingSteps steps={screen.steps} onCancel={() => abort.current?.abort()} />;
  } else {
    const v = screen.view;
    const again = <button type="button" className={btnGhost} onClick={restart}>Sửa yêu cầu</button>;
    if (v.status === 'refused') body = <Notice tone="info" title="Ngoài phạm vi hỗ trợ" action={again}>{v.message}</Notice>;
    else if (v.status === 'error' || !v.request) body = <Notice tone="error" title="Không lập được kế hoạch" action={again}>{v.message}</Notice>;
    else if (v.status === 'choose_destination' && !screen.chosenDest) {
      step = 2;
      body = <DestinationCards request={v.request} destinations={v.destinations ?? []} onChoose={name => setScreen({ kind: 'view', view: v, chosenDest: name })} />;
    } else if (v.status === 'choose_destination' || v.status === 'choose_package') {
      step = 2;
      const dest = screen.chosenDest ?? v.destination ?? '';
      const pkgs = screen.chosenDest ? v.destinations?.find(d => d.name === dest)?.packages ?? [] : v.packages ?? [];
      body = <PackageCompare key={dest} request={v.request} destination={dest} packages={pkgs}
        onApprove={b => approve(v, b)} onBack={screen.chosenDest ? () => setScreen({ kind: 'view', view: v }) : undefined} />;
    } else {
      step = 3;
      skipped = v.request.entry === 'C';
      body = (
        <>
          <PlanView plans={v.plans ?? []} request={v.request} />
          <div className="no-print mt-8"><button type="button" className={btnGhost} onClick={restart}>Lập chuyến đi khác</button></div>
        </>
      );
    }
  }

  return (
    <>
      <a href="#main" className="skip-link">Bỏ qua tới nội dung</a>
      <div className="no-print fixed inset-x-0 top-0 z-50 h-0.5 origin-left bg-gradient-to-r from-orange-300 via-sun to-sun-dark" style={{ transform: `scaleX(${sc.p})` }} aria-hidden />
      <header className={`no-print z-40 text-white transition-all duration-500 ${tab === 'home'
        ? `fixed inset-x-0 top-0 ${sc.y > 60 ? 'bg-ocean/90 shadow-lg backdrop-blur-md' : 'bg-transparent'}`
        : 'sticky top-0 bg-ocean/95 shadow-lg backdrop-blur'}`}>
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3 sm:px-6">
          <button type="button" onClick={() => switchTab('home')} className="cursor-pointer" aria-label="AuraFarming — trang chủ"><Logo /></button>
          {DEMO && <span className="rounded bg-est-bg px-2 py-0.5 text-xs font-medium text-est">Chế độ demo — dữ liệu mẫu</span>}
          <nav className="ml-auto flex gap-1 rounded-full p-1 glass" aria-label="Chức năng">
            {([['home', 'Trang chủ', Home], ['plan', 'Lập kế hoạch', CalendarRange], ['quote', 'Soát báo giá', FileSearch]] as const).map(([t, label, Icon]) => (
              <button key={t} type="button" onClick={() => switchTab(t)} aria-current={tab === t ? 'page' : undefined}
                className={`inline-flex cursor-pointer items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium transition sm:px-4 ${tab === t ? 'bg-white text-ocean shadow' : 'text-white/85 hover:bg-white/10'}`}>
                <Icon className="size-4" aria-hidden /><span className={t === 'home' ? 'hidden sm:inline' : ''}>{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </header>
      {tab === 'home' ? (
        <main id="main"><Landing onStart={dest => { restart(); setForm(f => ({ ...f, destination: dest ?? f.destination })); switchTab('plan'); }} onQuote={() => switchTab('quote')} /></main>
      ) : (<>
      <section className="app-hero no-print text-white">
        <div className="mx-auto max-w-6xl px-4 pb-14 pt-8">
          <p className="text-sm font-semibold uppercase tracking-wider text-orange-300">{tab === 'quote' ? 'Trước khi trình sếp' : 'Dự trù cho cả đoàn'}</p>
          <h1 className="mt-1 text-3xl font-extrabold sm:text-4xl">{tab === 'quote' ? 'Soát báo giá tour đoàn' : 'Lập kế hoạch chuyến đi công ty'}</h1>
          <p className="mt-2 max-w-2xl text-white/80">{tab === 'quote'
            ? 'Biết tổng chi thật (VAT, vé, tip, vé máy bay ngoài giá) và chứng từ cần có — trong vài giây.'
            : '3 gói Tiết kiệm · Cân bằng · Cao cấp với bảng chi phí, cơ cấu phòng, số xe và lịch từng giờ — mọi con số do code tính.'}</p>
        </div>
      </section>
      {tab === 'quote' ? (
        <main id="main" className="relative mx-auto -mt-8 max-w-6xl px-4 pb-16"><div className="rounded-3xl bg-card p-5 shadow-xl ring-1 ring-black/5 sm:p-8"><QuoteAudit /></div></main>
      ) : (<>
      <div className="relative mx-auto -mt-8 max-w-6xl px-4"><div className="overflow-hidden rounded-2xl shadow-lg ring-1 ring-black/5"><StepBar step={step} skipped={skipped} /></div></div>
      <main id="main" className="mx-auto max-w-6xl px-4 pb-16 pt-8">
        {error && <div className="mb-6"><Notice tone="error" title="Có lỗi">{error}</Notice></div>}
        {body}
      </main>
      </>)}
      </>)}
      <ChatWidget />
    </>
  );
}
