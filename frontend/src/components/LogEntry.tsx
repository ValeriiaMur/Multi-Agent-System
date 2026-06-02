import type { LogEntry } from "../types";

/** Logged-session card — fuzzy-matched names, honest about unmatched entries. */
export function LogCard({ entries }: { entries: LogEntry[] }) {
  const anyMatched = entries.some((e) => e.matched);
  return (
    <div
      data-testid="log-card"
      className="w-full overflow-hidden rounded-[20px] border border-line bg-surface shadow-[0_12px_32px_rgba(0,0,0,0.3)]"
    >
      <div className="flex items-center gap-[9px] border-b border-line-soft px-[15px] py-[13px] text-[15px] font-bold text-ink">
        <span className="inline-flex h-[22px] w-[22px] items-center justify-center rounded-full bg-good text-[13px] text-white">
          ✓
        </span>
        Logged {entries.length} {entries.length === 1 ? "entry" : "entries"}
      </div>
      {entries.map((e, i) => (
        <div
          key={i}
          data-testid="log-entry"
          className={`flex items-center justify-between gap-3 border-b border-line-soft px-[15px] py-3 last:border-none ${
            !e.matched ? "shadow-[inset_3px_0_0_var(--amber)]" : ""
          }`}
        >
          <div>
            <div className="text-[15px] font-medium text-ink">{e.exercise}</div>
            <div className="mt-[3px] text-[13px] tabular-nums text-ink2">
              <b className="font-bold text-ink">
                {e.sets} × {e.reps}
              </b>
              {e.weight != null ? <span className="font-bold text-accent"> @ {e.weight} lbs</span> : null}
            </div>
          </div>
          <div className="flex flex-col items-end gap-1 text-right">
            {e.matched ? (
              <span className="font-mono text-[10px] text-muted">matched in library</span>
            ) : (
              <span className="font-mono text-[10.5px] text-amber">not in library</span>
            )}
          </div>
        </div>
      ))}
      {anyMatched ? (
        <div className="bg-surface-2 px-[15px] py-2.5 font-mono text-[10.5px] text-muted">
          Saved to your training history
        </div>
      ) : null}
    </div>
  );
}
