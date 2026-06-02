import { render, screen } from "@testing-library/react";
import { LogEntryChip } from "../src/components/LogEntry";

// RED until Phase 6.
it("renders parsed log entry", () => {
  render(<LogEntryChip entry={{ exercise: "Barbell Flat Bench Press", sets: 3, reps: 10, weight: 185 }} />);
  expect(screen.getByText(/Barbell Flat Bench Press/)).toBeInTheDocument();
  expect(screen.getByText(/185/)).toBeInTheDocument();
});
