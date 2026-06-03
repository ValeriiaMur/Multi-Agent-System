import type { LogEntry, Route, TraceStep, Workout } from "../types";
import { ROUTE_META } from "../lib/agent";
import { RouteBadge } from "./RouteBadge";
import { Trace } from "./Trace";
import { Typing } from "./primitives";
import { Markdown } from "./Markdown";
import { WorkoutCard, RecoveryNote } from "./WorkoutCard";
import { LogCard } from "./LogEntry";
import { ReactionRail } from "./ReactionRail";
import { GenPills } from "./Chips";

export interface AssistantMsg {
  id: string;
  role: "assistant";
  phase: "routing" | "thinking" | "streaming" | "done";
  srcText?: string;
  route?: Route;
  confidence?: number;
  reason?: string | null;
  offline?: boolean;
  trace?: TraceStep[];
  lead?: string;
  kind?: "text" | "workout" | "log";
  workout?: Workout | null;
  entries?: LogEntry[] | null;
  runId?: string | null;
  chips?: string[] | null;
}

export function AssistantTurn({
  msg,
  showInternals,
  cardStyle,
  onRun,
}: {
  msg: AssistantMsg;
  showInternals: boolean;
  cardStyle: string;
  onRun: (text: string) => void;
}) {
  const routed = msg.phase !== "routing" && msg.route;
  const streaming = msg.phase === "streaming";
  const done = msg.phase === "done";
  const showLead = (streaming || done) && msg.lead;
  const workoutEmpty = msg.workout?.meta?.empty;

  return (
    <div className="group/turn flex">
      <div className="flex max-w-[84%] flex-col items-start gap-[7px] animate-rise">
        {showInternals && routed ? (
          <RouteBadge route={msg.route!} confidence={msg.confidence ?? 0} reason={msg.reason} offline={msg.offline} />
        ) : null}
        {showInternals && done && msg.trace?.length ? <Trace steps={msg.trace} /> : null}

        {msg.phase === "routing" ? <Typing label="reading your message" /> : null}
        {msg.phase === "thinking" ? <Typing label={(msg.route && ROUTE_META[msg.route]?.sub) || "working"} /> : null}

        {showLead ? (
          <div className="relative max-w-full break-words rounded-[19px] bg-bubble px-3.5 py-[9px] text-[16px] leading-[1.34] tracking-[-0.2px] text-ink bubble-coach">
            <Markdown>{msg.lead!}</Markdown>
            {streaming ? <span className="caret" /> : null}
          </div>
        ) : null}

        {done ? (
          <>
            {msg.kind === "workout" && msg.workout ? (
              workoutEmpty ? (
                <RecoveryNote meta={msg.workout.meta!} />
              ) : (
                <WorkoutCard workout={msg.workout} cardStyle={cardStyle} />
              )
            ) : null}

            {msg.kind === "log" && msg.entries?.length ? <LogCard entries={msg.entries} /> : null}

            {msg.kind === "text" && msg.route === "COACH" ? (
              <ReactionRail text={msg.lead ?? ""} runId={msg.runId} onRegen={() => msg.srcText && onRun(msg.srcText)} />
            ) : null}

            {msg.kind === "workout" && msg.workout && !workoutEmpty ? (
              <GenPills items={["Make this harder", "Build a 45-min version"]} onPick={onRun} />
            ) : null}
            {msg.kind === "log" && msg.entries?.length ? (
              <GenPills items={["What should I train next?"]} onPick={onRun} />
            ) : null}
          </>
        ) : null}
      </div>
    </div>
  );
}
