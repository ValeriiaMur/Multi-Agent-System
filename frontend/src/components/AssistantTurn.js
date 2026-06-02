import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { ROUTE_META } from "../lib/agent";
import { RouteBadge } from "./RouteBadge";
import { Trace } from "./Trace";
import { Typing, Streamer } from "./primitives";
import { WorkoutCard, RecoveryNote } from "./WorkoutCard";
import { LogCard } from "./LogEntry";
import { ReactionRail } from "./ReactionRail";
import { GenPills } from "./Chips";
export function AssistantTurn({ msg, speed, showInternals, cardStyle, onChipsReady, onTick, onRun, }) {
    const routed = msg.phase !== "routing" && msg.route;
    const done = msg.phase === "done";
    const workoutEmpty = msg.workout?.meta?.empty;
    return (_jsx("div", { className: "group/turn flex", children: _jsxs("div", { className: "flex max-w-[84%] flex-col items-start gap-[7px] animate-rise", children: [showInternals && routed ? (_jsx(RouteBadge, { route: msg.route, confidence: msg.confidence ?? 0, reason: msg.reason, offline: msg.offline })) : null, showInternals && done && msg.trace?.length ? _jsx(Trace, { steps: msg.trace }) : null, msg.phase === "routing" ? _jsx(Typing, { label: "reading your message" }) : null, msg.phase === "thinking" ? _jsx(Typing, { label: (msg.route && ROUTE_META[msg.route]?.sub) || "working" }) : null, done ? (_jsxs(_Fragment, { children: [msg.lead ? (_jsx("div", { className: "relative max-w-full break-words rounded-[19px] bg-bubble px-3.5 py-[9px] text-[16px] leading-[1.34] tracking-[-0.2px] text-ink bubble-coach", children: msg.streamed ? (msg.lead) : (_jsx(Streamer, { text: msg.lead, speed: speed, onTick: onTick, onDone: () => onChipsReady(msg.id) })) })) : null, msg.kind === "workout" && msg.workout ? (workoutEmpty ? (_jsx(RecoveryNote, { meta: msg.workout.meta })) : (_jsx(WorkoutCard, { workout: msg.workout, cardStyle: cardStyle }))) : null, msg.kind === "log" && msg.entries?.length ? _jsx(LogCard, { entries: msg.entries }) : null, msg.kind === "text" && msg.route === "COACH" ? (_jsx(ReactionRail, { text: msg.lead ?? "", runId: msg.runId, onRegen: () => msg.srcText && onRun(msg.srcText) })) : null, msg.kind === "workout" && msg.workout && !workoutEmpty ? (_jsx(GenPills, { items: ["Make this harder", "Build a 45-min version"], onPick: onRun })) : null, msg.kind === "log" && msg.entries?.length ? (_jsx(GenPills, { items: ["What should I train next?"], onPick: onRun })) : null] })) : null] }) }));
}
