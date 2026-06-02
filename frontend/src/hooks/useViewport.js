import { useEffect, useState } from "react";
const PHONE_W = 390;
const PHONE_H = 844;
/** Framed iPhone on desktop/tablet, full-bleed on phones — scaled to fit. */
function measure() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const framed = w >= 600 && h >= 560;
    const scale = framed ? Math.min(1, (h - 28) / PHONE_H, (w - 28) / PHONE_W) : 1;
    return { framed, scale };
}
export function useViewport() {
    const [vp, setVp] = useState(measure);
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
