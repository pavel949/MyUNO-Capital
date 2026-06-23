export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-muted" role="status">
      <span
        className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-border-subtle border-t-brand"
        aria-hidden="true"
      />
      {label ? <span className="text-sm">{label}</span> : null}
      <span className="sr-only">Loading</span>
    </div>
  );
}

export default Spinner;
