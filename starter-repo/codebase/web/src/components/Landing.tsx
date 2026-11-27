import { useEffect, useMemo, useState } from 'react';
import {
  ArrowRight, CalendarRange, FileSearch, Play, X, MapPin, Sun, Users, Receipt, ShieldCheck, Sparkles,
  Plane, Bus, Waves, Mountain, Landmark, TreePine, ExternalLink, CircleAlert, Clock,
} from 'lucide-react';
import { FEATURED, type Featured } from '../lib/featured';
import { formatVndShort } from '../lib/format';

const thumb = (id: string, q: 'hq' | 'mq' = 'hq') => `https://i.ytimg.com/vi/${id}/${q}default.jpg`;
const HERO_IDS = ['halong', 'phuquoc', 'dalat', 'hoian', 'sapa', 'ninhbinh']
  .map(id => FEATURED.find(f => f.id === id)?.videos[0]?.id).filter(Boolean) as string[];
const NOI_BAT = ['halong', 'phuquoc', 'dalat', 'hoian', 'sapa', 'nhatrang', 'quynhon', 'ninhbinh', 'danang', 'muine', 'catba', 'condao'];
const SCENERY_ICON: Record<string, typeof Waves> = { bien: Waves, vinh: Waves, dao: Waves, nui: Mountain, di_san: Landmark, rung: TreePine };
const SCENERY_VI: Record<string, string> = { bien: 'Biển', vinh: 'Vịnh', dao: 'Đảo', nui: 'Núi', di_san: 'Di sản', rung: 'Rừng', song_nuoc: 'Sông nước', thanh_pho: 'Thành phố', tam_linh: 'Tâm linh', cao_nguyen: 'Cao nguyên' };
type Filter = 'all' | 'Bắc' | 'Trung' | 'Nam' | 'nghi_duong' | 'gan_ket';
const FILTERS: [Filter, string][] = [['all', 'Tất cả'], ['Bắc', 'Miền Bắc'], ['Trung', 'Miền Trung'], ['Nam', 'Miền Nam'], ['nghi_duong', 'Hợp nghỉ dưỡng'], ['gan_ket', 'Hợp team building']];

function VideoModal({ d, onClose, onPlan }: { d: Featured; onClose: () => void; onPlan: (name: string) => void }) {
  const [vid, setVid] = useState(d.videos[0]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', k); document.body.style.overflow = ''; };
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ocean/85 p-3 backdrop-blur-sm sm:p-6" role="dialog" aria-modal="true" aria-label={`Video ${d.name}`} onClick={onClose}>
      <div className="fade-up grid max-h-full w-full max-w-6xl overflow-auto rounded-2xl bg-card shadow-2xl lg:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]" onClick={e => e.stopPropagation()}>
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
      className={`card-lift group relative cursor-pointer overflow-hidden rounded-2xl bg-ocean text-left text-white ${big ? 'sm:col-span-2 sm:row-span-2' : ''}`}>
      <img src={thumb(v.id)} alt="" loading="lazy" className="absolute inset-0 size-full scale-110 object-cover transition duration-700 group-hover:scale-125" />
      <div className="absolute inset-0 bg-gradient-to-t from-ocean via-ocean/40 to-transparent" />
      <div className={`relative flex h-full flex-col p-4 ${big ? 'min-h-[22rem] sm:p-6' : 'min-h-[15rem]'}`}>
        <div className="flex flex-wrap gap-1.5">
          {d.scenery.slice(0, 2).map(s => {
            const I = SCENERY_ICON[s] ?? MapPin;
            return <span key={s} className="glass inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px]"><I className="size-3" aria-hidden />{SCENERY_VI[s] ?? s}</span>;
          })}
          {d.fit.gan_ket >= 3 && <span className="inline-flex items-center gap-1 rounded-full bg-sun/90 px-2 py-0.5 text-[11px] font-medium"><Users className="size-3" aria-hidden />Team building</span>}
        </div>
        <span className="m-auto grid size-14 place-items-center rounded-full bg-white/20 ring-1 ring-white/40 backdrop-blur transition group-hover:scale-110 group-hover:bg-sun">
          <Play className="ml-0.5 size-6 fill-white" aria-hidden />
        </span>
        <div>
          <p className="text-xs text-white/75">{d.province}</p>
          <h3 className={`${big ? 'text-3xl' : 'text-xl'} font-extrabold leading-tight`}>{d.name}</h3>
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

export function Landing({ onStart, onQuote }: { onStart: (destination?: string) => void; onQuote: () => void }) {
  const [filter, setFilter] = useState<Filter>('all');
  const [open, setOpen] = useState<Featured | null>(null);
  const list = useMemo(() => {
    const all = filter === 'all' ? NOI_BAT.map(id => FEATURED.find(f => f.id === id)!).filter(Boolean)
      : FEATURED.filter(f => (filter === 'nghi_duong' || filter === 'gan_ket') ? f.fit[filter] >= 3 : f.region === filter);
    return all.filter(f => f.videos.length);
  }, [filter]);
  const nVideo = FEATURED.reduce((s, f) => s + f.videos.length, 0);

  return (
    <div className="-mt-px">
      {/* HERO ------------------------------------------------------------------------------- */}
      <section className="relative isolate overflow-hidden bg-ocean text-white">
        <div className="kenburns absolute inset-0 -z-20 grid grid-cols-3 grid-rows-2 opacity-90" aria-hidden>
          {HERO_IDS.map(id => <img key={id} src={thumb(id)} alt="" className="size-full object-cover" />)}
        </div>
        <div className="hero-overlay absolute inset-0 -z-10" aria-hidden />
        <div className="mx-auto grid max-w-6xl gap-10 px-4 pb-24 pt-16 sm:pt-24 lg:grid-cols-[1.25fr_1fr] lg:items-center">
          <div>
            <p className="fade-up glass inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium">
              <Sparkles className="size-3.5 text-orange-300" aria-hidden />Cho người tổ chức chuyến đi của cả công ty
            </p>
            <h1 className="fade-up-2 mt-5 text-4xl font-extrabold leading-[1.1] sm:text-6xl">
              Chuyến đi cả công ty —<br /><span className="text-gradient-sun">đúng tiền, đủ hoá đơn,</span><br />không phát sinh bất ngờ.
            </h1>
            <p className="fade-up-3 mt-5 max-w-xl text-lg text-white/85">
              Nhập số người, kinh phí, nơi muốn đi → 3 phương án có bảng chi phí và lịch từng giờ.
              Đã có báo giá tour? Dán vào để biết <b className="text-white">tổng chi thật</b> trước khi trình sếp.
            </p>
            <div className="fade-up-3 mt-8 flex flex-wrap gap-3">
              <button type="button" onClick={() => onStart()} className="inline-flex h-13 cursor-pointer items-center gap-2 rounded-full bg-sun px-7 py-3.5 text-base font-semibold shadow-xl shadow-sun/30 transition hover:-translate-y-0.5 hover:bg-sun-dark">
                <CalendarRange className="size-5" aria-hidden />Lập kế hoạch ngay
              </button>
              <button type="button" onClick={onQuote} className="glass inline-flex h-13 cursor-pointer items-center gap-2 rounded-full px-7 py-3.5 text-base font-semibold transition hover:bg-white/20">
                <FileSearch className="size-5" aria-hidden />Soát báo giá tour
              </button>
            </div>
            <dl className="mt-10 grid max-w-lg grid-cols-3 gap-4 text-center">
              {[['24', 'điểm đến 3 miền'], [String(nVideo), 'video review'], ['3', 'gói mỗi chuyến']].map(([n, l]) => (
                <div key={l} className="glass rounded-2xl px-2 py-3"><dt className="text-2xl font-extrabold sm:text-3xl">{n}</dt><dd className="text-xs text-white/75">{l}</dd></div>
              ))}
            </dl>
          </div>
          {/* Thẻ mẫu: báo giá → tổng chi thật (số thật từ báo giá công khai BCR) */}
          <div className="float-y hidden lg:block">
            <div className="rounded-3xl bg-card p-5 text-primary shadow-2xl ring-1 ring-black/5">
              <p className="flex items-center gap-2 text-sm font-semibold"><Receipt className="size-4 text-sun" aria-hidden />Soát báo giá · 45 khách</p>
              <div className="mt-4 grid gap-2 text-sm">
                <div className="flex justify-between"><span className="text-muted">Giá báo 950.000đ × 45</span><b>42,75 tr</b></div>
                <div className="flex justify-between"><span className="text-muted">+ VAT 10% (ghi "không bao gồm")</span><b className="text-over">+4,28 tr</b></div>
                <div className="flex justify-between"><span className="text-muted">+ Tip HDV, tài xế (ước tính)</span><b className="text-over">+2,25 tr</b></div>
                <div className="mt-1 flex justify-between border-t border-line pt-2 text-base"><span className="font-semibold">Tổng chi thật</span><b className="text-over">49,28 tr</b></div>
              </div>
              <p className="mt-3 flex items-center gap-2 rounded-xl bg-over-bg px-3 py-2 text-xs text-over"><CircleAlert className="size-4 shrink-0" aria-hidden />Giá báo vừa ngân sách 45 tr — tổng thật vượt 4,28 tr</p>
              <p className="mt-2 flex items-center gap-2 rounded-xl bg-ok-bg px-3 py-2 text-xs text-ok"><ShieldCheck className="size-4 shrink-0" aria-hidden />Chuyển khoản từ tài khoản công ty · lấy hoá đơn VAT</p>
            </div>
          </div>
        </div>
      </section>

      {/* NỖI ĐAU ---------------------------------------------------------------------------- */}
      <section className="relative z-10 mx-auto -mt-14 max-w-6xl px-4">
        <div className="grid gap-4 rounded-3xl bg-card p-6 shadow-xl ring-1 ring-black/5 sm:grid-cols-3 sm:p-8">
          {[
            ['83%', 'báo giá tour đoàn để VAT / hoá đơn ngoài giá', '25/30 báo giá công khai, đếm 27/11/2026'],
            ['+15% → +167%', 'tổng chi thật so với giá báo', 'VAT, vé, tip, vé máy bay nằm trong "không bao gồm"'],
            ['≈5,5%', 'review 1–2★ kể đặt rồi mà thiếu phòng', '7.130 review Google Play của 5 app du lịch'],
          ].map(([n, t, s]) => (
            <div key={t}>
              <p className="text-3xl font-extrabold text-sun sm:text-4xl">{n}</p>
              <p className="mt-1 font-semibold">{t}</p>
              <p className="mt-1 text-xs text-muted">{s}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ĐIỂM ĐẾN NỔI BẬT ------------------------------------------------------------------ */}
      <section className="mx-auto max-w-6xl px-4 py-20" aria-labelledby="dest-feat">
        <div className="mb-8 flex flex-wrap items-end gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-accent">Xem trước khi chọn</p>
            <h2 id="dest-feat" className="mt-1 text-3xl font-extrabold sm:text-4xl">Điểm đến nổi bật cho đoàn công ty</h2>
            <p className="mt-2 max-w-2xl text-muted">Bấm vào một nơi để xem video review và team building thật (link đã kiểm), mùa đẹp và giá tham khảo cho cả đoàn.</p>
          </div>
        </div>
        <div className="mb-6 flex flex-wrap gap-2" role="tablist" aria-label="Lọc điểm đến">
          {FILTERS.map(([f, l]) => (
            <button key={f} type="button" role="tab" aria-selected={filter === f} onClick={() => setFilter(f)}
              className={`cursor-pointer rounded-full px-4 py-2 text-sm font-medium transition ${filter === f ? 'bg-ocean text-white shadow' : 'bg-card text-muted ring-1 ring-line hover:text-primary'}`}>{l}</button>
          ))}
        </div>
        <div className="grid auto-rows-auto gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {list.map((d, i) => <DestCard key={d.id} d={d} big={filter === 'all' && i === 0} onOpen={() => setOpen(d)} />)}
        </div>
      </section>

      {/* HAI CÔNG CỤ ------------------------------------------------------------------------ */}
      <section className="bg-ocean py-20 text-white">
        <div className="mx-auto max-w-6xl px-4">
          <p className="text-sm font-semibold uppercase tracking-wider text-orange-300">Hai việc, một chỗ</p>
          <h2 className="mt-1 text-3xl font-extrabold sm:text-4xl">Từ ý tưởng chuyến đi đến tờ trình được duyệt</h2>
          <div className="mt-10 grid gap-6 lg:grid-cols-2">
            {[
              { Icon: CalendarRange, title: 'Lập kế hoạch & dự trù 3 gói', cta: 'Lập kế hoạch', go: () => onStart(),
                steps: ['Nhập số người, số ngày, nơi đi, mục đích + kinh phí và/hoặc địa điểm', 'Chỉ có kinh phí → gợi ý 3 nơi hợp mục đích, vừa tiền', 'So 3 gói Tiết kiệm · Cân bằng · Cao cấp, bỏ gala / team building rồi tính lại', 'Lịch từng giờ, cơ cấu phòng, số xe, giải thích khi vượt ngân sách'] },
              { Icon: FileSearch, title: 'Soát báo giá tour đoàn', cta: 'Soát báo giá', go: onQuote,
                steps: ['Dán báo giá công ty tour gửi (giá / khách, bao gồm, không bao gồm)', 'Cộng VAT, vé, tip, vé máy bay ngoài giá → tổng chi thật', 'Soát hoá đơn, chuyển khoản ≥ 5 triệu, trần phúc lợi — có link nguồn', 'Danh sách câu cần hỏi lại + tờ trình nháp để trình sếp'] },
            ].map(({ Icon, title, cta, go, steps }) => (
              <div key={title} className="glass rounded-3xl p-6 sm:p-8">
                <span className="grid size-12 place-items-center rounded-2xl bg-sun"><Icon className="size-6" aria-hidden /></span>
                <h3 className="mt-4 text-2xl font-bold">{title}</h3>
                <ol className="mt-4 grid gap-3">
                  {steps.map((s, i) => (
                    <li key={s} className="flex gap-3 text-white/85"><span className="grid size-6 shrink-0 place-items-center rounded-full bg-white/15 text-xs font-bold">{i + 1}</span>{s}</li>
                  ))}
                </ol>
                <button type="button" onClick={go} className="mt-6 inline-flex cursor-pointer items-center gap-2 rounded-full bg-white px-6 py-3 font-semibold text-ocean transition hover:bg-orange-100">
                  {cta} <ArrowRight className="size-4" aria-hidden />
                </button>
              </div>
            ))}
          </div>
          <div className="mt-10 grid gap-3 text-sm text-white/75 sm:grid-cols-3">
            <p className="flex gap-2"><ShieldCheck className="size-5 shrink-0 text-orange-300" aria-hidden />Mọi con số do code tính từ dữ liệu có nguồn — AI không tự nhẩm tiền.</p>
            <p className="flex gap-2"><Clock className="size-5 shrink-0 text-orange-300" aria-hidden />Kết quả trong vài giây, sửa yêu cầu là tính lại ngay.</p>
            <p className="flex gap-2"><CircleAlert className="size-5 shrink-0 text-orange-300" aria-hidden />Chỉ đề xuất — không đặt chỗ, không thanh toán thay công ty.</p>
          </div>
        </div>
      </section>

      <footer className="mx-auto max-w-6xl px-4 py-10 text-xs text-muted">
        Dữ liệu: 24 điểm đến dựng từ giá gốc có nguồn (<code>data/gia_chuan.json</code>) · video YouTube kiểm qua oEmbed 27/11/2026 · 30 báo giá tour đoàn công khai (vietnambooking.com) ·
        khách sạn / nhà hàng là mức giá theo hạng, không phải cơ sở cụ thể. Nhóm AuraFarming — AI20K Hackathon Track C.
      </footer>

      {open && <VideoModal d={open} onClose={() => setOpen(null)} onPlan={name => { setOpen(null); onStart(name); }} />}
    </div>
  );
}
