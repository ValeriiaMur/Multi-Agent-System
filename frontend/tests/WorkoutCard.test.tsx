import { render, screen } from "@testing-library/react";
import { WorkoutCard } from "../src/components/WorkoutCard";
import type { Workout } from "../src/types";

const item = (name: string, prescription: string) => ({
  exercise_id: name.toLowerCase().replace(/\s+/g, "-"),
  name,
  sets: 3,
  reps: 10,
  rest_seconds: 90,
  rest: 90,
  prescription,
  muscle_groups: ["chest"],
  is_bilateral: false,
});

const workout: Workout = {
  duration_minutes: 30,
  warmup: [item("Arm Circles", "0:45")],
  main: [item("Barbell Flat Bench Press", "3 × 10")],
  cooldown: [item("Chest Stretch", "0:30 hold")],
  meta: {
    duration_min: 30,
    goal: "strength",
    muscle_groups: ["chest"],
    equipment: ["Barbell"],
    avoid_joints: [],
    empty: false,
  },
};

it("renders main-block exercise with prescription", () => {
  render(<WorkoutCard workout={workout} />);
  expect(screen.getByText(/Barbell Flat Bench Press/)).toBeInTheDocument();
  expect(screen.getByText(/3 × 10/)).toBeInTheDocument();
});
