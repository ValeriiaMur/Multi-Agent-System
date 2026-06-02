import type { Workout, WorkoutItem, WorkoutMeta } from "../types";
import { Tag } from "./primitives";

function Section({ title, items }: { title: string; items: WorkoutItem[] }) {
  if (!items.length) return null;
  return (
    <div className="border-b border-line-soft py-[13px] last:border-none">
      <div className="mb-2.5 flex items-center gap-2">
        <span className="font-mono text-[11px] font-bold uppercase tracking-[1.4px] text-ink">{title}</span>
        <span className="inline-flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-chip px-[5px] font-mono text-[10px] text-muted">
          {items.length}
        </span>
      </div>
      <div className="flex flex-col gap-[11px]">
        {items.map((e, i) => (
          <div key={e.exercise_id + i} className="grid grid-cols-[22px_1fr_auto] items-start gap-2.5">
            <span className="pt-0.5 font-mono text-[12px] text-muted">{String(i + 1).padStart(2, "0")}</span>
            <div>
              <div className="text-[15px] font-medium leading-[1.25] text-ink">{e.name}</div>
              <div className="mt-[5px] flex flex-wrap gap-1">
                {e.muscle_groups.slice(0, 3).map((m) => (
                  <Tag key={m}>{m}</Tag>
                ))}
                {e.is_bilateral ? <Tag variant="ink">both sides</Tag> : null}
              </div>
            </div>
            <div className="shrink-0 text-right">
              <div className="whitespace-nowrap text-[14px] font-bold tabular-nums text-ink">{e.prescription}</div>
              {e.rest ? (
                <div className="mt-[3px] font-mono text-[9.5px] text-muted">{e.rest}s rest</div>
              ) : (
                <div className="mt-[3px] font-mono text-[9.5px] text-accent">hold</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function WorkoutCard({ workout, cardStyle = "tinted" }: { workout: Workout; cardStyle?: string }) {
  const { warmup, main, cooldown } = workout;
  const meta: WorkoutMeta = workout.meta ?? {
    duration_min: workout.duration_minutes,
    goal: "strength",
    muscle_groups: [],
    equipment: [],
    avoid_joints: [],
    empty: false,
  };
  const total = warmup.length + main.length + cooldown.length;
  const goalLabel = ({ strength: "Strength", endurance: "Endurance", power: "Power" } as Record<string, string>)[meta.goal] ?? "Session";
  const targets = meta.muscle_groups.length ? [...new Set(meta.muscle_groups)].slice(0, 4) : ["full body"];

  return (
    <div
      data-testid="workout-card"
      data-cardstyle={cardStyle}
      className="wcard-edge relative w-full overflow-hidden rounded-[20px] border border-line bg-surface shadow-[0_14px_40px_rgba(0,0,0,0.35)]"
    >
      <div className="border-b border-line-soft bg-surface-2 px-4 pb-3.5 pt-[15px]">
        <div className="font-mono text-[10px] font-bold tracking-[2px] text-accent">YOUR SESSION</div>
        <div className="my-[5px] mb-2.5 text-[21px] font-bold tracking-[-0.5px] text-ink">
          {goalLabel} · {meta.duration_min} min
        </div>
        <div className="flex flex-wrap gap-[5px]">
          {targets.map((m) => (
            <Tag key={m} variant="ink">
              {m}
            </Tag>
          ))}
        </div>
        <div className="mt-[11px] flex flex-wrap items-center gap-[5px]">
          <span className="mr-0.5 font-mono text-[9px] tracking-[1.4px] text-muted">EQUIPMENT</span>
          {(meta.equipment.length ? meta.equipment : ["Any"]).slice(0, 5).map((e) => (
            <span key={e} className="rounded-full border border-line px-[9px] py-0.5 text-[11px] text-ink2">
              {e}
            </span>
          ))}
        </div>
        {meta.avoid_joints.length ? (
          <div className="mt-2.5 text-[11.5px] text-amber">Avoiding load on {meta.avoid_joints.join(", ")}</div>
        ) : null}
      </div>

      <div className="px-4 pb-2 pt-1">
        <Section title="Warm-up" items={warmup} />
        <Section title="Main set" items={main} />
        <Section title="Cool-down" items={cooldown} />
      </div>

      <div className="flex items-center gap-[9px] border-t border-line-soft bg-surface-2 px-4 py-[13px] font-mono text-[11px] text-muted">
        <span>{total} exercises</span>
        <span className="h-[3px] w-[3px] rounded-full bg-muted" />
        <span>~{meta.duration_min} min</span>
        <button className="ml-auto rounded-full bg-accent px-4 py-2 text-[13px] font-semibold text-white transition hover:-translate-y-px hover:brightness-110">
          Start session
        </button>
      </div>
    </div>
  );
}

/** Shown when the generator finds no matching exercises (never invents any). */
export function RecoveryNote({ meta }: { meta: WorkoutMeta }) {
  return (
    <div className="w-full rounded-[20px] border border-accent-22 bg-accent-14 px-[15px] py-3.5">
      <div className="mb-1 text-[14px] font-bold text-accent">No exact matches in the library</div>
      <div className="text-[14px] leading-[1.45] text-ink2">
        I couldn’t find exercises that fit{" "}
        {meta.equipment.length ? <b>{meta.equipment.join(", ")}</b> : "those constraints"}
        {meta.muscle_groups.length ? (
          <>
            {" "}
            for <b>{[...new Set(meta.muscle_groups)].slice(0, 3).join(", ")}</b>
          </>
        ) : null}
        . I won’t invent any. Try loosening the equipment or target.
      </div>
    </div>
  );
}
