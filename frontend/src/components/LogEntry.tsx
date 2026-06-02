import type { LogEntry as Entry } from "../types";

export function LogEntryChip({ entry }: { entry: Entry }) {
  const weight = entry.weight != null ? ` @ ${entry.weight} lbs` : "";
  return (
    <span
      data-testid="log-entry"
      style={{
        display: "inline-block",
        background: "#f3e8ff",
        color: "#6b21a8",
        borderRadius: 8,
        padding: "2px 8px",
        margin: "2px 4px 2px 0",
        fontSize: 13,
      }}
    >
      {entry.exercise}: {entry.sets}x{entry.reps}
      {weight}
    </span>
  );
}
