import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { ROUTE_META } from "../lib/agent";
// Each route gets an accent color (mirrors the design's data-route mapping).
const ROUTE_COLOR = {
    COACH: "var(--cyan)",
    WORKOUT_GENERATE: "var(--accent)",
    WORKOUT_LOG: "var(--good)",
    CLARIFY: "var(--amber)",
};
export function RouteBadge({ route, confidence, reason, offline, }) {
    const meta = ROUTE_META[route] ?? ROUTE_META.CLARIFY;
    const color = ROUTE_COLOR[route] ?? "var(--text-2)";
    const pct = Math.round((confidence ?? 0) * 100);
    // animate the confidence meter in
    const [w, setW] = useState(0);
    useEffect(() => {
        const id = requestAnimationFrame(() => setTimeout(() => setW(confidence ?? 0), 60));
        return () => cancelAnimationFrame(id);
    }, [confidence]);
    return (_jsxs("span", { "data-testid": "route-badge", title: reason ?? "", className: "inline-flex items-center gap-[7px] self-start rounded-full border border-line bg-surface py-1 pl-2 pr-[9px] font-mono", children: [_jsx("span", { className: "h-[7px] w-[7px] rounded-full", style: { background: color, boxShadow: `0 0 8px ${color}` } }), _jsx("span", { className: "text-[9.5px] font-bold tracking-[1.2px]", style: { color }, children: meta.label }), _jsx("span", { className: "h-1 w-9 overflow-hidden rounded-full bg-track", children: _jsx("span", { className: "block h-full rounded-full transition-[width] duration-700 ease-out", style: { width: `${w * 100}%`, background: color } }) }), _jsxs("span", { className: "whitespace-nowrap text-[9.5px] font-bold text-muted", children: [_jsx("span", { className: "font-normal tracking-[0.3px] opacity-85", children: "confidence" }), " ", pct, "%"] }), offline ? (_jsx("span", { className: "rounded border border-line px-1 text-[8.5px] tracking-[0.3px] text-muted", children: "local" })) : null] }));
}
