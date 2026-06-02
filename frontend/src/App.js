import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCallback, useEffect, useRef, useState } from "react";
import { sendChat } from "./api";
import { deriveLead, deriveTrace, clarifyChips, STARTERS } from "./lib/agent";
import { PhoneFrame } from "./components/PhoneFrame";
import { Header, TabBar } from "./components/Chrome";
import { Composer } from "./components/Composer";
import { Chips } from "./components/Chips";
import { AssistantTurn } from "./components/AssistantTurn";
let _seq = 0;
const uid = () => `m${++_seq}`;
const STREAM_SPEED = 22;
const CARD_STYLE = "tinted";
const WELCOME = {
    id: uid(),
    role: "assistant",
    phase: "done",
    kind: "text",
    streamed: true,
    lead: "Hey — I'm your Future coach. Ask me about an exercise, tell me to build a session, or log a set you just hit.",
    chips: STARTERS,
};
export default function App() {
    const [messages, setMessages] = useState([WELCOME]);
    const [busy, setBusy] = useState(false);
    const [agent, setAgent] = useState({ busy: false, phase: null, route: null });
    const [readyChips, setReadyChips] = useState({});
    const scrollRef = useRef(null);
    const threadId = useRef(`t${Math.round(performance.now())}`);
    const scrollToEnd = useCallback(() => {
        const el = scrollRef.current;
        if (el)
            el.scrollTop = el.scrollHeight + 800;
    }, []);
    useEffect(() => {
        scrollToEnd();
    }, [messages, scrollToEnd]);
    const patch = useCallback((id, fields) => {
        setMessages((ms) => ms.map((m) => (m.id === id ? { ...m, ...fields } : m)));
    }, []);
    const markChips = useCallback((id) => setReadyChips((r) => ({ ...r, [id]: true })), []);
    const run = useCallback(async (text) => {
        const clean = text.trim();
        if (!clean || busy)
            return;
        setBusy(true);
        // clear any open quick-reply chips
        setMessages((ms) => ms.map((m) => (m.role === "assistant" && m.chips ? { ...m, chips: null } : m)));
        const aId = uid();
        setMessages((ms) => [
            ...ms,
            { id: uid(), role: "user", text: clean },
            { id: aId, role: "assistant", phase: "routing", srcText: clean },
        ]);
        setAgent({ busy: true, phase: "routing", route: null });
        try {
            const resp = await sendChat(clean, threadId.current);
            // surface the routing decision, then the sub-agent "thinking" beat
            patch(aId, {
                phase: "thinking",
                route: resp.route,
                confidence: resp.confidence,
                reason: resp.reason,
            });
            setAgent({ busy: true, phase: "thinking", route: resp.route });
            await new Promise((r) => setTimeout(r, 380));
            const trace = deriveTrace(resp);
            const lead = deriveLead(resp);
            if (resp.route === "WORKOUT_GENERATE") {
                patch(aId, { phase: "done", kind: "workout", lead, workout: resp.workout, trace, runId: resp.run_id });
            }
            else if (resp.route === "WORKOUT_LOG") {
                const entries = resp.log_entries ?? [];
                patch(aId, {
                    phase: "done",
                    kind: entries.length ? "log" : "text",
                    lead,
                    entries,
                    trace,
                    runId: resp.run_id,
                });
            }
            else if (resp.route === "CLARIFY") {
                patch(aId, { phase: "done", kind: "text", lead, chips: clarifyChips(clean), trace, runId: resp.run_id });
            }
            else {
                patch(aId, { phase: "done", kind: "text", lead, trace, runId: resp.run_id });
            }
        }
        catch {
            patch(aId, {
                phase: "done",
                kind: "text",
                lead: "Something went sideways on my end — mind trying that again?",
            });
        }
        finally {
            setBusy(false);
            setAgent({ busy: false, phase: null, route: null });
        }
    }, [busy, patch]);
    return (_jsx(PhoneFrame, { children: _jsxs("div", { className: "theme-dark flex min-h-0 flex-1 flex-col bg-bg font-sans text-[16px] text-ink", children: [_jsx(Header, { state: agent }), _jsx("div", { ref: scrollRef, className: "no-scrollbar min-h-0 flex-1 overflow-y-auto overflow-x-hidden bg-bg", children: _jsx("div", { className: "flex flex-col gap-[9px] px-4 pb-3 pt-3.5", children: messages.map((m) => m.role === "user" ? (_jsx("div", { className: "flex justify-end", children: _jsx("div", { className: "relative max-w-[80%] break-words rounded-[19px] bg-blue px-3.5 py-[9px] text-[16px] leading-[1.34] tracking-[-0.2px] text-white bubble-user", children: m.text }) }, m.id)) : (_jsxs("div", { children: [_jsx(AssistantTurn, { msg: m, speed: STREAM_SPEED, showInternals: true, cardStyle: CARD_STYLE, onChipsReady: markChips, onTick: scrollToEnd, onRun: run }), m.chips && (m.streamed || readyChips[m.id]) ? (_jsx("div", { className: "mt-[3px]", children: _jsx(Chips, { items: m.chips, onPick: run }) })) : null] }, m.id))) }) }), _jsx(Composer, { disabled: busy, onSend: run }), _jsx("div", { className: "shrink-0 border-t border-line-soft bg-tabbar-bg px-[18px] py-[7px] text-center text-[10.5px] text-muted [backdrop-filter:blur(22px)_saturate(170%)]", children: "Future Coach can make mistakes \u2014 verify important details." }), _jsx(TabBar, {})] }) }));
}
