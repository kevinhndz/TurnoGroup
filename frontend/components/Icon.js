const paths = {
  arrow: <><path d="M4 12h16M14 6l6 6-6 6" /></>,
  menu: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
  close: <><path d="m6 6 12 12M6 18 18 6" /></>,
  check: <><path d="m5 12 4 4L19 6" /></>,
  receipt: <><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z" /><path d="M9 7h6M9 11h6M9 15h3" /></>,
  book: <><path d="M12 5v16M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2V4Z" /></>,
  store: <><path d="M4 10v11h16V10M3 6l2-3h14l2 3v4H3V6ZM9 21v-7h6v7M8 6v4M16 6v4" /></>,
  team: <><circle cx="9" cy="7" r="3" /><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3" /></>,
  table: <><path d="M3 10h18V6H3v4ZM5 10l-2 11M19 10l2 11M7 16h10" /></>,
  money: <><rect x="2" y="5" width="20" height="14" rx="2" /><circle cx="12" cy="12" r="3" /><path d="M5 9h1M18 15h1" /></>,
  upload: <><path d="M14 2H5v20h14V7l-5-5ZM14 2v5h5M12 18V10m-3 3 3-3 3 3" /></>,
  chart: <><path d="M3 3v18h18M7 16v-4M12 16V7M17 16v-7" /></>,
  coffee: <><path d="M4 7h12v8a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V7ZM16 8h2a3 3 0 1 1 0 6h-2M8 2v2M12 2v2" /></>,
  plus: <><path d="M12 4v16M4 12h16" /></>,
  minus: <><path d="M4 12h16" /></>,
};
export default function Icon({ name = 'arrow', size = 20, ...props }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.arrow}</svg>;
}
