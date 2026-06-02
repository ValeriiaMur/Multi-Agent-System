import { render, screen } from "@testing-library/react";
import { WorkoutCard } from "../src/components/WorkoutCard";
import type { Workout } from "../src/types";

const workout: Workout = {
  warmup: [{ name: "Arm Circles", sets: 1, reps: 15, rest_seconds: 30 }],
  main: [{ name: "Barbell Flat Bench Press", sets: 3, reps: 10, rest_seconds: 90 }],
  cooldown: [{ name: "Chest Stretch", sets: 1, reps: 1, rest_seconds: 0 }],
};

// RED until Phase 6.
it("renders main-block exercise with prescription", () => {
  render(<WorkoutCard workout={workout} />);
  expect(screen.getByText(/Barbell Flat Bench Press/)).toBeInTheDocument();
  expect(screen.getByText(/3x10/)).toBeInTheDocument();
});
