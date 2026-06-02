import { useEffect, useState } from "react";

const PHONE_W = 390;
const PHONE_H = 844;

export interface Viewport {
  framed: boolean;
  scale: number;
}

/** Tablet/desktop threshold: frame only when the SMALLER viewport dimension is
 *  at least this big. Phones (min side ~390, even in landscape) stay full-bleed;
 *  iPads (min side 768) and desktops get the framed mockup. */
const FRAME_MIN_SIDE = 600;

/** Pure viewport decision — framed iPhone on desktop/tablet, full-bleed on
 *  phones, scaled to fit. Kept pure (no window access) so it's unit-testable. */
export function computeViewport(w: number, h: number): Viewport {
  const framed = Math.min(w, h) >= FRAME_MIN_SIDE;
  const scale = framed ? Math.min(1, (h - 28) / PHONE_H, (w - 28) / PHONE_W) : 1;
  return { framed, scale };
}

function measure(): Viewport {
  return computeViewport(window.innerWidth, window.innerHeight);
}

export function useViewport(): Viewport {
  const [vp, setVp] = useState<Viewport>(measure);
  useEffect(() => {
    let raf = 0;
    const onResize = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => setVp(measure()));
    };
    window.addEventListener("resize", onResize);
    window.addEventListener("orientationchange", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("orientationchange", onResize);
    };
  }, []);
  return vp;
}

export const PHONE_SIZE = { width: PHONE_W, height: PHONE_H };
