import { useEffect, useRef, useState } from 'react';
import { MapPinned, CalendarRange, FileSearch } from 'lucide-react';
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

type Tab = 'plan' | 'quote';

export default function App() {
  const [tab, setTab] = useState<Tab>(() => new URLSearchParams(window.location.search).get('tab') === 'bao-gia' ? 'quote' : 'plan');
  const switchTab = (t: Tab) => {
    const u = new URL(window.location.href);
    if (t === 'quote') u.searchParams.set('tab', 'bao-gia'); else u.searchParams.delete('tab');
    window.history.replaceState(null, '', u);
    setTab(t);
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
      <header className="no-print bg-primary text-white">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-4">
          <MapPinned className="size-6" aria-hidden />
          <span className="text-lg font-semibold">Kế hoạch du lịch công ty</span>
          {DEMO && <span className="rounded bg-est-bg px-2 py-0.5 text-xs font-medium text-est">Chế độ demo — dữ liệu mẫu</span>}
          <span className="ml-auto hidden text-sm text-white/70 sm:inline">AI đề xuất · bạn quyết định</span>
        </div>
        <nav className="mx-auto flex max-w-6xl gap-1 px-4" aria-label="Chức năng">
          {([['plan', 'Lập kế hoạch & dự trù', CalendarRange], ['quote', 'Soát báo giá tour', FileSearch]] as const).map(([t, label, Icon]) => (
            <button key={t} type="button" onClick={() => switchTab(t)} aria-current={tab === t ? 'page' : undefined}
              className={`inline-flex cursor-pointer items-center gap-2 rounded-t-lg px-4 py-2.5 text-sm font-medium ${tab === t ? 'bg-white text-primary' : 'text-white/80 hover:bg-white/10'}`}>
              <Icon className="size-4" aria-hidden />{label}
            </button>
          ))}
        </nav>
      </header>
      {tab === 'quote' ? (
        <main id="main" className="mx-auto max-w-6xl px-4 py-8"><QuoteAudit /></main>
      ) : (<>
      <StepBar step={step} skipped={skipped} />
      <main id="main" className="mx-auto max-w-6xl px-4 py-8">
        {error && <div className="mb-6"><Notice tone="error" title="Có lỗi">{error}</Notice></div>}
        {body}
      </main>
      </>)}
    </>
  );
}
