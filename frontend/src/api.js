// In dev, leave VITE_API_BASE unset and Vite proxies /chat to the backend.
// In production (Railway), set VITE_API_BASE to the backend's public URL.
const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
export async function sendChat(message, threadId) {
    const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, thread_id: threadId }),
    });
    if (!res.ok)
        throw new Error(`chat failed: ${res.status}`);
    return res.json();
}
/** Forward a thumbs up/down to the backend, which records it as LangSmith
 *  run feedback (no-op server-side when tracing is disabled). */
export async function sendFeedback(runId, score, comment) {
    try {
        const res = await fetch(`${API_BASE}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ run_id: runId, score, comment }),
        });
        if (!res.ok)
            return false;
        const data = (await res.json());
        return Boolean(data.ok);
    }
    catch {
        return false;
    }
}
/** SSE token stream from the backend's /chat/stream endpoint. */
export function streamChat(message, handlers, threadId) {
    const params = new URLSearchParams({ message });
    if (threadId)
        params.set("thread_id", threadId);
    const es = new EventSource(`${API_BASE}/chat/stream?${params.toString()}`);
    es.addEventListener("token", (e) => handlers.onToken?.(e.data));
    es.addEventListener("final", (e) => {
        handlers.onFinal?.(JSON.parse(e.data));
        es.close();
    });
    es.onerror = () => es.close();
    return es;
}
