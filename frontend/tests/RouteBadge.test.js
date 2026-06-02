import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen } from "@testing-library/react";
import { RouteBadge } from "../src/components/RouteBadge";
// RED until Phase 6: stub renders null.
it("shows the route and confidence percentage", () => {
    render(_jsx(RouteBadge, { route: "COACH", confidence: 0.91 }));
    expect(screen.getByText(/COACH/i)).toBeInTheDocument();
    expect(screen.getByText(/91%/)).toBeInTheDocument();
});
