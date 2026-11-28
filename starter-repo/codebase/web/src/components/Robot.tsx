/** Robot "Aura" — hoạt hình 3D bằng SVG (đổ bóng, phản quang, chuyển động CSS: lơ lửng, chớp mắt, ăng-ten sáng, vẫy tay). */
export function Robot({ className = 'size-24', waving = false, talking = false }: { className?: string; waving?: boolean; talking?: boolean }) {
  return (
    <svg viewBox="0 0 120 140" className={`${className} overflow-visible`} aria-hidden>
      <defs>
        <radialGradient id="rb-head" cx=".35" cy=".3" r=".85">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset=".55" stopColor="#e6f4f8" />
          <stop offset="1" stopColor="#a9c7d3" />
        </radialGradient>
        <radialGradient id="rb-body" cx=".35" cy=".25" r=".9">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset=".6" stopColor="#dbeef4" />
          <stop offset="1" stopColor="#94b8c6" />
        </radialGradient>
        <linearGradient id="rb-visor" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0b4a63" />
          <stop offset="1" stopColor="#041a28" />
        </linearGradient>
        <radialGradient id="rb-eye" cx=".5" cy=".4" r=".6">
          <stop offset="0" stopColor="#ecfeff" />
          <stop offset=".5" stopColor="#67e8f9" />
          <stop offset="1" stopColor="#0891b2" />
        </radialGradient>
        <radialGradient id="rb-bulb" cx=".4" cy=".35" r=".7">
          <stop offset="0" stopColor="#fff7ed" />
          <stop offset=".45" stopColor="#fb923c" />
          <stop offset="1" stopColor="#c2410c" />
        </radialGradient>
        <linearGradient id="rb-ear" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#fdba74" />
          <stop offset="1" stopColor="#ea580c" />
        </linearGradient>
        <filter id="rb-soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" /></filter>
      </defs>

      {/* bóng dưới chân */}
      <ellipse className="robot-shadow" cx="60" cy="134" rx="30" ry="5" fill="#06263a" opacity=".25" />

      <g className="robot-bob">
        {/* ăng-ten */}
        <path d="M60 22 V10" stroke="#7ea3b3" strokeWidth="3" strokeLinecap="round" />
        <circle className="robot-glow" cx="60" cy="8" r="9" fill="#fb923c" opacity=".35" filter="url(#rb-soft)" />
        <circle cx="60" cy="8" r="5.5" fill="url(#rb-bulb)" />
        <circle cx="58" cy="6" r="1.6" fill="#fff" opacity=".9" />

        {/* tai */}
        <rect x="13" y="38" width="10" height="20" rx="5" fill="url(#rb-ear)" />
        <rect x="97" y="38" width="10" height="20" rx="5" fill="url(#rb-ear)" />

        {/* đầu */}
        <rect x="20" y="20" width="80" height="58" rx="26" fill="url(#rb-head)" stroke="#8fb3c2" strokeWidth="1.2" />
        <ellipse cx="42" cy="29" rx="14" ry="5" fill="#fff" opacity=".85" transform="rotate(-12 42 29)" />

        {/* kính mặt + mắt + miệng */}
        <rect x="29" y="34" width="62" height="34" rx="16" fill="url(#rb-visor)" />
        <rect x="33" y="36" width="30" height="6" rx="3" fill="#fff" opacity=".12" />
        <g className="robot-eyes">
          <ellipse cx="47" cy="50" rx="6.5" ry="7.5" fill="url(#rb-eye)" />
          <ellipse cx="73" cy="50" rx="6.5" ry="7.5" fill="url(#rb-eye)" />
          <circle cx="45" cy="47.5" r="2" fill="#fff" />
          <circle cx="71" cy="47.5" r="2" fill="#fff" />
        </g>
        {talking
          ? <ellipse className="robot-talk" cx="60" cy="61" rx="5" ry="3" fill="#67e8f9" />
          : <path d="M53 60 Q60 66 67 60" fill="none" stroke="#67e8f9" strokeWidth="2.6" strokeLinecap="round" />}
        <ellipse cx="36" cy="62" rx="4" ry="2.4" fill="#fb7185" opacity=".55" />
        <ellipse cx="84" cy="62" rx="4" ry="2.4" fill="#fb7185" opacity=".55" />

        {/* cổ + thân */}
        <rect x="50" y="76" width="20" height="8" rx="3" fill="#9dbccb" />
        <path d="M32 100c0-12 12-18 28-18s28 6 28 18v8c0 10-12 18-28 18s-28-8-28-18z" fill="url(#rb-body)" stroke="#8fb3c2" strokeWidth="1.2" />
        <ellipse cx="46" cy="92" rx="9" ry="3.6" fill="#fff" opacity=".8" transform="rotate(-10 46 92)" />
        {/* ngực: mini logo aura */}
        <circle cx="60" cy="104" r="9.5" fill="#06263a" />
        <path d="M66 98.6A7 7 0 1 1 63.4 97" fill="none" stroke="#fb923c" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M60 110c-.4-.6-4-4.6-4-7.6a4 4 0 0 1 8 0c0 3-3.6 7-4 7.6z" fill="#5eead4" />

        {/* tay trái (vẫy) + tay phải */}
        <g className={waving ? 'robot-wave' : 'robot-wave-idle'} style={{ transformOrigin: '34px 96px' }}>
          <path d="M34 96 Q20 88 16 74" fill="none" stroke="#9dbccb" strokeWidth="7" strokeLinecap="round" />
          <circle cx="15.5" cy="72" r="6.5" fill="url(#rb-ear)" />
        </g>
        <path d="M86 96 Q98 104 100 114" fill="none" stroke="#9dbccb" strokeWidth="7" strokeLinecap="round" />
        <circle cx="100.5" cy="116" r="6.5" fill="url(#rb-ear)" />
      </g>
    </svg>
  );
}
