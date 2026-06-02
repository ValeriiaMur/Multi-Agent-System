export const ROUTE_META = {
    COACH: { label: "COACH", sub: "Coaching", glyph: "✦" },
    WORKOUT_GENERATE: { label: "GENERATE", sub: "Building workout", glyph: "▣" },
    WORKOUT_LOG: { label: "LOG", sub: "Logging", glyph: "✓" },
    CLARIFY: { label: "CLARIFY", sub: "Checking in", glyph: "?" },
};
export const STARTERS = [
    "What muscles does a deadlift work?",
    "Build me a 30-min upper body session with dumbbells",
    "I just did 3×10 bench press at 185 lbs",
];
/** Build the observability trace from the *real* response — router decision plus
 *  whatever each sub-agent actually produced (counts, match rates). */
export function deriveTrace(resp) {
    const pct = Math.round((resp.confidence ?? 0) * 100);
    const steps = [{ tool: "router.classify", arg: "intent", res: `${resp.route} · ${pct}%` }];
    if (resp.reason)
        steps.push({ tool: "reason", res: resp.reason });
    if (resp.route === "WORKOUT_GENERATE" && resp.workout) {
        const w = resp.workout;
        const meta = w.meta;
        if (meta) {
            const arg = [
                meta.muscle_groups?.length ? meta.muscle_groups.slice(0, 3).join(",") : "any",
                meta.equipment?.length ? meta.equipment.slice(0, 2).join(",") : "any",
            ].join(" · ");
            steps.push({ tool: "search_exercises", arg, res: `${w.main.length} matches` });
            if (meta.avoid_joints?.length)
                steps.push({ tool: "injury_filter", arg: meta.avoid_joints.join(","), res: "joints excluded" });
        }
        steps.push({
            tool: "build_workout",
            arg: meta ? `${meta.goal}·${meta.duration_min}m` : undefined,
            res: `${w.warmup.length}+${w.main.length}+${w.cooldown.length}`,
        });
    }
    else if (resp.route === "WORKOUT_LOG" && resp.log_entries) {
        const entries = resp.log_entries;
        const matched = entries.filter((e) => e.matched).length;
        steps.push({ tool: "extract_log", res: `${entries.length} parsed` });
        if (entries.length)
            steps.push({ tool: "fuzzy_match", res: `${matched}/${entries.length} matched` });
    }
    else if (resp.route === "COACH") {
        steps.push({ tool: "coach.respond", res: "grounded answer" });
    }
    else if (resp.route === "CLARIFY") {
        steps.push({ tool: "clarify", res: "low confidence → ask" });
    }
    return steps;
}
/** A natural lead-in bubble. Coach/Clarify use the model's real reply; generate
 *  and log format the real structured result into a friendly sentence. */
export function deriveLead(resp) {
    if (resp.route === "WORKOUT_GENERATE") {
        const m = resp.workout?.meta;
        if (!resp.workout || m?.empty)
            return resp.reply;
        const targets = m?.muscle_groups?.length ? `, targeting ${m.muscle_groups.slice(0, 3).join(", ")}` : "";
        const dur = m?.duration_min ? ` for ${m.duration_min} minutes` : "";
        return `Here's a ${m?.goal ?? "strength"} session${dur}${targets}. Warm-up and cool-down are built in.`;
    }
    if (resp.route === "WORKOUT_LOG") {
        return resp.log_entries?.length
            ? "Nice work. Logging that now —"
            : resp.reply || "I couldn't pull a set out of that — try e.g. “3×10 bench at 185”.";
    }
    return resp.reply;
}
/** Client-side quick replies for the CLARIFY route (presentational scaffolding). */
export function clarifyChips(text) {
    const short = text.trim().split(/\s+/).length <= 2;
    if (short)
        return [`Explain ${text}`, `Build around ${text}`, `Log ${text}`];
    if (/adjust|change|tweak|my workout/i.test(text))
        return ["Log what I did", "Build a new session"];
    return ["Coach a question", "Build me a workout", "Log a set"];
}
