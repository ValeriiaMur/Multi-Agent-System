import { useState } from "react";
import { sendChat } from "./api";
import type { ChatResponse } from "./types";
import { RouteBadge } from "./components/RouteBadge";
import { WorkoutCard } from "./components/WorkoutCard";
import { LogEntryChip } from "./components/LogEntry";

interface Turn {
  user: string;
  resp?: ChatResponse;
}

// Minimal chat shell wired to the components. Behavior is filled in Phase 6.
export default function App() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");

  async function submit() {
    const text = input.trim();
    if (!text) return;
    setInput("");
    const resp = await sendChat(text);
    setTurns((t) => [...t, { user: text, resp }]);
  }

  return (
    <main style={{ maxWidth: 640, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>Fitness Coach</h1>
      <div>
        {turns.map((t, i) => (
          <div key={i}>
            <p><strong>You:</strong> {t.user}</p>
            {t.resp && (
              <div>
                <RouteBadge route={t.resp.route} confidence={t.resp.confidence} />
                <p>{t.resp.reply}</p>
                {t.resp.workout && <WorkoutCard workout={t.resp.workout} />}
                {t.resp.log_entries?.map((e, j) => <LogEntryChip key={j} entry={e} />)}
              </div>
            )}
          </div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} aria-label="message" />
      <button onClick={submit}>Send</button>
    </main>
  );
}
