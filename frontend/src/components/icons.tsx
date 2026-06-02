// Inline SVG icons — currentColor so Tailwind text-* classes drive their color.
export const BackIcon = () => (
  <svg width="11" height="18" viewBox="0 0 11 18" fill="none">
    <path d="M9 1L2 9l7 8" stroke="var(--blue)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const MediaIcon = () => (
  <svg width="20" height="18" viewBox="0 0 22 20" fill="none">
    <rect x="1" y="3" width="20" height="14" rx="3" stroke="currentColor" strokeWidth="1.7" />
    <circle cx="7" cy="8" r="1.8" fill="currentColor" />
    <path d="M3 16l5-5 3 3 4-4 4 4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const PlusIcon = () => (
  <svg width="17" height="17" viewBox="0 0 17 17">
    <path d="M8.5 1v15M1 8.5h15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

export const SendIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M12 19V5M5 12l7-7 7 7" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const MicIcon = () => (
  <svg width="15" height="20" viewBox="0 0 15 22" fill="none">
    <rect x="4.5" y="1" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.7" />
    <path d="M1.5 9.5a6 6 0 0012 0M7.5 15.5V20" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
  </svg>
);

export const CopyIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <rect x="8" y="8" width="12" height="12" rx="2.5" stroke="currentColor" strokeWidth="1.8" />
    <path d="M4 16V5a1 1 0 011-1h11" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const CheckIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path d="M5 13l4 4 10-10" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const RegenIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path d="M20 11a8 8 0 10-1 5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
    <path d="M20 4v6h-6" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const ThumbUpIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path
      d="M7 10v9H4v-9h3zm0 0l5-7c1.3 0 2 .9 2 2l-.8 4H19a2 2 0 012 2.3l-1.2 6A2 2 0 0117.8 19H7"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
  </svg>
);

export const ThumbDownIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
    <path
      d="M17 14V5h3v9h-3zm0 0l-5 7c-1.3 0-2-.9-2-2l.8-4H5a2 2 0 01-2-2.3l1.2-6A2 2 0 016.2 5H17"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
  </svg>
);
