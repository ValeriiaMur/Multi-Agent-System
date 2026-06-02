import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

// Element styling tuned for a chat bubble: tight margins, modest headings,
// readable lists/code. No raw HTML is rendered (react-markdown is XSS-safe).
const components: Components = {
  p: ({ children }) => <p className="m-0 [&:not(:first-child)]:mt-2">{children}</p>,
  h1: ({ children }) => <p className="m-0 text-[16px] font-bold [&:not(:first-child)]:mt-2.5">{children}</p>,
  h2: ({ children }) => <p className="m-0 text-[15px] font-bold [&:not(:first-child)]:mt-2.5">{children}</p>,
  h3: ({ children }) => <p className="m-0 text-[14px] font-semibold [&:not(:first-child)]:mt-2">{children}</p>,
  ul: ({ children }) => <ul className="my-1 list-disc space-y-1 pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="my-1 list-decimal space-y-1 pl-5">{children}</ol>,
  li: ({ children }) => <li className="leading-snug [&>ul]:mt-1 [&>ol]:mt-1">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-blue underline underline-offset-2">
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code className="rounded bg-chip px-1 py-0.5 font-mono text-[13px]">{children}</code>
  ),
  pre: ({ children }) => (
    <pre className="my-1.5 overflow-x-auto rounded-lg bg-surface-2 p-2.5 font-mono text-[12.5px] leading-snug">
      {children}
    </pre>
  ),
  blockquote: ({ children }) => (
    <blockquote className="my-1.5 border-l-2 border-line pl-2.5 text-ink2">{children}</blockquote>
  ),
  hr: () => <hr className="my-2 border-line-soft" />,
  table: ({ children }) => (
    <div className="my-1.5 overflow-x-auto">
      <table className="w-full border-collapse text-[14px]">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-line px-2 py-1 text-left font-semibold">{children}</th>,
  td: ({ children }) => <td className="border border-line-soft px-2 py-1">{children}</td>,
};

/** Render Markdown text inside a chat bubble. */
export function Markdown({ children }: { children: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {children}
    </ReactMarkdown>
  );
}
