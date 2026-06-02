import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen } from "@testing-library/react";
import { LogCard } from "../src/components/LogEntry";
it("renders parsed log entries with weight", () => {
    render(_jsx(LogCard, { entries: [
            {
                exercise: "Barbell Flat Bench Press",
                exercise_id: "bench",
                matched: true,
                sets: 3,
                reps: 10,
                weight: 185,
            },
        ] }));
    expect(screen.getByText(/Barbell Flat Bench Press/)).toBeInTheDocument();
    expect(screen.getByText(/185/)).toBeInTheDocument();
});
