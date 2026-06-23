interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
      <span>{message}</span>
      {onRetry ? (
        <button
          onClick={onRetry}
          className="shrink-0 rounded-md border border-rose-500/40 px-2.5 py-1 text-xs font-medium text-rose-100 hover:bg-rose-500/20"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export default ErrorBanner;
