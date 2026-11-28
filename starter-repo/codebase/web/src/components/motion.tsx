import { useEffect, useRef, useState, type ReactNode, type CSSProperties, type ElementType } from 'react';

/** Hiện dần khi cuộn tới (IntersectionObserver) — mượt, chỉ chạy một lần. */
export function Reveal({ children, as: Tag = 'div', delay = 0, variant = 'up', className = '', style, ...rest }: {
  children: ReactNode; as?: ElementType; delay?: number; variant?: 'up' | 'left' | 'right' | 'zoom'; className?: string; style?: CSSProperties;
  role?: string; id?: string; 'aria-label'?: string;
}) {
  const ref = useRef<HTMLElement>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === 'undefined') { setOn(true); return; }
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setOn(true); io.disconnect(); } }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <Tag ref={ref} {...rest} className={`reveal reveal-${variant} ${on ? 'in' : ''} ${className}`} style={{ transitionDelay: `${delay}ms`, ...style }}>{children}</Tag>;
}

/** Số đếm lên khi cuộn tới. */
export function CountUp({ to, decimals = 0, prefix = '', suffix = '', ms = 1600 }: { to: number; decimals?: number; prefix?: string; suffix?: string; ms?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [v, setV] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === 'undefined') { setV(to); return; }
    let raf = 0;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      const t0 = performance.now();
      const tick = (t: number) => {
        const p = Math.min(1, (t - t0) / ms);
        setV(to * (1 - Math.pow(1 - p, 3)));
        if (p < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, { threshold: 0.4 });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); };
  }, [to, ms]);
  return <span ref={ref}>{prefix}{v.toLocaleString('vi-VN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}{suffix}</span>;
}

/** Vị trí cuộn (cho header đổi nền, thanh tiến độ). */
export function useScroll() {
  const [s, setS] = useState({ y: 0, p: 0 });
  useEffect(() => {
    let raf = 0;
    const on = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        setS({ y: window.scrollY, p: h > 0 ? window.scrollY / h : 0 });
      });
    };
    on();
    window.addEventListener('scroll', on, { passive: true });
    return () => { window.removeEventListener('scroll', on); cancelAnimationFrame(raf); };
  }, []);
  return s;
}
