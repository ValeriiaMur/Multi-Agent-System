import { useEffect, useRef, useState } from "react";
import { Markdown } from "./Markdown";

/** Muscle / equipment chip. `ink` variant = accent-tinted. */
export function Tag({ children, variant }: { children: React.ReactNode; variant?: "ink" }) {
  const base =
    "rounded-md border px-1.5 py-0.5 text-[10.5px] whitespace-nowrap leading-none py-1";
  return variant === "ink" ? (
    <span className={`${base} border-accent-22 bg-accent-14 text-accent`}>{children}</span>
  ) : (
    <span className={`${base} border-line-soft bg-chip text-ink2`}>{children}</span>
  );
}

/** Typing indicator with sparkle + bouncing dots. */
export function Typing({ label }: { label?: string }) {
  return (
    <div className="inline-flex items-center gap-[7px] self-start rounded-[19px] bg-bubble px-[15px] py-3">
      <span className="text-[12px] leading-none text-accent animate-sparkle" aria-hidden>
        ✦
      </span>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-2 w-2 rounded-full bg-muted animate-bounce2"
          style={{ animationDelay: `${i * 0.16}s` }}
        />
      ))}
      {label ? <span className="ml-0.5 font-mono text-[10px] text-muted">{label}</span> : null}
    </div>
  );
}

/** Indeterminate pulsing progress bar shown while an agent works. */
export function ThinkingBar() {
  return (
    <div className="absolute inset-x-0 -bottom-px z-[7] h-[3px] overflow-hidden animate-tbpulse" aria-hidden>
      <div className="absolute inset-0 bg-accent opacity-[0.14]" />
      <span className="tb-sweep" />
    </div>
  );
}

/** Reveal text word-by-word with a blinking caret. */
export function Streamer({
  text,
  speed = 24,
  markdown = false,
  onTick,
  onDone,
}: {
  text: string;
  speed?: number;
  markdown?: boolean;
  onTick?: () => void;
  onDone?: () => void;
}) {
  const parts = useRef<string[]>([]);
  const [n, setN] = useState(0);
  const onTickRef = useRef(onTick);
  const onDoneRef = useRef(onDone);
  onTickRef.current = onTick;
  onDoneRef.current = onDone;

  useEffect(() => {
    parts.current = String(text).split(/(\s+)/);
    setN(0);
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setN(i);
      onTickRef.current?.();
      if (i >= parts.current.length) {
        clearInterval(id);
        onDoneRef.current?.();
      }
    }, speed);
    return () => clearInterval(id);
  }, [text, speed]);

  const shown = parts.current.slice(0, n).join("");
  const done = n >= parts.current.length;

  // Markdown produces block elements, so reveal them inside a div (the bubble
  // already supplies padding). Plain text keeps the inline blinking caret.
  if (markdown) {
    return (
      <div className="text-[16px] leading-[1.4]">
        <Markdown>{shown}</Markdown>
        {!done ? <span className="caret" /> : null}
      </div>
    );
  }
  return (
    <span>
      {shown}
      {!done ? <span className="caret" /> : null}
    </span>
  );
}
