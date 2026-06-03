import type { ChatResponse } from "./types";

// In dev, leave VITE_API_BASE unset and Vite proxies /chat to the backend.
// In production (Railway), set VITE_API_BASE to the backend's public URL.
const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
// Optional shared secret — sent as X-API-Key when the backend has API_KEY set.
// NOTE: a key baked into a browser bundle is visible to anyone who reads it; it
// raises the bar (blocks casual direct calls) but isn't real auth on its own.
const API_KEY = (import.meta.env.VITE_API_KEY ?? "").trim();

function jsonHeaders(): Record<string, string> {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

export async function sendChat(message: string, threadId?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.ok) throw new Error(`chat failed: ${res.status}`);
  return res.json();
}

/** Forward a thumbs up/down to the backend, which records it as LangSmith
 *  run feedback (no-op server-side when tracing is disabled). */
export async function sendFeedback(
  runId: string,
  score: number,
  comment?: string,
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({ run_id: runId, score, comment }),
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { ok?: boolean };
    return Boolean(data.ok);
  } catch {
    return false;
  }
}

export interface RouteMeta {
  route: ChatResponse["route"];
  confidence: number;
  reason?: string | null;
}

/**
 * Live SSE from /chat/stream — the app's real-time path.
 * Event order: `meta` (routing decision) → `token`* (prose deltas) → `final`
 * (full shaped payload incl. run_id). `stream_error` / transport errors call
 * onError. EventSource can't set headers, so the API key rides as a query param.
 */
export function streamChat(
  message: string,
  handlers: {
    onMeta?: (m: RouteMeta) => void;
    onToken?: (t: string) => void;
    onFinal?: (r: ChatResponse) => void;
    onError?: (detail?: string) => void;
  },
  threadId?: string,
): EventSource {
  const params = new URLSearchParams({ message });
  if (threadId) params.set("thread_id", threadId);
  if (API_KEY) params.set("api_key", API_KEY);
  const es = new EventSource(`${API_BASE}/chat/stream?${params.toString()}`);

  es.addEventListener("meta", (e) => handlers.onMeta?.(JSON.parse((e as MessageEvent).data)));
  es.addEventListener("token", (e) => handlers.onToken?.((e as MessageEvent).data));
  es.addEventListener("final", (e) => {
    handlers.onFinal?.(JSON.parse((e as MessageEvent).data));
    es.close();
  });
  es.addEventListener("stream_error", (e) => {
    let detail: string | undefined;
    try {
      detail = JSON.parse((e as MessageEvent).data)?.detail;
    } catch {
      /* ignore */
    }
    handlers.onError?.(detail);
    es.close();
  });
  es.onerror = () => {
    handlers.onError?.();
    es.close();
  };
  return es;
}
