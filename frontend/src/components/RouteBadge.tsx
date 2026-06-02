import type { Route } from "../types";

const LABEL: Record<Route, string> = {
  COACH: "COACH",
  WORKOUT_GENERATE: "GENERATE",
  WORKOUT_LOG: "LOG",
  CLARIFY: "CLARIFY",
};

const COLOR: Record<Route, string> = {
  COACH: "#2563eb",
  WORKOUT_GENERATE: "#16a34a",
  WORKOUT_LOG: "#9333ea",
  CLARIFY: "#d97706",
};

export function RouteBadge({ route, confidence }: { route: Route; confidence: number }) {
  const pct = Math.round(confidence * 100);
  return (
    <span
      data-testid="route-badge"
      style={{
        display: "inline-flex",
        gap: 6,
        alignItems: "center",
        fontSize: 12,
        fontWeight: 600,
        color: "#fff",
        background: COLOR[route],
        borderRadius: 999,
        padding: "2px 10px",
      }}
    >
      {LABEL[route]} · {pct}%
    </span>
  );
}
