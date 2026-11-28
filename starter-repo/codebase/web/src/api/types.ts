// Hợp đồng với FastAPI (codebase/backend/src/api/schemas.py — Task 9′ chốt theo file này).
// Mọi con số do máy chủ tính; web chỉ hiển thị.

export type Tier = 'tiet_kiem' | 'can_bang' | 'cao_cap';
export type Purpose = 'gan_ket' | 'nghi_duong' | 'ca_hai';
export type Status = 'choose_destination' | 'choose_package' | 'ok' | 'ask_back' | 'refused' | 'error';
export type Field = 'headcount' | 'days' | 'start_date' | 'origin' | 'purpose' | 'budget_or_destination';

export interface TripInput {
  headcount: number | null;
  days: number;
  start_date: string | null;
  origin: string;
  purpose: Purpose | null;
  budget: number | null;
  budget_per_person: boolean;
  destination: string;
}

/** "Đã hiểu": máy chủ nhắc lại yêu cầu sau khi chuẩn hoá (vd ngân sách mỗi người × số người). */
export interface TripEcho {
  headcount: number;
  days: number;
  nights: number;
  start_date: string;
  end_date: string;
  origin: string;
  purpose: Purpose;
  budget: number | null;
  entry: 'A' | 'B' | 'C';
}

export interface LineItem {
  category: string;
  description: string;
  qty: number;
  unit: string;
  unit_price: number;
  amount: number;
  estimated: boolean;
  source_url?: string;
  note?: string;
}

export interface Explanation {
  over_amount: number;
  over_pct: number;
  compared_to?: Tier;
  drivers: { label: string; amount: number }[];
  cuts: { label: string; saving: number; total_after: number }[];
  min_budget?: number;
}

/** Tóm tắt từng hạng mục cho bảng so 3 gói. */
export interface PackageSummary {
  transport: string;
  lodging: string;
  rooms: string;
  meals: string;
  gala: string;
  activities: string;
}

export interface Package {
  tier: Tier;
  summary: PackageSummary;
  line_items: LineItem[];
  total: number;
  per_person: number;
  over_budget: number | null;
  recommended: boolean;
  explanation?: Explanation;
}

export interface DestinationOption {
  name: string;
  transport: 'bus' | 'plane';
  travel_time: string;
  why: string;
  refs: { articles: number; videos: number; url?: string };
  packages: Package[];
  recommended: boolean;
}

export interface Menu {
  name: string;
  price_per_pax: number;
  table_size?: number;
  dishes: string[];
  drinks_note?: string;
  source_url?: string;
  estimated: boolean;
}

export interface ProgramStep { start: string; end: string; text: string }

export type SlotKind = 'travel' | 'hotel' | 'meal' | 'activity' | 'gala' | 'sight' | 'rest';

export interface Slot {
  start: string;
  kind: SlotKind;
  title: string;
  note?: string;
  flags?: ('estimate' | 'confirm_rooms' | 'confirm_capacity')[];
  source_url?: string;
  menu?: Menu;
  program?: { title?: string; steps: ProgramStep[]; includes?: string; fallback?: string };
  details?: string;
}

export interface Day { label: string; date: string; slots: Slot[] }

export interface Plan {
  tier: Tier;
  destination: string;
  total: number;
  per_person: number;
  estimate_total: number;
  estimate_note?: string;
  over_budget: number | null;
  explanation?: Explanation;
  days: Day[];
  /** Cảnh báo (về muộn, bỏ việc không đủ giờ…), thông tin thêm (cách đi, nơi ở, mùa đẹp) và video review đã kiểm link. */
  notes?: string[];
  info?: string[];
  videos?: { title: string; url: string; channel: string; kind?: string }[];
  extra?: {
    travel: string;
    lodging: string;
    season: { months: string; in_season: boolean; month_now: number };
    sights: string[];
    price_note: string;
  };
}

export interface TripView {
  trip_id: string;
  status: Status;
  message: string;
  request?: TripEcho;
  missing_fields?: Field[];
  destinations?: DestinationOption[];
  destination?: string;
  packages?: Package[];
  plans?: Plan[];
  /** Sửa ngay trên trang kế hoạch (POST /api/trips/{id}/recalc). */
  customize?: { options: string[]; removed: string[]; headcount: number; days: number };
  map?: { origin: MapPoint; dest: MapPoint; mode: 'bus' | 'plane'; routes?: Partial<Record<Tier, RouteLeg[]>> };
}

export interface MapPoint { name: string; lat: number; lon: number }

/** Một chặng đi: đường bộ vẽ theo bản đồ thật (OSRM / OpenStreetMap), chặng bay vẽ cung. */
export interface RouteLeg {
  from: string; to: string; mode: 'road' | 'flight'; vehicle: string;
  km: number | null; hours: number | null; path: [number, number][]; approx: boolean; ferry?: boolean;
}

export interface RecalcInput { headcount?: number; days?: number; removed?: string[] }

export interface ApproveInput {
  destination?: string;
  package: Tier;
  headcount?: number;
  remove_items?: ('gala' | 'team_building')[];
}

/** Soát báo giá tour đoàn (POST /api/quote-audit) — mọi số do máy chủ tính. */
export interface QuoteLine { ten: string; so_luong: number; don_vi: string; don_gia: number; thanh_tien: number }
export interface QuoteResult {
  status: 'ok' | 'ask_back';
  message?: string;
  so_nguoi?: number;
  dia_diem?: string | null;
  gia_moi_khach?: number;
  gia_bao?: number;
  tong?: number;
  moi_nguoi?: number;
  ngan_sach?: number | null;
  vuot?: number | null;
  chenh_pct?: number;
  dong?: QuoteLine[];
  vi_sao_vuot?: string[];
  tham_chieu?: string;
  chung_tu?: string[];
  ca_nhan?: string[];
  cau_hoi?: string[];
  to_trinh?: string;
  markdown?: string;
  doi_chieu?: QuoteCompare;
}

export interface QuoteCompare {
  tier: Tier; ke_hoach: number; ke_hoach_moi_nguoi: number; bao_gia_that: number; chenh: number; chenh_pct: number; nhan_xet: string;
}
