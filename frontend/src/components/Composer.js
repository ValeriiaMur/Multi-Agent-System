import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { PlusIcon, SendIcon, MicIcon } from "./icons";
const blur = "backdrop-blur-[22px] [backdrop-filter:blur(22px)_saturate(170%)]";
/** iMessage-style composer. */
export function Composer({ disabled, onSend }) {
    const [value, setValue] = useState("");
    const send = () => {
        const text = value.trim();
        if (!text || disabled)
            return;
        onSend(text);
        setValue("");
    };
    return (_jsxs("div", { className: `flex shrink-0 items-end gap-[9px] border-t border-line-soft bg-header-bg px-3 pb-2.5 pt-2 ${blur}`, children: [_jsx("button", { className: "flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full bg-surface text-ink2", "aria-label": "Add", children: _jsx(PlusIcon, {}) }), _jsxs("div", { className: "flex flex-1 items-center gap-2 rounded-[19px] border-[1.5px] border-line py-[5px] pl-3.5 pr-1.5", children: [_jsx("input", { className: "min-w-0 flex-1 bg-transparent py-[3px] text-[16px] text-ink outline-none placeholder:text-muted", value: value, placeholder: "Message", "aria-label": "message", onChange: (e) => setValue(e.target.value), onKeyDown: (e) => {
                            if (e.key === "Enter")
                                send();
                        } }), value.trim() ? (_jsx("button", { className: "flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full bg-blue transition hover:brightness-110 disabled:opacity-50", onClick: send, disabled: disabled, "aria-label": "Send", children: _jsx(SendIcon, {}) })) : (_jsx("button", { className: "flex px-1 py-0.5 text-ink2", "aria-label": "Dictate", children: _jsx(MicIcon, {}) }))] })] }));
}
