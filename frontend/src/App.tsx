import { useCallback, useEffect, useRef, useState } from "react";
import { sendChat } from "./api";
import { deriveLead, deriveTrace, clarifyChips, STARTERS } from "./lib/agent";
import { PhoneFrame } from "./components/PhoneFrame";
import { Header, TabBar, type AgentState } from "./components/Chrome";
import { Composer } from "./components/Composer";
import { Chips } from "./components/Chips";
import { AssistantTurn, type AssistantMsg } from "./components/AssistantTurn";

interface UserMsg {
  id: string;
  role: "user";
  text: string;
}
type Message = UserMsg | AssistantMsg;

let _seq = 0;
const uid = () => `m${++_seq}`;

const STREAM_SPEED = 22;
const CARD_STYLE = "tinted";

const WELCOME: AssistantMsg = {
  id: uid(),
  role: "assistant",
  phase: "done",
  kind: "text",
  streamed: true,
  lead: "Hey — I'm your Future coach. Ask me about an exercise, tell me to build a session, or log a set you just hit.",
  chips: STARTERS,
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [busy, setBusy] = useState(false);
  const [agent, setAgent] = useState<AgentState>({ busy: false, phase: null, route: null });
  const [readyChips, setReadyChips] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);
  const threadId = useRef(`t${Math.round(performance.now())}`);

  const scrollToEnd = useCallback(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight + 800;
  }, []);
  useEffect(() => {
    scrollToEnd();
  }, [messages, scrollToEnd]);

  const patch = useCallback((id: string, fields: Partial<AssistantMsg>) => {
    setMessages((ms) => ms.map((m) => (m.id === id ? ({ ...m, ...fields } as Message) : m)));
  }, []);

  const markChips = useCallback((id: string) => setReadyChips((r) => ({ ...r, [id]: true })), []);

  const run = useCallback(
    async (text: string) => {
      const clean = text.trim();
      if (!clean || busy) return;
      setBusy(true);

      // clear any open quick-reply chips
      setMessages((ms) => ms.map((m) => (m.role === "assistant" && m.chips ? { ...m, chips: null } : m)));

      const aId = uid();
      setMessages((ms) => [
        ...ms,
        { id: uid(), role: "user", text: clean },
        { id: aId, role: "assistant", phase: "routing", srcText: clean },
      ]);
      setAgent({ busy: true, phase: "routing", route: null });

      try {
        const resp = await sendChat(clean, threadId.current);

        // surface the routing decision, then the sub-agent "thinking" beat
        patch(aId, {
          phase: "thinking",
          route: resp.route,
          confidence: resp.confidence,
          reason: resp.reason,
        });
        setAgent({ busy: true, phase: "thinking", route: resp.route });
        await new Promise((r) => setTimeout(r, 380));

        const trace = deriveTrace(resp);
        const lead = deriveLead(resp);

        if (resp.route === "WORKOUT_GENERATE") {
          patch(aId, { phase: "done", kind: "workout", lead, workout: resp.workout, trace, runId: resp.run_id });
        } else if (resp.route === "WORKOUT_LOG") {
          const entries = resp.log_entries ?? [];
          patch(aId, {
            phase: "done",
            kind: entries.length ? "log" : "text",
            lead,
            entries,
            trace,
            runId: resp.run_id,
          });
        } else if (resp.route === "CLARIFY") {
          patch(aId, { phase: "done", kind: "text", lead, chips: clarifyChips(clean), trace, runId: resp.run_id });
        } else {
          patch(aId, { phase: "done", kind: "text", lead, trace, runId: resp.run_id });
        }
      } catch {
        patch(aId, {
          phase: "done",
          kind: "text",
          lead: "Something went sideways on my end — mind trying that again?",
        });
      } finally {
        setBusy(false);
        setAgent({ busy: false, phase: null, route: null });
      }
    },
    [busy, patch],
  );

  return (
    <PhoneFrame>
      <div className="theme-dark flex min-h-0 flex-1 flex-col bg-bg font-sans text-[16px] text-ink">
        <Header state={agent} />

        <div ref={scrollRef} className="no-scrollbar min-h-0 flex-1 overflow-y-auto overflow-x-hidden bg-bg">
          <div className="flex flex-col gap-[9px] px-4 pb-3 pt-3.5">
            {messages.map((m) =>
              m.role === "user" ? (
                <div key={m.id} className="flex justify-end">
                  <div className="relative max-w-[80%] break-words rounded-[19px] bg-blue px-3.5 py-[9px] text-[16px] leading-[1.34] tracking-[-0.2px] text-white bubble-user">
                    {m.text}
                  </div>
                </div>
              ) : (
                <div key={m.id}>
                  <AssistantTurn
                    msg={m}
                    speed={STREAM_SPEED}
                    showInternals
                    cardStyle={CARD_STYLE}
                    onChipsReady={markChips}
                    onTick={scrollToEnd}
                    onRun={run}
                  />
                  {m.chips && (m.streamed || readyChips[m.id]) ? (
                    <div className="mt-[3px]">
                      <Chips items={m.chips} onPick={run} />
                    </div>
                  ) : null}
                </div>
              ),
            )}
          </div>
        </div>

        <Composer disabled={busy} onSend={run} />
        <div className="shrink-0 border-t border-line-soft bg-tabbar-bg px-[18px] py-[7px] text-center text-[10.5px] text-muted [backdrop-filter:blur(22px)_saturate(170%)]">
          Future Coach can make mistakes — verify important details.
        </div>
        <TabBar />
      </div>
    </PhoneFrame>
  );
}
