import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/** Quick-reply chips (CLARIFY + welcome starters). */
export function Chips({ items, onPick }) {
    if (!items.length)
        return null;
    return (_jsx("div", { className: "flex max-w-[84%] flex-col items-start gap-[7px]", children: items.map((c) => (_jsx("button", { onClick: () => onPick(c), className: "rounded-[17px] border border-line bg-gradient-to-b from-surface to-[color-mix(in_oklab,var(--surface),#000_16%)] px-[14px] py-[9px] text-left text-[14.5px] leading-[1.3] text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.06),0_1px_3px_rgba(0,0,0,0.28)] transition hover:-translate-y-px hover:border-accent hover:bg-accent-14", children: c }, c))) }));
}
/** Sparkle action pills under a result ("✦ Make this harder"). */
export function GenPills({ items, onPick }) {
    return (_jsx("div", { className: "mt-px flex flex-wrap gap-[7px]", children: items.map((i) => (_jsxs("button", { onClick: () => onPick(i), className: "inline-flex items-center gap-1.5 rounded-full border border-line bg-gradient-to-b from-surface to-[color-mix(in_oklab,var(--surface),#000_16%)] px-[13px] py-[7px] text-[12.5px] font-medium text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] transition hover:-translate-y-px hover:border-accent", children: [_jsx("span", { className: "text-[11px] text-accent", "aria-hidden": true, children: "\u2726" }), i] }, i))) }));
}
