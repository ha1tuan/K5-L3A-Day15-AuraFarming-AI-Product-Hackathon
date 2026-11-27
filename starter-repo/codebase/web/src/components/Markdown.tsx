import type { ReactNode } from 'react';
import { InlineMd } from './InlineMd';

/** Markdown khối do máy chủ sinh (agent / soát báo giá): tiêu đề, danh sách, bảng, trích dẫn, đoạn. Không chạy HTML. */
export function Markdown({ text }: { text: string }) {
  const lines = text.replace(/\r/g, '').split('\n');
  const out: ReactNode[] = [];
  let i = 0;
  let k = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) { i++; continue; }
    const h = /^(#{1,4})\s+(.*)$/.exec(l);
    if (h) {
      const lv = h[1].length;
      out.push(<p key={k++} className={lv <= 2 ? 'mt-1 text-base font-extrabold text-ocean' : 'mt-2 font-bold text-ocean'}><InlineMd text={h[2]} /></p>);
      i++; continue;
    }
    if (l.trim().startsWith('|')) {
      const rows: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        const cells = lines[i].trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
        if (!cells.every(c => /^:?-{2,}:?$/.test(c))) rows.push(cells);
        i++;
      }
      out.push(
        <div key={k++} className="-mx-1 overflow-x-auto">
          <table className="w-full text-xs">
            <tbody>{rows.map((r, ri) => (
              <tr key={ri} className={ri === 0 ? 'border-b border-line font-semibold text-muted' : 'border-b border-line/50'}>
                {r.map((c, ci) => <td key={ci} className={`px-1 py-1 align-top ${ci > 0 ? 'text-right whitespace-nowrap' : ''}`}><InlineMd text={c} /></td>)}
              </tr>
            ))}</tbody>
          </table>
        </div>,
      );
      continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
      const ordered = /^\s*\d+\./.test(l);
      const items: ReactNode[] = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        const sub = /^\s{2,}/.test(lines[i]);
        items.push(<li key={i} className={sub ? 'ml-4 list-[circle]' : ''}><InlineMd text={lines[i].replace(/^\s*([-*]|\d+\.)\s+/, '')} /></li>);
        i++;
      }
      out.push(ordered ? <ol key={k++} className="ml-5 grid list-decimal gap-0.5">{items}</ol>
        : <ul key={k++} className="ml-5 grid list-disc gap-0.5">{items}</ul>);
      continue;
    }
    if (l.startsWith('>')) {
      out.push(<p key={k++} className="rounded-lg bg-est-bg px-3 py-2 text-xs text-est"><InlineMd text={l.replace(/^>\s?/, '')} /></p>);
      i++; continue;
    }
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|\||\s*([-*]|\d+\.)\s|>)/.test(lines[i])) { para.push(lines[i]); i++; }
    out.push(<p key={k++}><InlineMd text={para.join(' ')} /></p>);
  }
  return <div className="grid gap-2 text-sm leading-relaxed">{out}</div>;
}
