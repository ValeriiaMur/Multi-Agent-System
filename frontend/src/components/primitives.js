import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
/** Muscle / equipment chip. `ink` variant = accent-tinted. */
export function Tag({ children, variant }) {
    const base = "rounded-md border px-1.5 py-0.5 text-[10.5px] whitespace-nowrap leading-none py-1";
    return variant === "ink" ? (_jsx("span", { className: `${base} border-accent-22 bg-accent-14 text-accent`, children: children })) : (_jsx("span", { className: `${base} border-line-soft bg-chip text-ink2`, children: children }));
}
/** Typing indicator with sparkle + bouncing dots. */
export function Typing({ label }) {
    return (_jsxs("div", { className: "inline-flex items-center gap-[7px] self-start rounded-[19px] bg-bubble px-[15px] py-3", children: [_jsx("span", { className: "text-[12px] leading-none text-accent animate-sparkle", "aria-hidden": true, children: "\u2726" }), [0, 1, 2].map((i) => (_jsx("span", { className: "h-2 w-2 rounded-full bg-muted animate-bounce2", style: { animationDelay: `${i * 0.16}s` } }, i))), label ? _jsx("span", { className: "ml-0.5 font-mono text-[10px] text-muted", children: label }) : null] }));
}
/** Indeterminate pulsing progress bar shown while an agent works. */
export function ThinkingBar() {
    return (_jsxs("div", { className: "absolute inset-x-0 -bottom-px z-[7] h-[3px] overflow-hidden animate-tbpulse", "aria-hidden": true, children: [_jsx("div", { className: "absolute inset-0 bg-accent opacity-[0.14]" }), _jsx("span", { className: "tb-sweep" })] }));
}
/** Reveal text word-by-word with a blinking caret. */
export function Streamer({ text, speed = 24, onTick, onDone, }) {
    const parts = useRef([]);
    const [n, setN] = useState(0);
    const onTickRef = useRef(onTick);
    const onDoneRef = useRef(onDone);
    onTickRef.current = onTick;
    onDoneRef.current = onDone;
    useEffect(() => {
        parts.current = String(text).split(/(\s+)/);
        setN(0);
        let i = 0;
        const id = setInterval(() => {
            i += 1;
            setN(i);
            onTickRef.current?.();
            if (i >= parts.current.length) {
                clearInterval(id);
                onDoneRef.current?.();
            }
        }, speed);
        return () => clearInterval(id);
    }, [text, speed]);
    const done = n >= parts.current.length;
    return (_jsxs("span", { children: [parts.current.slice(0, n).join(""), !done ? _jsx("span", { className: "caret" }) : null] }));
}
