import { useEffect, useState } from "react";
import type { Route } from "../types";
import { ROUTE_META } from "../lib/agent";

// Each route gets an accent color (mirrors the design's data-route mapping).
const ROUTE_COLOR: Record<Route, string> = {
  COACH: "var(--cyan)",
  WORKOUT_GENERATE: "var(--accent)",
  WORKOUT_LOG: "var(--good)",
  CLARIFY: "var(--amber)",
};

export function RouteBadge({
  route,
  confidence,
  reason,
  offline,
}: {
  route: Route;
  confidence: number;
  reason?: string | null;
  offline?: boolean;
}) {
  const meta = ROUTE_META[route] ?? ROUTE_META.CLARIFY;
  const color = ROUTE_COLOR[route] ?? "var(--text-2)";
  const pct = Math.round((confidence ?? 0) * 100);

  // animate the confidence meter in
  const [w, setW] = useState(0);
  useEffect(() => {
    const id = requestAnimationFrame(() => setTimeout(() => setW(confidence ?? 0), 60));
    return () => cancelAnimationFrame(id);
  }, [confidence]);

  return (
    <span
      data-testid="route-badge"
      title={reason ?? ""}
      className="inline-flex items-center gap-[7px] self-start rounded-full border border-line bg-surface py-1 pl-2 pr-[9px] font-mono"
    >
      <span className="h-[7px] w-[7px] rounded-full" style={{ background: color, boxShadow: `0 0 8px ${color}` }} />
      <span className="text-[9.5px] font-bold tracking-[1.2px]" style={{ color }}>
        {meta.label}
      </span>
      <span className="h-1 w-9 overflow-hidden rounded-full bg-track">
        <span
          className="block h-full rounded-full transition-[width] duration-700 ease-out"
          style={{ width: `${w * 100}%`, background: color }}
        />
      </span>
      <span className="whitespace-nowrap text-[9.5px] font-bold text-muted">
        <span className="font-normal tracking-[0.3px] opacity-85">confidence</span> {pct}%
      </span>
      {offline ? (
        <span className="rounded border border-line px-1 text-[8.5px] tracking-[0.3px] text-muted">local</span>
      ) : null}
    </span>
  );
}
