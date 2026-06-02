import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/** Monospace agent-trace console — the real pipeline each turn ran. */
export function Trace({ steps }) {
    if (!steps.length)
        return null;
    return (_jsx("div", { className: "relative flex max-w-full flex-col gap-[3px] self-start rounded-[13px] border border-line-soft bg-surface-2 py-2 pl-[13px] pr-[11px] font-mono before:absolute before:left-[5px] before:top-[9px] before:bottom-[9px] before:w-[2px] before:rounded-[2px] before:bg-accent before:opacity-[0.55]", children: steps.map((s, i) => (_jsxs("div", { className: "flex flex-wrap items-baseline gap-[7px] text-[10.5px] leading-[1.35]", children: [_jsx("span", { className: "shrink-0 whitespace-nowrap text-accent", children: s.tool }), s.arg ? _jsx("span", { className: "min-w-0 break-words text-ink2", children: s.arg }) : null, s.res ? _jsx("span", { className: "ml-auto min-w-0 break-words text-right text-muted", children: s.res }) : null] }, i))) }));
}
