import { Fragment, type ReactNode } from 'react';

/** Markdown một dòng do máy chủ sinh: **đậm**, *nghiêng*, `mã`, [chữ](link). Không chạy HTML. */
export function InlineMd({ text }: { text: string }) {
  const out: ReactNode[] = [];
  const re = /\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(<Fragment key={k++}>{text.slice(last, m.index)}</Fragment>);
    if (m[1] !== undefined) out.push(<b key={k++}>{m[1]}</b>);
    else if (m[2] !== undefined) out.push(<i key={k++}>{m[2]}</i>);
    else if (m[3] !== undefined) out.push(<code key={k++} className="rounded bg-soft px-1 text-xs">{m[3]}</code>);
    else out.push(<a key={k++} href={m[5]} target="_blank" rel="noreferrer" className="text-accent hover:underline">{m[4]}</a>);
    last = re.lastIndex;
  }
  if (last < text.length) out.push(<Fragment key={k++}>{text.slice(last)}</Fragment>);
  return <>{out}</>;
}
