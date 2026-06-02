import { ROUTE_META } from "../lib/agent";
import type { Route } from "../types";
import { ThinkingBar } from "./primitives";
import { BackIcon, MediaIcon } from "./icons";

const blur = "backdrop-blur-[22px] [backdrop-filter:blur(22px)_saturate(170%)]";

/** iOS status bar — purely cosmetic (hardcoded 9:41). */
export function StatusBar() {
  return (
    <div className="relative z-[8] flex items-center justify-between px-7 pb-[7px] pt-3.5 text-ink">
      <span className="text-[15px] font-semibold tracking-[0.2px]">9:41</span>
      <span className="flex items-center gap-1.5">
        <svg width="18" height="11" viewBox="0 0 18 11">
          <rect x="0" y="6.5" width="3" height="4.5" rx="0.6" fill="currentColor" />
          <rect x="4.5" y="4.5" width="3" height="6.5" rx="0.6" fill="currentColor" />
          <rect x="9" y="2.3" width="3" height="8.7" rx="0.6" fill="currentColor" />
          <rect x="13.5" y="0" width="3" height="11" rx="0.6" fill="currentColor" />
        </svg>
        <svg width="25" height="12" viewBox="0 0 25 12">
          <rect x="0.5" y="0.5" width="21" height="11" rx="3" stroke="currentColor" strokeOpacity="0.4" fill="none" />
          <rect x="2" y="2" width="18" height="8" rx="1.6" fill="currentColor" />
          <path d="M23 4v4c.8-.3 1.3-1 1.3-2S23.8 4.3 23 4z" fill="currentColor" fillOpacity="0.5" />
        </svg>
      </span>
    </div>
  );
}

export function Avatar({ size = 38 }: { size?: number }) {
  return (
    <div
      className="coach-av flex shrink-0 items-center justify-center rounded-full font-extrabold tracking-[-0.5px] text-white"
      style={{ width: size, height: size, fontSize: size * 0.42 }}
      aria-hidden
    >
      <span className="relative z-[1]">F</span>
    </div>
  );
}

/** Ambient last-session sparkline — decorative, hardcoded. */
function Sparkline() {
  const pts = "0,26 12,22 24,27 36,15 48,19 60,8 72,13 84,6 96,11 108,4";
  return (
    <svg className="h-[34px] min-w-0 flex-1" viewBox="0 0 108 32" preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <polyline points={`0,32 ${pts} 108,32`} fill="var(--accent)" fillOpacity="0.12" stroke="none" />
    </svg>
  );
}

export interface AgentState {
  busy: boolean;
  phase: "routing" | "thinking" | null;
  route: Route | null;
}

/** Chat header reflecting live agent state. Session stats are hardcoded. */
export function Header({ state }: { state: AgentState }) {
  const meta = state.route ? ROUTE_META[state.route] : null;
  const status = state.busy
    ? state.phase === "routing"
      ? "routing…"
      : `${(meta?.sub ?? "thinking").toLowerCase()}…`
    : "active now";

  return (
    <div className={`relative z-[6] shrink-0 border-b border-line-soft bg-header-bg ${blur}`}>
      <div className="relative flex min-h-[74px] items-start justify-between px-3.5 pb-0.5 pt-1.5">
        <button className="flex h-[34px] w-[34px] items-center justify-center rounded-full bg-surface text-ink2" aria-label="Back">
          <BackIcon />
        </button>
        <div className="absolute left-1/2 top-1 flex -translate-x-1/2 flex-col items-center gap-[3px]">
          <div className="relative">
            <Avatar size={42} />
            <span
              className={`absolute -bottom-px -right-px h-[11px] w-[11px] rounded-full border-[2.5px] border-bg ${
                state.busy ? "bg-accent animate-pulse2" : "bg-good"
              }`}
            />
          </div>
          <div className="text-[12.5px] font-semibold tracking-[-0.1px] text-ink">Future Coach</div>
          <div className={`text-[10.5px] ${state.busy ? "text-accent" : "text-muted"}`}>
            {state.busy ? <span className="mr-[3px] text-[9px] text-accent">✦</span> : null}
            {status}
          </div>
        </div>
        <button className="flex h-[34px] w-[34px] items-center justify-center rounded-full bg-surface text-ink2" aria-label="Media">
          <MediaIcon />
        </button>
      </div>
      {state.busy ? <ThinkingBar /> : null}
      <div className="flex items-center gap-3 px-[22px] pb-3">
        <div className="flex shrink-0 flex-col">
          <div className="text-[22px] font-bold leading-none tabular-nums tracking-[-0.6px] text-ink">172</div>
          <div className="mt-[3px] text-[10px] text-muted">Est. Calorie Burn</div>
        </div>
        <Sparkline />
        <div className="flex shrink-0 flex-col items-end text-right">
          <div className="text-[22px] font-bold leading-none tabular-nums tracking-[-0.6px] text-ink">53:03</div>
          <div className="mt-[3px] text-[10px] text-muted">Minutes</div>
        </div>
      </div>
    </div>
  );
}

/** Bottom tab bar — hardcoded, Messages tab active. */
export function TabBar() {
  const items = [
    {
      key: "home",
      label: "Home",
      icon: (
        <path d="M4 11l8-6 8 6v8a1 1 0 01-1 1h-4v-6h-6v6H5a1 1 0 01-1-1v-8z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      ),
    },
    {
      key: "progress",
      label: "Progress",
      icon: (
        <>
          <rect x="4" y="12" width="3.4" height="8" rx="1" fill="currentColor" />
          <rect x="10.3" y="7" width="3.4" height="13" rx="1" fill="currentColor" />
          <rect x="16.6" y="3.5" width="3.4" height="16.5" rx="1" fill="currentColor" />
        </>
      ),
    },
    { key: "messages", label: "Messages", avatar: true },
    {
      key: "friends",
      label: "Friends",
      icon: (
        <>
          <circle cx="9" cy="8" r="3.2" stroke="currentColor" strokeWidth="1.7" />
          <circle cx="17" cy="9" r="2.6" stroke="currentColor" strokeWidth="1.7" />
          <path d="M3 19c0-3 2.7-5 6-5s6 2 6 5M16 19c0-2.3.7-3.6 2-4.3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
        </>
      ),
    },
    {
      key: "profile",
      label: "Profile",
      icon: (
        <>
          <circle cx="12" cy="8" r="3.6" stroke="currentColor" strokeWidth="1.7" />
          <path d="M4.5 20c0-3.6 3.4-6 7.5-6s7.5 2.4 7.5 6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
        </>
      ),
    },
  ];
  return (
    <div className={`flex shrink-0 items-center justify-around border-t border-line-soft bg-tabbar-bg px-1 pb-[22px] pt-2 ${blur}`}>
      {items.map((it) => {
        const active = it.key === "messages";
        return (
          <button key={it.key} className={`flex flex-1 flex-col items-center gap-1 ${active ? "text-ink" : "text-muted"}`}>
            {it.avatar ? (
              <span className="rounded-full ring-2 ring-accent">
                <Avatar size={26} />
              </span>
            ) : (
              <span className={active ? "text-accent" : "text-current"}>
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
                  {it.icon}
                </svg>
              </span>
            )}
            <span className="text-[10px] tracking-[0.1px]">{it.label}</span>
          </button>
        );
      })}
    </div>
  );
}
