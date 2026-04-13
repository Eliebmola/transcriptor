export function StatusBanner({ tone = "neutral", children }) {
  if (!children) return null;
  return <div className={`status-banner ${tone}`}>{children}</div>;
}
