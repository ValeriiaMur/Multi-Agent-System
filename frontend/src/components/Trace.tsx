import type { TraceStep } from "../types";

/** Monospace agent-trace console — the real pipeline each turn ran. */
export function Trace({ steps }: { steps: TraceStep[] }) {
  if (!steps.length) return null;
  return (
    <div className="relative flex max-w-full flex-col gap-[3px] self-start rounded-[13px] border border-line-soft bg-surface-2 py-2 pl-[13px] pr-[11px] font-mono before:absolute before:left-[5px] before:top-[9px] before:bottom-[9px] before:w-[2px] before:rounded-[2px] before:bg-accent before:opacity-[0.55]">
      {steps.map((s, i) => (
        <div key={i} className="flex flex-wrap items-baseline gap-[7px] text-[10.5px] leading-[1.35]">
          <span className="shrink-0 whitespace-nowrap text-accent">{s.tool}</span>
          {s.arg ? <span className="min-w-0 break-words text-ink2">{s.arg}</span> : null}
          {s.res ? <span className="ml-auto min-w-0 break-words text-right text-muted">{s.res}</span> : null}
        </div>
      ))}
    </div>
  );
}
