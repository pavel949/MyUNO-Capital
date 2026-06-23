import { scoreBadgeClasses, type ScoreTone } from "@/lib/score";

interface ScoreBadgeProps {
  /** A 0–100 score. */
  score: number;
  /** "good" = higher is better; "bad" = higher is worse. */
  tone?: ScoreTone;
  /** Optional label shown before the number (e.g. "Risk"). */
  label?: string;
}

export function ScoreBadge({ score, tone = "good", label }: ScoreBadgeProps) {
  const value = Math.round(score);
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold ${scoreBadgeClasses(
        score,
        tone,
      )}`}
      title={`${label ? `${label}: ` : ""}${value}/100`}
    >
      {label ? <span className="opacity-70">{label}</span> : null}
      <span>{value}</span>
    </span>
  );
}

export default ScoreBadge;
