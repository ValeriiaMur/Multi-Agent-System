export type Route = "COACH" | "WORKOUT_GENERATE" | "WORKOUT_LOG" | "CLARIFY";

/** A single prescribed exercise in a generated workout (enriched server-side
 *  from the real exercise catalog — never invented). */
export interface WorkoutItem {
  exercise_id: string;
  name: string;
  sets: number;
  reps: number;
  rest_seconds: number;
  /** "3 × 10", "0:45", "0:30 hold" — already formatted by the backend. */
  prescription: string;
  rest: number;
  muscle_groups: string[];
  is_bilateral: boolean;
}

export interface WorkoutMeta {
  duration_min: number;
  goal: string;
  muscle_groups: string[];
  equipment: string[];
  avoid_joints: string[];
  empty: boolean;
}

export interface Workout {
  duration_minutes: number;
  warmup: WorkoutItem[];
  main: WorkoutItem[];
  cooldown: WorkoutItem[];
  meta?: WorkoutMeta;
}

export interface LogEntry {
  exercise: string;
  exercise_id: string | null;
  matched: boolean;
  sets: number;
  reps: number;
  weight?: number | null;
}

export interface ChatResponse {
  route: Route;
  confidence: number;
  reason?: string | null;
  reply: string;
  workout?: Workout | null;
  log_entries?: LogEntry[] | null;
  /** LangSmith run id; thumbs up/down feedback attaches to it. */
  run_id?: string | null;
}

/** One line in the agent observability trace. */
export interface TraceStep {
  tool: string;
  arg?: string;
  res?: string;
}
