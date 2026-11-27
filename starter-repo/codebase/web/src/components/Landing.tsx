import { useEffect, useMemo, useState } from 'react';
import {
  ArrowRight, CalendarRange, FileSearch, Play, X, MapPin, Sun, Users, Receipt, ShieldCheck, Sparkles,
  Plane, Bus, Waves, Mountain, Landmark, TreePine, ExternalLink, CircleAlert, ChevronDown, Calculator,
  Database, Bot, Ban, MessageSquareText, ListChecks, FileText, Quote,
} from 'lucide-react';
import { FEATURED, type Featured } from '../lib/featured';
import { SCENES, scene, type Scene } from '../lib/scenes';
import { formatVndShort } from '../lib/format';
import { Logo, LogoMark } from './Brand';
import { Reveal, CountUp } from './motion';

const thumb = (id: string, q: 'hq' | 'mq' = 'hq') => `https://i.ytimg.com/vi/${id}/${q}default.jpg`;
const HERO = ['goldenbridge', 'halong', 'khaupha', 'trangan', 'hoian'].map(scene);
const NOI_BAT = ['halong', 'phuquoc', 'dalat', 'hoian', 'sapa', 'nhatrang', 'quynhon', 'ninhbinh', 'danang', 'muine', 'catba', 'condao'];
const SCENERY_ICON: Record<string, typeof Waves> = { bien: Waves, vinh: Waves, dao: Waves, nui: Mountain, di_san: Landmark, di_tich: Landmark, rung: TreePine };
const SCENERY_VI: Record<string, string> = { bien: 'Biển', vinh: 'Vịnh', dao: 'Đảo', nui: 'Núi', di_san: 'Di sản', di_tich: 'Di tích', rung: 'Rừng', song_nuoc: 'Sông nước', thanh_pho: 'Thành phố', tam_linh: 'Tâm linh', doi_cat: 'Đồi cát', dong_co: 'Đồng cỏ', hang_dong: 'Hang động' };
type Filter = 'all' | 'Bắc' | 'Trung' | 'Nam' | 'nghi_duong' | 'gan_ket';
const FILTERS: [Filter, string][] = [['all', 'Nổi bật'], ['Bắc', 'Miền Bắc'], ['Trung', 'Miền Trung'], ['Nam', 'Miền Nam'], ['nghi_duong', 'Nghỉ dưỡng'], ['gan_ket', 'Team building']];
const TEAM = [['Phan Văn Diện', 'Trưởng nhóm'], ['Vũ Hải Tuấn', 'Thành viên'], ['Đoàn Viết Huy', 'Thành viên'], ['Nguyễn Văn Vinh', 'Thành viên']];

function Img({ s, className = '', eager = false }: { s: Scene; className?: string; eager?: boolean }) {
  return <img src={s.src} srcSet={`${s.src} 1920w, ${s.src4k} 3840w`} sizes="100vw" alt={`${s.name}, ${s.province}`}
    loading={eager ? 'eager' : 'lazy'} decoding="async" className={className} />;
}

function Eyebrow({ children, light = false }: { children: React.ReactNode; light?: boolean }) {
  return <p className={`text-xs font-bold uppercase tracking-[.22em] ${light ? 'text-orange-300' : 'text-sun'}`}>{children}</p>;
}

/* --- Video điểm đến -------------------------------------------------------------------------------- */
function VideoModal({ d, onClose, onPlan }: { d: Featured; onClose: () => void; onPlan: (name: string) => void }) {
  const [vid, setVid] = useState(d.videos[0]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', k); document.body.style.overflow = ''; };
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ocean/85 p-3 backdrop-blur-md sm:p-6" role="dialog" aria-modal="true" aria-label={`Video ${d.name}`} onClick={onClose}>
      <div className="fade-up grid max-h-full w-full max-w-6xl overflow-auto rounded-3xl bg-card shadow-2xl lg:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]" onClick={e => e.stopPropagation()}>
        <div className="bg-black">
          <div className="relative aspect-video">
            <iframe key={vid.id} className="absolute inset-0 size-full" title={vid.title}
              src={`https://www.youtube-nocookie.com/embed/${vid.id}?autoplay=1&rel=0`}
              allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen />
          </div>
          <div className="flex items-center gap-2 px-4 py-2 text-xs text-white/70">
            <span className="truncate">{vid.title} — {vid.channel}</span>
            <a href={`https://www.youtube.com/watch?v=${vid.id}`} target="_blank" rel="noreferrer" className="ml-auto inline-flex shrink-0 items-center gap-1 text-white hover:underline">
              Mở trên YouTube <ExternalLink className="size-3" aria-hidden />
            </a>
          </div>
        </div>
        <div className="grid content-start gap-4 p-5">
          <div className="flex items-start gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-accent">{d.province} · Miền {d.region}</p>
              <h3 className="text-2xl font-extrabold">{d.name}</h3>
            </div>
            <button type="button" onClick={onClose} className="ml-auto grid size-9 cursor-pointer place-items-center rounded-full bg-soft hover:bg-line" aria-label="Đóng"><X className="size-5" /></button>
          </div>
          <p className="text-sm text-muted">{d.desc[0].toUpperCase() + d.desc.slice(1)}.</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-xl bg-sun-soft p-3"><p className="text-xs text-muted">Gói tiết kiệm từ</p><p className="text-lg font-bold text-sun-dark">{formatVndShort(d.price_from)}<span className="text-xs font-normal text-muted">/người</span></p></div>
            <div className="rounded-xl bg-accent-soft p-3"><p className="text-xs text-muted">Mùa đẹp</p><p className="text-lg font-bold text-accent-dark">Tháng {d.season}</p></div>
          </div>
          <p className="text-xs text-muted">Giá tham khảo tính bằng code: 30 người, 3N2Đ, từ {d.from} ({d.travel}{d.hours ? `, ~${d.hours} giờ` : ''}).</p>
          <div>
            <p className="mb-2 text-sm font-semibold">Video khác ({d.videos.length})</p>
            <div className="grid grid-cols-2 gap-2">
              {d.videos.map(v => (
                <button key={v.id} type="button" onClick={() => setVid(v)}
                  className={`group relative cursor-pointer overflow-hidden rounded-lg text-left ring-2 ${v.id === vid.id ? 'ring-sun' : 'ring-transparent hover:ring-accent/40'}`}>
                  <img src={thumb(v.id, 'mq')} alt="" loading="lazy" className="aspect-video w-full object-cover" />
                  <span className="absolute left-1.5 top-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-white">{v.kind === 'review' ? 'Review' : 'Team building'}</span>
                </button>
              ))}
            </div>
          </div>
          <button type="button" onClick={() => onPlan(d.name)}
            className="inline-flex h-12 cursor-pointer items-center justify-center gap-2 rounded-full bg-sun font-semibold text-white shadow-lg shadow-sun/30 transition hover:bg-sun-dark">
            Lập kế hoạch đi {d.name} <ArrowRight className="size-4" aria-hidden />
          </button>
        </div>
      </div>
    </div>
  );
}

function DestCard({ d, big, onOpen }: { d: Featured; big?: boolean; onOpen: () => void }) {
  const v = d.videos[0];
  const Icon = d.island || d.hours > 6 ? Plane : Bus;
  return (
    <button type="button" onClick={onOpen}
      className={`card-lift group relative cursor-pointer overflow-hidden rounded-3xl bg-ocean text-left text-white ${big ? 'sm:col-span-2 sm:row-span-2' : ''}`}>
      <img src={thumb(v.id)} alt="" loading="lazy" className="absolute inset-0 size-full scale-110 object-cover transition duration-1000 group-hover:scale-125" />
      <div className="absolute inset-0 bg-gradient-to-t from-ocean via-ocean/35 to-transparent" />
      <div className={`relative flex h-full flex-col p-5 ${big ? 'min-h-[24rem] sm:p-7' : 'min-h-[16rem]'}`}>
        <div className="flex flex-wrap gap-1.5">
          {d.scenery.slice(0, 2).map(s => {
            const I = SCENERY_ICON[s] ?? MapPin;
            return <span key={s} className="glass inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px]"><I className="size-3" aria-hidden />{SCENERY_VI[s] ?? s}</span>;
          })}
          {d.fit.gan_ket >= 3 && <span className="inline-flex items-center gap-1 rounded-full bg-sun/90 px-2 py-0.5 text-[11px] font-medium"><Users className="size-3" aria-hidden />Team building</span>}
        </div>
        <span className="m-auto grid size-14 place-items-center rounded-full bg-white/20 ring-1 ring-white/40 backdrop-blur transition duration-500 group-hover:scale-110 group-hover:bg-sun">
          <Play className="ml-0.5 size-6 fill-white" aria-hidden />
        </span>
        <div>
          <p className="text-xs text-white/75">{d.province}</p>
          <h3 className={`${big ? 'text-3xl sm:text-4xl' : 'text-xl'} font-extrabold leading-tight`}>{d.name}</h3>
          {big && <p className="mt-1 max-w-md text-sm text-white/80">{d.desc[0].toUpperCase() + d.desc.slice(1)}.</p>}
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-white/85">
            <span className="font-semibold text-orange-200">từ {formatVndShort(d.price_from)}/người</span>
            <span className="inline-flex items-center gap-1"><Sun className="size-3" aria-hidden />T{d.season}</span>
            <span className="inline-flex items-center gap-1"><Icon className="size-3" aria-hidden />{d.hours ? `~${d.hours}h từ ${d.from}` : d.from}</span>
          </div>
        </div>
      </div>
    </button>
  );
}

/* --- Hero trình chiếu 4K ------------------------------------------------------------------------- */
function Hero({ onStart, onQuote }: { onStart: () => void; onQuote: () => void }) {
  const [i, setI] = useState(0);
  useEffect(() => { const t = setInterval(() => setI(x => (x + 1) % HERO.length), 7000); return () => clearInterval(t); }, []);
  const cur = HERO[i];
  return (
    <section className="relative isolate flex min-h-[100svh] items-end overflow-hidden bg-ocean text-white">
      <div className="absolute inset-0 -z-20" aria-hidden>
        {HERO.map((s, k) => (
          <div key={s.id} className={`slide ${k === i ? 'active' : ''}`}><Img s={s} eager={k === 0} /></div>
        ))}
      </div>
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(180deg,rgba(6,38,58,.55)_0%,rgba(6,38,58,.15)_35%,rgba(6,38,58,.55)_70%,rgba(6,38,58,.95)_100%)]" aria-hidden />
      <div className="mx-auto w-full max-w-7xl px-4 pb-14 pt-32 sm:px-6 sm:pb-20">
        <p className="fade-up glass inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-medium">
          <Sparkles className="size-3.5 text-orange-300" aria-hidden />AuraFarming · AI cho người tổ chức chuyến đi của cả công ty
        </p>
        <h1 className="fade-up-2 mt-6 max-w-4xl text-[2.6rem] font-extrabold leading-[1.05] tracking-tight drop-shadow-[0_4px_30px_rgba(0,0,0,.35)] sm:text-7xl">
          Đưa cả công ty đi chơi —<br /><span className="text-gradient-sun">đúng tiền, đủ hoá đơn.</span>
        </h1>
        <p className="fade-up-3 mt-6 max-w-2xl text-lg text-white/90 sm:text-xl">
          3 phương án có bảng chi phí và lịch từng giờ trong vài giây. Đã có báo giá tour? Dán vào để biết <b>tổng chi thật</b> trước khi trình sếp.
        </p>
        <div className="fade-up-3 mt-9 flex flex-wrap gap-3">
          <button type="button" onClick={onStart} className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-sun px-8 py-4 text-base font-semibold shadow-2xl shadow-sun/40 transition hover:-translate-y-0.5 hover:bg-sun-dark">
            <CalendarRange className="size-5" aria-hidden />Lập kế hoạch ngay
          </button>
          <button type="button" onClick={onQuote} className="glass inline-flex cursor-pointer items-center gap-2 rounded-full px-8 py-4 text-base font-semibold transition hover:bg-white/20">
            <FileSearch className="size-5" aria-hidden />Soát báo giá tour
          </button>
        </div>
        <div className="mt-14 flex flex-wrap items-end gap-6">
          <div key={cur.id} className="fade-up">
            <p className="flex items-center gap-1.5 text-sm font-semibold"><MapPin className="size-4 text-orange-300" aria-hidden />{cur.name}</p>
            <p className="text-xs text-white/60">{cur.province} · Ảnh: {cur.artist} ({cur.license}, Wikimedia Commons)</p>
          </div>
          <div className="ml-auto flex gap-2" role="tablist" aria-label="Ảnh nền">
            {HERO.map((s, k) => (
              <button key={s.id} type="button" role="tab" aria-selected={k === i} aria-label={s.name} onClick={() => setI(k)}
                className="relative h-1.5 w-10 cursor-pointer overflow-hidden rounded-full bg-white/25 sm:w-14">
                {k === i && <span key={`p${i}`} className="slide-progress absolute inset-0 rounded-full bg-white" />}
                {k < i && <span className="absolute inset-0 rounded-full bg-white/70" />}
              </button>
            ))}
          </div>
        </div>
        <a href="#y-tuong" className="mx-auto mt-10 hidden w-fit flex-col items-center gap-1 text-xs text-white/70 hover:text-white sm:flex">
          Khám phá ý tưởng<ChevronDown className="scroll-cue size-5" aria-hidden />
        </a>
      </div>
    </section>
  );
}

/* --- Trang -------------------------------------------------------------------------------------- */
export function Landing({ onStart, onQuote }: { onStart: (destination?: string) => void; onQuote: () => void }) {
  const [filter, setFilter] = useState<Filter>('all');
  const [open, setOpen] = useState<Featured | null>(null);
  const list = useMemo(() => {
    const all = filter === 'all' ? NOI_BAT.map(id => FEATURED.find(f => f.id === id)!).filter(Boolean)
      : FEATURED.filter(f => (filter === 'nghi_duong' || filter === 'gan_ket') ? f.fit[filter] >= 3 : f.region === filter);
    return all.filter(f => f.videos.length);
  }, [filter]);
  const nVideo = FEATURED.reduce((s, f) => s + f.videos.length, 0);
  const hanoi = scene('hanoi'), hue = scene('hue'), danang = scene('danang');
  const GALLERY = ['phongnha', 'sapa', 'hue', 'phuquoc', 'hoian', 'trangan'].map(scene);

  return (
    <div>
      <Hero onStart={() => onStart()} onQuote={onQuote} />

      {/* Dải tên điểm đến chạy ngang */}
      <div className="overflow-hidden border-y border-white/10 bg-ocean py-4 text-white/80" aria-hidden>
        <div className="marquee flex w-max gap-10 whitespace-nowrap text-sm font-semibold uppercase tracking-[.2em]">
          {[...FEATURED, ...FEATURED].map((f, k) => <span key={k} className="flex items-center gap-10">{f.name}<span className="text-sun">✦</span></span>)}
        </div>
      </div>

      {/* 1. Ý TƯỞNG -------------------------------------------------------------------------------- */}
      <section id="y-tuong" className="mx-auto max-w-7xl scroll-mt-20 px-4 py-24 sm:px-6 sm:py-32">
        <div className="grid gap-14 lg:grid-cols-[1fr_1.1fr] lg:items-center">
          <div>
            <Reveal><Eyebrow>Ý tưởng</Eyebrow></Reveal>
            <Reveal delay={80}><h2 className="mt-3 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
              "Lo chuyến đi cho cả công ty" — việc không ai được đào tạo, nhưng sai là <span className="text-sun">mất tiền thật</span>.
            </h2></Reveal>
            <Reveal delay={160}><p className="mt-6 text-lg leading-relaxed text-muted">
              Giám đốc, HR hay admin được giao một con số và một yêu cầu: <i>"đi đâu đó 3 ngày cho anh em gắn kết"</i>. Họ xin báo giá tour,
              tra giá lẻ trên app, tự cộng trong Excel rồi trình sếp. Nhưng giá trong báo giá <b className="text-primary">không phải số công ty phải chi</b>:
              VAT, vé tham quan, tip, có khi cả vé máy bay nằm trong mục "không bao gồm". Duyệt xong mới phát sinh — hoặc kế toán không thanh toán được vì thiếu hoá đơn.
            </p></Reveal>
            <Reveal delay={240}><p className="mt-4 text-lg leading-relaxed text-muted">
              <b className="text-primary">AuraFarming</b> gom việc đó lại: AI hiểu yêu cầu bằng tiếng Việt, còn <b className="text-primary">mọi con số do code tính</b> từ dữ liệu có nguồn —
              để người tổ chức trình sếp một bản dự trù đúng ngay lần đầu.
            </p></Reveal>
          </div>
          <Reveal variant="right" className="relative">
            <div className="img-zoom relative aspect-[4/5] overflow-hidden rounded-[2rem] shadow-2xl sm:aspect-[5/4] lg:aspect-[4/5]">
              <Img s={scene('trangan')} className="size-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-ocean/70 via-transparent to-transparent" />
              <p className="absolute bottom-4 left-5 text-xs text-white/80">Tràng An, Ninh Bình · Ảnh: {scene('trangan').artist}</p>
            </div>
            <div className="float-y absolute -bottom-8 -left-4 w-72 rounded-3xl bg-card p-5 shadow-2xl ring-1 ring-black/5 sm:-left-10">
              <p className="flex items-center gap-2 text-sm font-semibold"><Receipt className="size-4 text-sun" aria-hidden />Báo giá thật · 45 khách</p>
              <div className="mt-3 grid gap-1.5 text-sm">
                <div className="flex justify-between"><span className="text-muted">Giá báo</span><b>42,75 tr</b></div>
                <div className="flex justify-between"><span className="text-muted">+ VAT 10%</span><b className="text-over">+4,28 tr</b></div>
                <div className="flex justify-between"><span className="text-muted">+ Tip (ước tính)</span><b className="text-over">+2,25 tr</b></div>
                <div className="flex justify-between border-t border-line pt-1.5"><span className="font-semibold">Tổng thật</span><b className="text-over">49,28 tr</b></div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* 2. CON SỐ — nền Hà Nội -------------------------------------------------------------------- */}
      <section className="parallax relative isolate py-24 text-white sm:py-32" style={{ backgroundImage: `url("${hanoi.src4k}")` }}>
        <div className="absolute inset-0 -z-10 bg-ocean/80" aria-hidden />
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <Reveal><Eyebrow light>Bằng chứng, không phải cảm giác</Eyebrow></Reveal>
          <Reveal delay={80}><h2 className="mt-3 max-w-3xl text-4xl font-extrabold leading-tight sm:text-5xl">Nhóm đã đếm trên dữ liệu công khai trước khi xây sản phẩm.</h2></Reveal>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { n: <CountUp to={83} suffix="%" />, t: 'báo giá tour đoàn để VAT / hoá đơn ngoài giá', s: '25/30 báo giá công khai, đếm bằng script, ngưỡng ghi trước' },
              { n: <CountUp to={167} prefix="+" suffix="%" />, t: 'tổng chi thật so với giá báo — ca nặng nhất', s: 'tour "giá rẻ" để vé máy bay ở mục "không bao gồm"' },
              { n: <CountUp to={5.5} decimals={1} prefix="≈" suffix="%" />, t: 'review 1–2★ kể đặt rồi mà thiếu phòng', s: '7.130 review Google Play của 5 app du lịch' },
              { n: <CountUp to={nVideo} />, t: 'video review & team building đã kiểm link', s: `${FEATURED.length} điểm đến · 120 tuyến · giá gốc có nguồn` },
            ].map((x, k) => (
              <Reveal key={k} delay={k * 120} className="glass rounded-3xl p-6">
                <p className="text-5xl font-extrabold text-orange-300">{x.n}</p>
                <p className="mt-3 font-semibold">{x.t}</p>
                <p className="mt-2 text-xs text-white/65">{x.s}</p>
              </Reveal>
            ))}
          </div>
          <p className="mt-8 text-xs text-white/50">Ảnh nền: {hanoi.name} — {hanoi.artist} ({hanoi.license})</p>
        </div>
      </section>

      {/* 3. CÁCH HOẠT ĐỘNG ------------------------------------------------------------------------- */}
      <section className="mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32">
        <div className="text-center">
          <Reveal><Eyebrow>Cách hoạt động</Eyebrow></Reveal>
          <Reveal delay={80}><h2 className="mx-auto mt-3 max-w-3xl text-4xl font-extrabold leading-tight sm:text-5xl">Từ một câu nhắn đến tờ trình được duyệt</h2></Reveal>
        </div>
        <ol className="relative mt-16 grid gap-6 lg:grid-cols-4">
          <span className="absolute left-0 right-0 top-8 hidden h-px bg-gradient-to-r from-transparent via-sun/50 to-transparent lg:block" aria-hidden />
          {[
            { I: MessageSquareText, t: 'Nhắn như nói chuyện', d: '"50 người từ Đà Nẵng, 2 ngày 1 đêm, gắn kết, 200 triệu" — hoặc điền form, hoặc dán báo giá.' },
            { I: Bot, t: 'AI hiểu yêu cầu', d: 'Bóc số người, ngày, nơi đi, mục đích, ngân sách. Thiếu thì hỏi lại, không tự đoán.' },
            { I: Calculator, t: 'Code tính mọi con số', d: 'Chặng đi, xếp phòng rẻ nhất, số xe, ăn, hoạt động, 5% phát sinh, VAT — từ dữ liệu có nguồn.' },
            { I: FileText, t: 'Ra quyết định', d: '3 gói + lịch từng giờ, giải thích khi vượt ngân sách, câu cần hỏi công ty tour, tờ trình nháp.' },
          ].map(({ I, t, d }, k) => (
            <Reveal as="li" key={t} delay={k * 140} className="relative rounded-3xl bg-card p-6 shadow-sm ring-1 ring-black/5">
              <span className="relative z-10 grid size-16 place-items-center rounded-2xl bg-ocean text-white shadow-lg"><I className="size-7" aria-hidden /></span>
              <p className="mt-5 text-xs font-bold text-sun">BƯỚC {k + 1}</p>
              <h3 className="mt-1 text-xl font-bold">{t}</h3>
              <p className="mt-2 text-muted">{d}</p>
            </Reveal>
          ))}
        </ol>
      </section>

      {/* 4. ĐIỂM ĐẾN + VIDEO ----------------------------------------------------------------------- */}
      <section className="bg-soft py-24 sm:py-32" aria-labelledby="dest-feat">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="mb-10 flex flex-wrap items-end gap-6">
            <div>
              <Reveal><Eyebrow>Xem trước khi chọn</Eyebrow></Reveal>
              <Reveal delay={80}><h2 id="dest-feat" className="mt-3 text-4xl font-extrabold leading-tight sm:text-5xl">{FEATURED.length} điểm đến cho đoàn công ty</h2></Reveal>
              <Reveal delay={160}><p className="mt-3 max-w-2xl text-lg text-muted">Bấm vào một nơi để xem video review và team building thật, mùa đẹp và giá tham khảo cho cả đoàn.</p></Reveal>
            </div>
          </div>
          <Reveal className="mb-8 flex flex-wrap gap-2" role="tablist" aria-label="Lọc điểm đến">
            {FILTERS.map(([f, l]) => (
              <button key={f} type="button" role="tab" aria-selected={filter === f} onClick={() => setFilter(f)}
                className={`cursor-pointer rounded-full px-5 py-2.5 text-sm font-semibold transition ${filter === f ? 'bg-ocean text-white shadow-lg' : 'bg-card text-muted ring-1 ring-line hover:text-primary'}`}>{l}</button>
            ))}
          </Reveal>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {list.map((d, k) => (
              <Reveal key={`${filter}-${d.id}`} delay={(k % 4) * 90} variant="zoom" className={filter === 'all' && k === 0 ? 'sm:col-span-2 sm:row-span-2' : ''}>
                <DestCard d={d} big={filter === 'all' && k === 0} onOpen={() => setOpen(d)} />
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* 5. VIỆT NAM QUA ỐNG KÍNH ------------------------------------------------------------------ */}
      <section className="mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
          <div>
            <Reveal><Eyebrow>Cảm hứng</Eyebrow></Reveal>
            <Reveal delay={80}><h2 className="mt-3 text-4xl font-extrabold leading-tight sm:text-5xl">Việt Nam qua ống kính 4K</h2></Reveal>
          </div>
          <Reveal delay={160}><p className="max-w-md text-muted">Ảnh gốc độ phân giải cao từ Wikimedia Commons, giấy phép mở — bấm để xem bản đầy đủ và tác giả.</p></Reveal>
        </div>
        <div className="grid auto-rows-[14rem] gap-4 sm:grid-cols-2 lg:auto-rows-[16rem] lg:grid-cols-4">
          {GALLERY.map((s, k) => (
            <Reveal key={s.id} delay={(k % 3) * 120} variant="zoom"
              className={k === 0 ? 'sm:col-span-2 sm:row-span-2' : k === 3 ? 'lg:col-span-2' : ''}>
              <a href={s.page} target="_blank" rel="noreferrer" className="img-zoom group relative block size-full overflow-hidden rounded-3xl bg-ocean">
                <Img s={s} className="size-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-ocean/85 via-ocean/10 to-transparent opacity-90 transition group-hover:opacity-100" />
                <div className="absolute bottom-0 p-5 text-white">
                  <p className="text-lg font-extrabold">{s.name}</p>
                  <p className="text-xs text-white/70">{s.province} · {s.artist} · {s.license}</p>
                </div>
              </a>
            </Reveal>
          ))}
        </div>
      </section>

      {/* 6. HAI CÔNG CỤ — nền Huế ------------------------------------------------------------------ */}
      <section className="parallax relative isolate py-24 text-white sm:py-32" style={{ backgroundImage: `url("${hue.src4k}")` }}>
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-ocean/90 via-ocean/80 to-ocean/95" aria-hidden />
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <Reveal><Eyebrow light>Hai việc, một chỗ</Eyebrow></Reveal>
          <Reveal delay={80}><h2 className="mt-3 max-w-3xl text-4xl font-extrabold leading-tight sm:text-5xl">Chọn công cụ theo việc bạn đang có trong tay</h2></Reveal>
          <div className="mt-14 grid gap-6 lg:grid-cols-2">
            {[
              { Icon: CalendarRange, title: 'Lập kế hoạch & dự trù 3 gói', cta: 'Lập kế hoạch', go: () => onStart(),
                steps: ['Nhập số người, số ngày, nơi đi, mục đích + kinh phí và/hoặc địa điểm', 'Chỉ có kinh phí → gợi ý 3 nơi hợp mục đích, vừa tiền', 'So 3 gói Tiết kiệm · Cân bằng · Cao cấp, bỏ gala / team building rồi tính lại', 'Lịch từng giờ, cơ cấu phòng, số xe, giải thích khi vượt ngân sách'] },
              { Icon: FileSearch, title: 'Soát báo giá tour đoàn', cta: 'Soát báo giá', go: onQuote,
                steps: ['Dán báo giá công ty tour gửi (giá / khách, bao gồm, không bao gồm)', 'Cộng VAT, vé, tip, vé máy bay ngoài giá → tổng chi thật', 'Soát hoá đơn, chuyển khoản ≥ 5 triệu, trần phúc lợi — có link nguồn', 'Danh sách câu cần hỏi lại + tờ trình nháp để trình sếp'] },
            ].map(({ Icon, title, cta, go, steps }, k) => (
              <Reveal key={title} delay={k * 150} variant={k ? 'right' : 'left'} className="glass rounded-[2rem] p-7 sm:p-9">
                <span className="grid size-14 place-items-center rounded-2xl bg-sun shadow-lg shadow-sun/30"><Icon className="size-7" aria-hidden /></span>
                <h3 className="mt-5 text-2xl font-bold sm:text-3xl">{title}</h3>
                <ol className="mt-5 grid gap-3">
                  {steps.map((s, j) => (
                    <li key={s} className="flex gap-3 text-white/85"><span className="grid size-6 shrink-0 place-items-center rounded-full bg-white/15 text-xs font-bold">{j + 1}</span>{s}</li>
                  ))}
                </ol>
                <button type="button" onClick={go} className="mt-7 inline-flex cursor-pointer items-center gap-2 rounded-full bg-white px-7 py-3.5 font-semibold text-ocean transition hover:-translate-y-0.5 hover:bg-orange-100">
                  {cta} <ArrowRight className="size-4" aria-hidden />
                </button>
              </Reveal>
            ))}
          </div>
          <p className="mt-8 text-xs text-white/50">Ảnh nền: {hue.name} — {hue.artist} ({hue.license})</p>
        </div>
      </section>

      {/* 7. NGUYÊN TẮC ----------------------------------------------------------------------------- */}
      <section className="mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.4fr]">
          <div>
            <Reveal><Eyebrow>Vì sao tin được</Eyebrow></Reveal>
            <Reveal delay={80}><h2 className="mt-3 text-4xl font-extrabold leading-tight sm:text-5xl">AI hiểu — code tính — người quyết.</h2></Reveal>
            <Reveal delay={160}><p className="mt-5 text-lg text-muted">Sai một con số cho cả đoàn là sai cả bản dự trù. Vì vậy AuraFarming tách rõ việc của AI và việc của code.</p></Reveal>
            <Reveal delay={240} className="mt-8 flex gap-3 rounded-3xl bg-sun-soft p-5">
              <Quote className="size-6 shrink-0 text-sun" aria-hidden />
              <p className="text-sm italic text-primary">"Nếu quý khách có nhu cầu xuất hóa đơn, công ty du lịch sẽ phụ thu thêm 10% trên giá tour." <span className="not-italic text-muted">— trích mục "không bao gồm" của một báo giá tour đoàn công khai</span></p>
            </Reveal>
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            {[
              { I: Bot, t: 'AI chỉ hiểu yêu cầu', d: 'Model bóc thông tin từ câu nhắn; số người, ngân sách được code kiểm lại với chữ người dùng viết.' },
              { I: Calculator, t: 'Code tính mọi con số', d: 'Tiền, phòng (quy hoạch động), số xe, giờ đi, VAT, phát sinh 5% — kiểm lại được từng dòng.' },
              { I: Database, t: 'Dữ liệu có nguồn', d: 'Giá gốc có link + ngày xem; số không có nguồn luôn ghi nhãn "ước tính".' },
              { I: Ban, t: 'Không đặt, không thanh toán', d: 'Chỉ đề xuất; từ chối lệnh "bỏ qua ngân sách", che số thẻ / SĐT, không khẳng định còn phòng.' },
              { I: ListChecks, t: 'Đo bằng bộ câu thử', d: '42 câu thử (14 từ dữ liệu thật, 12 trong đó là báo giá tour), chuẩn "đạt" chốt trước; lượt 1: 27/30.' },
              { I: ShieldCheck, t: 'Soát chứng từ', d: 'Hoá đơn VAT, chuyển khoản ≥ 5 triệu, trần phúc lợi — kèm link nguồn, kế toán đối chiếu.' },
            ].map(({ I, t, d }, k) => (
              <Reveal key={t} delay={(k % 2) * 120 + Math.floor(k / 2) * 80} className="card-lift rounded-3xl bg-card p-6 shadow-sm ring-1 ring-black/5">
                <span className="grid size-12 place-items-center rounded-2xl bg-accent-soft text-accent"><I className="size-6" aria-hidden /></span>
                <h3 className="mt-4 text-lg font-bold">{t}</h3>
                <p className="mt-1.5 text-sm text-muted">{d}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* 8. ĐỘI NGŨ -------------------------------------------------------------------------------- */}
      <section className="bg-soft py-24 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6">
          <Reveal className="flex justify-center"><LogoMark className="size-16" /></Reveal>
          <Reveal delay={80}><h2 className="mt-4 text-4xl font-extrabold sm:text-5xl">Đội <span className="text-gradient-sun">AuraFarming</span></h2></Reveal>
          <Reveal delay={160}><p className="mx-auto mt-3 max-w-2xl text-lg text-muted">AI20K Hackathon · Track C — lập kế hoạch du lịch cho cả công ty.</p></Reveal>
          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {TEAM.map(([n, r], k) => (
              <Reveal key={n} delay={k * 110} variant="zoom" className="card-lift rounded-3xl bg-card p-7 shadow-sm ring-1 ring-black/5">
                <span className="mx-auto grid size-20 place-items-center rounded-full bg-gradient-to-br from-accent to-ocean text-2xl font-extrabold text-white shadow-lg">
                  {n.split(' ').slice(-1)[0][0]}
                </span>
                <p className="mt-4 text-lg font-bold">{n}</p>
                <p className={`text-sm ${k === 0 ? 'font-semibold text-sun' : 'text-muted'}`}>{r}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* 9. KÊU GỌI — nền Đà Nẵng ------------------------------------------------------------------ */}
      <section className="parallax relative isolate py-28 text-center text-white sm:py-40" style={{ backgroundImage: `url("${danang.src4k}")` }}>
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-ocean/70 to-ocean/85" aria-hidden />
        <div className="mx-auto max-w-3xl px-4">
          <Reveal><h2 className="text-4xl font-extrabold leading-tight sm:text-6xl">Chuyến đi tới của công ty bạn<br /><span className="text-gradient-sun">bắt đầu từ một câu nhắn.</span></h2></Reveal>
          <Reveal delay={150} className="mt-10 flex flex-wrap justify-center gap-3">
            <button type="button" onClick={() => onStart()} className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-sun px-8 py-4 text-base font-semibold shadow-2xl shadow-sun/40 transition hover:-translate-y-0.5 hover:bg-sun-dark">
              <CalendarRange className="size-5" aria-hidden />Lập kế hoạch ngay
            </button>
            <button type="button" onClick={onQuote} className="glass inline-flex cursor-pointer items-center gap-2 rounded-full px-8 py-4 text-base font-semibold transition hover:bg-white/20">
              <FileSearch className="size-5" aria-hidden />Soát báo giá tour
            </button>
          </Reveal>
          <Reveal delay={250}><p className="mt-6 flex items-center justify-center gap-2 text-sm text-white/75"><CircleAlert className="size-4" aria-hidden />Hoặc bấm robot <b className="text-white">Aura</b> ở góc phải để hỏi trực tiếp.</p></Reveal>
          <p className="mt-10 text-xs text-white/50">Ảnh nền: {danang.name} — {danang.artist} ({danang.license})</p>
        </div>
      </section>

      {/* CHÂN TRANG -------------------------------------------------------------------------------- */}
      <footer className="bg-ocean text-white/70">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1.2fr_1fr_1.4fr]">
          <div>
            <Logo />
            <p className="mt-4 max-w-sm text-sm">Dự trù chuyến đi cả công ty đúng tiền, đủ hoá đơn. Chỉ đề xuất — không đặt chỗ, không thanh toán.</p>
          </div>
          <div className="text-sm">
            <p className="mb-3 font-semibold text-white">Dữ liệu</p>
            <ul className="grid gap-1.5">
              <li>{FEATURED.length} điểm đến · giá gốc có nguồn</li>
              <li>{nVideo} video YouTube kiểm qua oEmbed</li>
              <li>30 báo giá tour đoàn công khai</li>
              <li>Khách sạn / nhà hàng: mức giá theo hạng</li>
            </ul>
          </div>
          <div className="text-xs">
            <p className="mb-3 text-sm font-semibold text-white">Ảnh (Wikimedia Commons)</p>
            <ul className="grid gap-1">
              {SCENES.map(s => (
                <li key={s.id}><a href={s.page} target="_blank" rel="noreferrer" className="hover:text-white hover:underline">{s.name}</a> — {s.artist}, {s.license}</li>
              ))}
            </ul>
          </div>
        </div>
        <p className="border-t border-white/10 py-5 text-center text-xs">© 2026 AuraFarming · AI20K Hackathon Track C</p>
      </footer>

      {open && <VideoModal d={open} onClose={() => setOpen(null)} onPlan={name => { setOpen(null); onStart(name); }} />}
    </div>
  );
}
