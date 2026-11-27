/** Thương hiệu AuraFarming: vòng hào quang (aura) cam–vàng ôm chiếc lá non (farming) hình ghim định vị (du lịch). */
export function LogoMark({ className = 'size-10' }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={className} role="img" aria-label="Logo AuraFarming">
      <defs>
        <linearGradient id="af-aura" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#fde68a" />
          <stop offset=".45" stopColor="#fb923c" />
          <stop offset="1" stopColor="#ea580c" />
        </linearGradient>
        <linearGradient id="af-leaf" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#5eead4" />
          <stop offset=".55" stopColor="#0e7490" />
          <stop offset="1" stopColor="#06263a" />
        </linearGradient>
        <radialGradient id="af-glow" cx=".5" cy=".42" r=".55">
          <stop offset="0" stopColor="#fff7ed" stopOpacity=".95" />
          <stop offset="1" stopColor="#fff7ed" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="32" cy="32" r="30" fill="url(#af-glow)" />
      {/* vòng aura hở một khe ở góc trên phải — như mặt trời mọc */}
      <path d="M50.6 13.4A26 26 0 1 1 41 7.6" fill="none" stroke="url(#af-aura)" strokeWidth="5" strokeLinecap="round" />
      <circle cx="47" cy="10.4" r="3.4" fill="#fb923c" />
      {/* lá non hình ghim định vị */}
      <path d="M32 52c-1.2-1.6-13-15.4-13-25.2C19 19.6 24.8 14 32 14s13 5.6 13 12.8C45 36.6 33.2 50.4 32 52z" fill="url(#af-leaf)" />
      <path d="M32 47.5V24.5M32 33.5c3.6-1.6 6-4.4 6.6-8M32 40c-3.8-1.4-6.4-4.2-7.2-7.8" fill="none" stroke="#ecfeff" strokeWidth="2.2" strokeLinecap="round" opacity=".9" />
      <ellipse cx="27.5" cy="21" rx="3.2" ry="1.8" fill="#fff" opacity=".45" transform="rotate(-30 27.5 21)" />
    </svg>
  );
}

export function Logo({ dark = false, sub = true }: { dark?: boolean; sub?: boolean }) {
  return (
    <span className="flex items-center gap-2.5">
      <LogoMark className="size-10 drop-shadow-[0_6px_14px_rgba(249,115,22,.35)]" />
      <span className="text-left leading-tight">
        <span className="block text-lg font-extrabold tracking-tight">
          <span className={dark ? 'text-ocean' : 'text-white'}>Aura</span><span className="text-gradient-sun">Farming</span>
        </span>
        {sub && <span className={`block text-[11px] ${dark ? 'text-muted' : 'text-white/70'}`}>Chuyến đi công ty · đúng tiền, đủ hoá đơn</span>}
      </span>
    </span>
  );
}
