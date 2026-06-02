import type { Workout, WorkoutItem } from "../types";

function Block({ title, items }: { title: string; items: WorkoutItem[] }) {
  if (!items.length) return null;
  return (
    <div style={{ marginBottom: 8 }}>
      <h4 style={{ margin: "4px 0", textTransform: "capitalize" }}>{title}</h4>
      <ul style={{ margin: 0, paddingLeft: 18 }}>
        {items.map((it, i) => (
          <li key={i}>
            {it.name} — {it.sets}x{it.reps}, rest {it.rest_seconds}s
          </li>
        ))}
      </ul>
    </div>
  );
}

export function WorkoutCard({ workout }: { workout: Workout }) {
  return (
    <div
      data-testid="workout-card"
      style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 12, margin: "8px 0" }}
    >
      <Block title="warmup" items={workout.warmup} />
      <Block title="main" items={workout.main} />
      <Block title="cooldown" items={workout.cooldown} />
    </div>
  );
}
