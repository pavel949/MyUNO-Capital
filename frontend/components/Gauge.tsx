import { clampScore, scoreColor } from "@/lib/score";

interface GaugeProps {
  /** 0–100 score. */
  value: number;
  label?: string;
  size?: number;
}

const COLOR_MAP: Record<string, string> = {
  green: "#34d399",
  amber: "#fbbf24",
  red: "#fb7185",
};

export function Gauge({ value, label, size = 140 }: GaugeProps) {
  const v = clampScore(value);
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  // Render as a 270° arc gauge.
  const arcFraction = 0.75;
  const dash = circumference * arcFraction;
  const progress = (v / 100) * dash;
  const color = COLOR_MAP[scoreColor(v, "good")];

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-[135deg]"
        role="img"
        aria-label={`${label ?? "Score"}: ${Math.round(v)} out of 100`}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1f2a40"
          strokeWidth={stroke}
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={`${progress} ${circumference}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="-mt-[calc(50%+4px)] flex flex-col items-center pb-6">
        <span className="text-3xl font-bold text-slate-50">
          {Math.round(v)}
        </span>
        <span className="text-xs text-muted">/ 100</span>
      </div>
      {label ? <span className="mt-1 text-sm text-muted">{label}</span> : null}
    </div>
  );
}

export default Gauge;
