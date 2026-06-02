export type Route = "COACH" | "WORKOUT_GENERATE" | "WORKOUT_LOG" | "CLARIFY";

export interface WorkoutItem {
  name: string;
  sets: number;
  reps: number;
  rest_seconds: number;
}

export interface Workout {
  warmup: WorkoutItem[];
  main: WorkoutItem[];
  cooldown: WorkoutItem[];
}

export interface LogEntry {
  exercise: string;
  sets: number;
  reps: number;
  weight?: number | null;
}

export interface ChatResponse {
  route: Route;
  confidence: number;
  reply: string;
  workout?: Workout | null;
  log_entries?: LogEntry[] | null;
}
