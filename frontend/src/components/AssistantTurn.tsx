import type { LogEntry, Route, TraceStep, Workout } from "../types";
import { ROUTE_META } from "../lib/agent";
import { RouteBadge } from "./RouteBadge";
import { Trace } from "./Trace";
import { Typing, Streamer } from "./primitives";
import { Markdown } from "./Markdown";
import { WorkoutCard, RecoveryNote } from "./WorkoutCard";
import { LogCard } from "./LogEntry";
import { ReactionRail } from "./ReactionRail";
import { GenPills } from "./Chips";

export interface AssistantMsg {
  id: string;
  role: "assistant";
  phase: "routing" | "thinking" | "done";
  srcText?: string;
  route?: Route;
  confidence?: number;
  reason?: string | null;
  offline?: boolean;
  trace?: TraceStep[];
  lead?: string;
  streamed?: boolean;
  kind?: "text" | "workout" | "log";
  workout?: Workout | null;
  entries?: LogEntry[] | null;
  runId?: string | null;
  chips?: string[] | null;
}

export function AssistantTurn({
  msg,
  speed,
  showInternals,
  cardStyle,
  onChipsReady,
  onTick,
  onRun,
}: {
  msg: AssistantMsg;
  speed: number;
  showInternals: boolean;
  cardStyle: string;
  onChipsReady: (id: string) => void;
  onTick: () => void;
  onRun: (text: string) => void;
}) {
  const routed = msg.phase !== "routing" && msg.route;
  const done = msg.phase === "done";
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

        {done ? (
          <>
            {msg.lead ? (
              <div className="relative max-w-full break-words rounded-[19px] bg-bubble px-3.5 py-[9px] text-[16px] leading-[1.34] tracking-[-0.2px] text-ink bubble-coach">
                {msg.streamed ? (
                  <Markdown>{msg.lead}</Markdown>
                ) : (
                  <Streamer text={msg.lead} speed={speed} markdown onTick={onTick} onDone={() => onChipsReady(msg.id)} />
                )}
              </div>
            ) : null}

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
