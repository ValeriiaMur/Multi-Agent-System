import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useViewport, PHONE_SIZE } from "../hooks/useViewport";
import { StatusBar } from "./Chrome";
/** Framed iPhone on desktop/tablet (white studio surface); full-bleed on phones. */
export function PhoneFrame({ children }) {
    const { framed, scale } = useViewport();
    if (!framed) {
        return (_jsx("div", { className: "h-full w-full", children: _jsx("div", { className: "h-[100dvh] w-screen bg-black", children: _jsxs("div", { className: "relative flex h-full w-full flex-col overflow-hidden bg-bg", children: [_jsx(StatusBar, {}), children, _jsx(HomeIndicator, {})] }) }) }));
    }
    return (_jsx("div", { className: "flex h-full w-full items-center justify-center bg-[radial-gradient(135%_115%_at_50%_0%,#ffffff_0%,#ededf0_62%,#e1e1e5_100%)] p-3.5", children: _jsx("div", { className: "shrink-0 rounded-[56px] bg-[#0a0a0b] p-[5px] shadow-[inset_0_0_0_5px_#050506,0_0_0_11px_#1c1c20,0_0_0_12px_#3a3a40,0_50px_110px_rgba(0,0,0,0.6),0_12px_30px_rgba(0,0,0,0.4)]", style: { width: PHONE_SIZE.width, height: PHONE_SIZE.height, transform: `scale(${scale})`, transformOrigin: "center" }, children: _jsxs("div", { className: "relative flex h-full w-full flex-col overflow-hidden rounded-[51px] bg-bg", children: [_jsx(StatusBar, {}), _jsx("span", { className: "absolute left-1/2 top-[9px] z-[70] h-[26px] w-[92px] -translate-x-1/2 rounded-2xl bg-black" }), children, _jsx(HomeIndicator, {})] }) }) }));
}
function HomeIndicator() {
    return (_jsx("div", { className: "pointer-events-none absolute inset-x-0 bottom-[7px] z-[80] flex justify-center", children: _jsx("span", { className: "h-[5px] w-[140px] rounded-full bg-[var(--home-ind)]" }) }));
}
