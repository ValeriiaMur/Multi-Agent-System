import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { sendFeedback } from "../api";
import { CopyIcon, CheckIcon, RegenIcon, ThumbUpIcon, ThumbDownIcon } from "./icons";
const railBtn = "flex h-[27px] w-[27px] items-center justify-center rounded-lg border-none bg-transparent text-muted transition-colors hover:bg-chip hover:text-ink";
/** Copy · regenerate · 👍/👎. Thumbs post to /feedback → LangSmith run feedback. */
export function ReactionRail({ text, runId, onRegen, }) {
    const [copied, setCopied] = useState(false);
    const [vote, setVote] = useState(0);
    const [sent, setSent] = useState(false);
    const copy = () => {
        navigator.clipboard?.writeText(text || "").catch(() => { });
        setCopied(true);
        setTimeout(() => setCopied(false), 1200);
    };
    const rate = async (score) => {
        const next = vote === score ? 0 : score;
        setVote(next);
        if (next !== 0 && runId) {
            const ok = await sendFeedback(runId, next === 1 ? 1 : 0);
            if (ok) {
                setSent(true);
                setTimeout(() => setSent(false), 1600);
            }
        }
    };
    return (_jsxs("div", { className: "mt-px flex items-center gap-[3px] opacity-60 transition-opacity group-hover/turn:opacity-100", children: [_jsx("button", { className: railBtn, onClick: copy, title: "Copy", "aria-label": "Copy", children: copied ? _jsx(CheckIcon, {}) : _jsx(CopyIcon, {}) }), _jsx("button", { className: railBtn, onClick: onRegen, title: "Regenerate", "aria-label": "Regenerate", children: _jsx(RegenIcon, {}) }), _jsx("button", { className: `${railBtn} ${vote === 1 ? "!text-accent" : ""}`, onClick: () => rate(1), title: "Good response", "aria-label": "Good response", "aria-pressed": vote === 1, disabled: !runId, children: _jsx(ThumbUpIcon, {}) }), _jsx("button", { className: `${railBtn} ${vote === -1 ? "!text-accent" : ""}`, onClick: () => rate(-1), title: "Bad response", "aria-label": "Bad response", "aria-pressed": vote === -1, disabled: !runId, children: _jsx(ThumbDownIcon, {}) }), sent ? _jsx("span", { className: "ml-1 font-mono text-[9px] text-muted", children: "sent to LangSmith" }) : null] }));
}
