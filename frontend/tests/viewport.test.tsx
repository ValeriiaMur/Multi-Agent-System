import { computeViewport } from "../src/hooks/useViewport";

// Phones — never framed, in either orientation.
it("phone portrait is full-bleed", () => {
  expect(computeViewport(390, 844).framed).toBe(false);
});
it("phone landscape is full-bleed", () => {
  expect(computeViewport(844, 390).framed).toBe(false);
});
it("large phone (Pro Max) is full-bleed", () => {
  expect(computeViewport(430, 932).framed).toBe(false);
});

// iPad — framed in both orientations.
it("iPad portrait is framed", () => {
  expect(computeViewport(768, 1024).framed).toBe(true);
});
it("iPad landscape is framed", () => {
  expect(computeViewport(1024, 768).framed).toBe(true);
});

// Desktop — framed; a narrow desktop window falls back to full-bleed.
it("desktop is framed", () => {
  expect(computeViewport(1440, 900).framed).toBe(true);
});
it("narrow desktop window is full-bleed", () => {
  expect(computeViewport(500, 800).framed).toBe(false);
});

it("framed viewport never scales above 1", () => {
  expect(computeViewport(1440, 900).scale).toBeLessThanOrEqual(1);
});
