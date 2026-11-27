// Bộ giả lập API cho chế độ ?demo=1. Số tiền ở đây cũng tính bằng code (cộng dòng + 5% phát sinh)
// để giao diện hiển thị đúng như dữ liệu thật. Không dùng khi chạy với FastAPI.
import type {
  ApproveInput, Day, DestinationOption, Explanation, LineItem, Package, Plan, Tier, TripEcho, TripInput, TripView,
} from './types';

const store = new Map<string, TripView & { _input: TripInput }>();
const TIERS: Tier[] = ['tiet_kiem', 'can_bang', 'cao_cap'];
const r1k = (n: number) => Math.round(n / 1000) * 1000;

function wait(ms: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal?.addEventListener('abort', () => { clearTimeout(t); reject(new DOMException('Đã huỷ', 'AbortError')); });
  });
}

interface DestSeed { name: string; transport: 'bus' | 'plane'; travel_time: string; km: number; why: string; refs: { articles: number; videos: number }; price: number }
const SEEDS: DestSeed[] = [
  { name: 'Hạ Long', transport: 'bus', travel_time: 'Xe ~3 giờ', km: 170, why: 'Biển và bãi cát rộng cho team building, nhiều khách sạn nhận đoàn lớn, gần Hà Nội.', refs: { articles: 3, videos: 2 }, price: 1 },
  { name: 'Ninh Bình', transport: 'bus', travel_time: 'Xe ~2 giờ', km: 95, why: 'Đi ngắn, cảnh núi đá – sông nước, có khu resort sân vườn hợp hoạt động ngoài trời.', refs: { articles: 4, videos: 1 }, price: 0.85 },
  { name: 'Đà Nẵng', transport: 'plane', travel_time: 'Máy bay ~1h20 + 2h thủ tục', km: 760, why: 'Biển đẹp, nhiều hoạt động, nhưng vé máy bay cho cả đoàn đẩy chi phí lên.', refs: { articles: 5, videos: 3 }, price: 1.15 },
];

function lineItems(seed: DestSeed, tier: Tier, n: number, nights: number, days: number, noGala: boolean, noTb: boolean): LineItem[] {
  const k = TIERS.indexOf(tier);
  const p = seed.price;
  const items: LineItem[] = [];
  const add = (category: string, description: string, qty: number, unit: string, unit_price: number, estimated: boolean, src = false, note?: string) =>
    items.push({ category, description, qty, unit, unit_price: r1k(unit_price), amount: qty * r1k(unit_price), estimated, source_url: src ? '#' : undefined, note });

  if (seed.transport === 'plane') {
    add('Di chuyển', 'Vé máy bay khứ hồi (giá tham khảo)', n, 'vé', [2400000, 2900000, 3600000][k], false, true);
    add('Di chuyển', 'Xe đưa đón sân bay và tham quan', Math.ceil(n / 45), 'xe', 4500000 * days, true);
  } else if (k === 0) {
    add('Di chuyển', `Xe 45 chỗ khứ hồi ${seed.name}`, Math.ceil(n / 45), 'xe', seed.km * 2 * 14000 + 1500000 * (days - 1), true);
  } else {
    add('Di chuyển', `Limousine 16 chỗ khứ hồi ${seed.name}`, Math.ceil(n / 16), 'xe', seed.km * 2 * 17000 + 1200000 * (days - 1), false, true);
  }
  if (nights > 0) {
    const hotel = ['Khách sạn 3★', 'Khách sạn 4★', 'Resort 5★'][k];
    if (k === 2) {
      add('Lưu trú', `${hotel} · phòng 2 người × ${nights} đêm`, Math.ceil(n / 2) * nights, 'phòng·đêm', 3200000 * p, true);
    } else {
      // Xếp phòng rẻ nhất: ưu tiên phòng 4 → 3 → 2 (giá mẫu theo hạng sao).
      const price4 = [900000, 1600000][k] * p, price3 = [750000, 1350000][k] * p, price2 = [600000, 1100000][k] * p;
      let rest = n; const r4 = Math.floor(rest / 4); rest -= r4 * 4;
      let r3 = 0, r2 = 0;
      if (rest === 3) r3 = 1; else if (rest === 2) r2 = 1; else if (rest === 1) r2 = 1;
      if (r4) add('Lưu trú', `${hotel} · phòng 4 người × ${nights} đêm`, r4 * nights, 'phòng·đêm', price4, k === 0, k === 1);
      if (r3) add('Lưu trú', `${hotel} · phòng 3 người × ${nights} đêm`, r3 * nights, 'phòng·đêm', price3, k === 0, k === 1);
      if (r2) add('Lưu trú', `${hotel} · phòng 2 người × ${nights} đêm`, r2 * nights, 'phòng·đêm', price2, k === 0, k === 1);
    }
  }
  const meal = [130000, 190000, 280000][k] * p;
  const mealsCount = days * 2 - 1 - (noGala || k === 0 ? 0 : 1);
  add('Ăn uống', `${mealsCount} bữa chính · ${['suất thường', 'set menu 6–8 món', 'set cao cấp'][k]}`, n * mealsCount, 'suất', meal, k !== 1, k === 1);
  if (nights > 0) add('Ăn uống', 'Bữa sáng buffet khách sạn', 0, 'đã gồm trong giá phòng', 0, false);
  if (k > 0 && !noGala) {
    add('Gala', `Buffet gala ${k === 2 ? 'cao cấp' : ''}`.trim(), n, 'người', [0, 350000, 550000][k] * p, true);
    add('Gala', k === 2 ? 'Sân khấu, MC, ban nhạc, âm thanh ánh sáng' : 'MC + âm thanh ánh sáng + backdrop', 1, 'gói', [0, 8000000, 19000000][k], true);
  }
  if (!noTb) add('Hoạt động', ['Team building tự tổ chức (đạo cụ)', 'Team building 3 giờ có đơn vị tổ chức', 'Team building trọn gói + quay phim'][k], n, 'người', [60000, 250000, 420000][k], true);
  add('Vé', 'Vé tham quan chính', n, 'người', [200000, 300000, 450000][k] * p, false, true);
  return items;
}

function summary(seed: DestSeed, tier: Tier, items: LineItem[], noGala: boolean) {
  const k = TIERS.indexOf(tier);
  const rooms = items.filter(i => i.category === 'Lưu trú' && i.qty > 0)
    .map(i => `${i.qty} ${i.description.split('·')[1]?.split('×')[0].trim() ?? ''}`).join(' + ');
  return {
    transport: items.filter(i => i.category === 'Di chuyển').map(i => `${i.description.split(' khứ')[0]} × ${i.qty}`).join(', '),
    lodging: ['Khách sạn 3★', 'Khách sạn 4★', 'Resort 5★'][k],
    rooms: rooms || '—',
    meals: ['Suất thường', 'Set menu 6–8 món', 'Set cao cấp'][k],
    gala: k === 0 || noGala ? '—' : k === 1 ? 'Buffet + MC, văn nghệ, trao giải, bốc thăm' : 'Buffet cao cấp, sân khấu, ban nhạc',
    activities: ['Tự tổ chức', 'Team building 3 giờ, 6 đội', 'Trọn gói + quay phim'][k] + (seed.transport === 'plane' ? '' : ''),
  };
}

function explain(pkgs: Package[], budget: number): void {
  for (let k = 0; k < pkgs.length; k++) {
    const p = pkgs[k];
    if (p.over_budget === null || p.over_budget <= 0) continue;
    const ex: Explanation = { over_amount: p.over_budget, over_pct: Math.round((p.over_budget / budget) * 100), drivers: [], cuts: [] };
    if (k > 0) {
      const prev = pkgs[k - 1];
      ex.compared_to = prev.tier;
      const byCat = (pk: Package) => pk.line_items.reduce<Record<string, number>>((m, i) => ((m[i.category] = (m[i.category] ?? 0) + i.amount), m), {});
      const a = byCat(p), b = byCat(prev);
      ex.drivers = Object.keys(a).map(c => ({ label: `${c}: ${p.summary[catKey(c)] ?? c}`, amount: a[c] - (b[c] ?? 0) }))
        .filter(d => d.amount > 0).sort((x, y) => y.amount - x.amount).slice(0, 3);
      const cut1 = ex.drivers[0];
      if (cut1) ex.cuts.push({ label: `Hạ ${cut1.label.split(':')[0].toLowerCase()} về mức ${TIER_NAME[prev.tier]}`, saving: r1k(cut1.amount * 1.05), total_after: p.total - r1k(cut1.amount * 1.05) });
      const gala = p.line_items.filter(i => i.category === 'Gala').reduce((s, i) => s + i.amount, 0);
      if (gala) ex.cuts.push({ label: 'Bỏ gala tối', saving: r1k(gala * 1.05), total_after: p.total - r1k(gala * 1.05) });
    } else {
      ex.drivers = [...p.line_items].sort((x, y) => y.amount - x.amount).slice(0, 2).map(i => ({ label: i.description, amount: i.amount }));
      ex.min_budget = p.total;
      ex.cuts.push({ label: 'Bớt 1 ngày 1 đêm', saving: r1k(p.total * 0.3), total_after: p.total - r1k(p.total * 0.3) });
    }
    p.explanation = ex;
  }
}
const TIER_NAME: Record<Tier, string> = { tiet_kiem: 'Tiết kiệm', can_bang: 'Cân bằng', cao_cap: 'Cao cấp' };
function catKey(c: string): keyof Package['summary'] {
  return ({ 'Di chuyển': 'transport', 'Lưu trú': 'lodging', 'Ăn uống': 'meals', Gala: 'gala', 'Hoạt động': 'activities', 'Vé': 'activities' } as const)[c as 'Gala'] ?? 'transport';
}

function packages(seed: DestSeed, n: number, nights: number, days: number, budget: number | null, removed: string[] = []): Package[] {
  const noGala = removed.includes('gala'), noTb = removed.includes('team_building');
  const pkgs = TIERS.map<Package>(tier => {
    const items = lineItems(seed, tier, n, nights, days, noGala, noTb);
    const sub = items.reduce((s, i) => s + i.amount, 0);
    const ps = r1k(sub * 0.05);
    items.push({ category: 'Phát sinh', description: '5% các khoản trên', qty: 1, unit: 'khoản', unit_price: ps, amount: ps, estimated: true });
    const total = sub + ps;
    return { tier, summary: summary(seed, tier, items, noGala), line_items: items, total, per_person: r1k(total / n),
      over_budget: budget === null ? null : total - budget, recommended: false };
  });
  const within = budget === null ? null : pkgs.filter(p => p.total <= budget);
  const rec = budget === null ? pkgs[1] : within!.length ? within![within!.length - 1] : pkgs[0];
  rec.recommended = true;
  if (budget !== null) explain(pkgs, budget);
  return pkgs;
}

function addDays(iso: string, d: number) { const t = new Date(iso + 'T00:00:00'); t.setDate(t.getDate() + d); return t.toISOString().slice(0, 10); }
function nextFriday() { const t = new Date(); t.setDate(t.getDate() + ((5 - t.getDay() + 7) % 7 || 7)); return t.toISOString().slice(0, 10); }
const WD = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

function buildDays(seed: DestSeed, echo: TripEcho, tier: Tier, removed: string[]): Day[] {
  const k = TIERS.indexOf(tier);
  const out: Day[] = [];
  const setMenu = (name: string, price: number, dishes: string[], src = false) => ({ name, price_per_pax: price, table_size: 10, dishes, drinks_note: 'Trà đá, nước lọc (đồ uống khác tính riêng)', estimated: !src, source_url: src ? '#' : undefined });
  for (let d = 0; d < echo.days; d++) {
    const date = addDays(echo.start_date, d);
    const wd = WD[new Date(date + 'T00:00:00').getDay()];
    const slots: Day['slots'] = [];
    if (d === 0) {
      slots.push({ start: seed.transport === 'plane' ? '05:30' : '06:30', kind: 'travel', title: `Xuất phát từ ${echo.origin}`, note: seed.transport === 'plane' ? 'Tập trung sân bay, bay ~1h20' : `${summary(seed, tier, [], false).transport || 'Xe'} · ${seed.travel_time.replace('Xe ', '')}, nghỉ 20 phút giữa đường` });
      if (echo.nights > 0) slots.push({ start: '10:00', kind: 'hotel', title: `Nhận phòng: ${['Khách sạn Hoàng Gia (3★)', 'KS Mường Thanh Grand (4★)', 'Resort Vinpearl (5★)'][k]}`, note: 'Nhận đoàn lớn, gần trung tâm', flags: ['confirm_rooms'], source_url: '#' });
      slots.push({ start: '11:30', kind: 'meal', title: 'Ăn trưa: Nhà hàng Hồng Hạnh 3', note: `Hải sản, phòng riêng cho đoàn ${echo.headcount} người`, flags: ['confirm_capacity'],
        menu: setMenu('Set hải sản trưa', [140000, 180000, 280000][k], ['Súp hải sản', 'Chả mực', 'Tôm hấp bia', 'Cá song hấp xì dầu', 'Rau muống xào tỏi', 'Canh ngao chua', 'Cơm trắng · trái cây tráng miệng'], true) });
      if (!removed.includes('team_building')) slots.push({ start: '14:00', kind: 'activity', title: 'Team building trên bãi biển', note: k === 0 ? 'Tự tổ chức · công ty cử 2 người điều phối' : '3 giờ · đơn vị tổ chức có MC, âm thanh, đạo cụ', flags: ['estimate'],
        program: { title: `Chủ đề "Chung một con thuyền" · chia ${Math.max(2, Math.round(echo.headcount / 10))} đội × ~10 người`, steps: [
          { start: '14:00', end: '14:20', text: 'Khởi động tập thể, chia đội, đặt tên & khẩu hiệu đội' },
          { start: '14:20', end: '15:00', text: 'Trò 1 · Kết nối: "Bước chân đồng đội", "Truyền nước"' },
          { start: '15:00', end: '15:45', text: 'Trò 2 · Phối hợp: "Mê cung bịt mắt", "Xây tháp ống hút"' },
          { start: '15:45', end: '16:00', text: 'Nghỉ, uống nước' },
          { start: '16:00', end: '16:45', text: 'Trò 3 · Thử thách lớn: "Kéo co mật mã" — giải câu đố để lấy lượt kéo' },
          { start: '16:45', end: '17:00', text: 'Tổng kết điểm, chụp ảnh đội (giải thưởng trao ở gala)' },
        ], includes: k === 0 ? 'Đạo cụ cơ bản; công ty tự cử người dẫn.' : 'MC + 3 hướng dẫn viên, loa, áo đội, đạo cụ, nước uống.', fallback: 'Trời mưa → chuyển vào sảnh khách sạn (trò 2, 3).' } });
      slots.push({ start: '18:00', kind: 'meal', title: 'Ăn tối tại khách sạn', flags: ['estimate'],
        menu: setMenu('Set menu tối', [130000, 200000, 300000][k], ['Gỏi ngó sen tôm thịt', 'Gà luộc lá chanh', 'Bò xào cần tỏi', 'Mực xào thập cẩm', 'Đậu phụ sốt cà chua', 'Canh cua mồng tơi', 'Cơm trắng · hoa quả']) });
      slots.push({ start: '20:00', kind: 'rest', title: 'Tự do / nghỉ ngơi' });
    } else if (d < echo.days - 1) {
      slots.push({ start: '08:00', kind: 'sight', title: 'Tham quan chính: du thuyền vịnh', note: '4 giờ · hang động, đảo', source_url: '#', details: '08:00 đón tại cảng → 09:15 hang Sửng Sốt (1 giờ) → 10:45 đảo Ti Tốp (tắm biển / leo đỉnh, 1 giờ) → 12:00 về cảng. Vé đã gồm phí tham quan.' });
      slots.push({ start: '12:30', kind: 'meal', title: 'Ăn trưa trên du thuyền', flags: ['estimate'], menu: setMenu('Set trưa trên tàu', [150000, 220000, 320000][k], ['Chả mực', 'Ngao hấp sả', 'Cá thu sốt cà', 'Rau xào theo mùa', 'Canh chua hải sản', 'Cơm · trái cây']) });
      slots.push({ start: '15:00', kind: 'rest', title: 'Nghỉ ngơi tự do', note: 'Hồ bơi khách sạn / dạo biển' });
      if (k > 0 && !removed.includes('gala')) slots.push({ start: '18:30', kind: 'gala', title: 'Gala tối "Vươn khơi"', note: `Sảnh tiệc khách sạn · 3 giờ · buffet + chương trình`, flags: ['estimate'],
        program: { steps: [
          { start: '18:30', end: '19:00', text: 'Đón khách, chụp ảnh tại backdrop' },
          { start: '19:00', end: '19:15', text: 'Khai mạc: MC giới thiệu, giám đốc phát biểu' },
          { start: '19:15', end: '19:45', text: 'Tiệc buffet — vừa ăn vừa xem clip kỷ niệm năm' },
          { start: '19:45', end: '20:15', text: 'Văn nghệ: tiết mục của từng phòng ban (đăng ký trước)' },
          { start: '20:15', end: '20:35', text: 'Trao giải team building & vinh danh nhân viên' },
          { start: '20:35', end: '21:15', text: 'Mini game sân khấu + bốc thăm may mắn' },
          { start: '21:15', end: '21:30', text: 'Hát tập thể, bế mạc' },
        ], includes: (k === 2 ? 'Sân khấu, ban nhạc, MC, âm thanh ánh sáng, backdrop.' : 'MC, âm thanh ánh sáng cơ bản, backdrop in tên công ty.') + ' Quà bốc thăm và giải thưởng do công ty tự chuẩn bị (không tính trong dự trù).' },
        menu: { name: 'Buffet gala', price_per_pax: [0, 350000, 550000][k], dishes: ['Khai vị: gỏi cuốn, salad hải sản', 'Hải sản: tôm nướng, mực hấp gừng, hàu nướng mỡ hành', 'Món chính: bò lúc lắc, gà nướng mật ong, cá hồi áp chảo', 'Lẩu thái hải sản', 'Tráng miệng: chè, bánh ngọt, hoa quả'], drinks_note: 'Bia + nước ngọt: 2 lon / người', estimated: true } });
      else slots.push({ start: '18:30', kind: 'meal', title: 'Ăn tối nhà hàng địa phương', flags: ['estimate'], menu: setMenu('Set menu tối', [130000, 200000, 300000][k], ['Lẩu hải sản', 'Gà rang muối', 'Rau xào', 'Cơm · trái cây']) });
    }
    if (d === echo.days - 1 && echo.days > 1) {
      slots.push({ start: '08:30', kind: 'sight', title: 'Cáp treo & vòng quay', note: '2 giờ', source_url: '#', details: 'Cáp treo lên đỉnh → vòng quay → chụp ảnh tập thể. Vé theo bảng giá niêm yết.' });
      slots.push({ start: '11:30', kind: 'meal', title: 'Ăn trưa, trả phòng', flags: ['estimate'], menu: setMenu('Set trưa nhẹ', [120000, 160000, 240000][k], ['Bún chả mực', 'Nem rán', 'Rau sống', 'Trà đá']) });
    }
    if (d === echo.days - 1) slots.push({ start: echo.days === 1 ? '16:00' : '13:30', kind: 'travel', title: `Về ${echo.origin}`, note: `${seed.travel_time} · dự kiến tới ${echo.days === 1 ? '19:00' : '16:30'}` });
    out.push({ label: `Ngày ${d + 1}`, date: `${wd} ${date.slice(8, 10)}/${date.slice(5, 7)}`, slots });
  }
  return out;
}

function plan(seed: DestSeed, echo: TripEcho, pkg: Package, removed: string[]): Plan {
  const estimate_total = r1k(pkg.total * 0.965);
  return { tier: pkg.tier, destination: seed.name, total: pkg.total, per_person: pkg.per_person, estimate_total,
    estimate_note: 'Khách sạn và nhà hàng cụ thể đắt hơn mức giá chung của hạng.',
    over_budget: pkg.over_budget, explanation: pkg.explanation, days: buildDays(seed, echo, pkg.tier, removed) };
}

function seedFor(name: string): DestSeed {
  return SEEDS.find(s => s.name.toLowerCase() === name.trim().toLowerCase()) ?? { ...SEEDS[0], name: name.trim(), refs: { articles: 2, videos: 1 } };
}

export async function createTrip(input: TripInput, signal?: AbortSignal): Promise<TripView> {
  await wait(2200, signal);
  const id = 'demo-' + Math.random().toString(36).slice(2, 8);
  const missing: TripView['missing_fields'] = [];
  if (!input.headcount) missing.push('headcount');
  if (!input.origin.trim()) missing.push('origin');
  if (!input.purpose) missing.push('purpose');
  if (!input.budget && !input.destination.trim()) missing.push('budget_or_destination');
  if (missing.length) {
    const v: TripView = { trip_id: id, status: 'ask_back', message: 'Cần thêm thông tin trước khi lập kế hoạch.', missing_fields: missing };
    return v;
  }
  if (input.headcount! < 5 || input.headcount! > 500) {
    return { trip_id: id, status: 'refused', message: 'Hệ thống hỗ trợ đoàn từ 5 đến 500 người. Với đoàn lớn hơn, nên chia đợt hoặc làm việc với đơn vị tổ chức sự kiện.' };
  }
  const n = input.headcount!;
  const budget = input.budget === null ? null : input.budget_per_person ? input.budget * n : input.budget;
  const start = input.start_date || nextFriday();
  const echo: TripEcho = { headcount: n, days: input.days, nights: input.days - 1, start_date: start, end_date: addDays(start, input.days - 1),
    origin: input.origin.trim(), purpose: input.purpose!, budget, entry: input.destination.trim() ? (budget ? 'C' : 'B') : 'A' };
  let view: TripView;
  if (echo.entry === 'A') {
    const dests: DestinationOption[] = SEEDS.map(s => ({ name: s.name, transport: s.transport, travel_time: s.travel_time, why: s.why,
      refs: { ...s.refs, url: '#' }, packages: packages(s, n, echo.nights, echo.days, budget), recommended: false }));
    dests.sort((a, b) => Number(b.packages[1].total <= budget!) - Number(a.packages[1].total <= budget!));
    dests[0].recommended = true;
    view = { trip_id: id, status: 'choose_destination', message: 'Gợi ý địa điểm phù hợp.', request: echo, destinations: dests };
  } else {
    const seed = seedFor(input.destination);
    const pkgs = packages(seed, n, echo.nights, echo.days, budget);
    if (echo.entry === 'B') view = { trip_id: id, status: 'choose_package', message: 'Dự trù kinh phí 3 gói.', request: echo, destination: seed.name, packages: pkgs };
    else view = { trip_id: id, status: 'ok', message: '3 kế hoạch chi tiết.', request: echo, destination: seed.name, packages: pkgs, plans: pkgs.map(p => plan(seed, echo, p, [])) };
  }
  store.set(id, { ...view, _input: input });
  return view;
}

export async function approveTrip(id: string, body: ApproveInput, signal?: AbortSignal): Promise<TripView> {
  await wait(1800, signal);
  const prev = store.get(id);
  if (!prev?.request) return { trip_id: id, status: 'error', message: 'Không tìm thấy chuyến đi. Hãy lập lại từ đầu.' };
  const echo = { ...prev.request, headcount: body.headcount ?? prev.request.headcount };
  const seed = seedFor(body.destination ?? prev.destination ?? SEEDS[0].name);
  const pkgs = packages(seed, echo.headcount, echo.nights, echo.days, echo.budget, body.remove_items);
  const chosen = pkgs.find(p => p.tier === body.package)!;
  const view: TripView = { trip_id: id, status: 'ok', message: 'Kế hoạch chi tiết.', request: echo, destination: seed.name, packages: pkgs, plans: [plan(seed, echo, chosen, body.remove_items ?? [])] };
  store.set(id, { ...view, _input: prev._input });
  return view;
}

export async function getTrip(id: string): Promise<TripView> {
  const v = store.get(id);
  if (!v) return { trip_id: id, status: 'error', message: 'Phiên demo đã hết (dữ liệu demo chỉ giữ trong tab này).' };
  return v;
}
