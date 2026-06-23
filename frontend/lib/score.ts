// Pure helpers for color-coding 0–100 scores.
//
// Convention (see docs/decision-hub.md): for "potential"/"good" scores a
// higher value is better, while for "risk"/"complexity" a higher value is
// worse. `tone` selects the orientation.

export type ScoreTone = "good" | "bad";

export type ScoreLevel = "low" | "medium" | "high";

/** Clamp an arbitrary number into the 0–100 range. */
export function clampScore(value: number): number {
  if (Number.isNaN(value)) return 0;
  return Math.max(0, Math.min(100, value));
}

/** Bucket a 0–100 score into low/medium/high bands. */
export function scoreLevel(value: number): ScoreLevel {
  const v = clampScore(value);
  if (v < 34) return "low";
  if (v < 67) return "medium";
  return "high";
}

/**
 * Return a semantic color name for a score given its tone.
 * - tone "good": high = green (positive), low = red.
 * - tone "bad":  high = red (negative),  low = green.
 */
export function scoreColor(
  value: number,
  tone: ScoreTone = "good",
): "green" | "amber" | "red" {
  const level = scoreLevel(value);
  if (level === "medium") return "amber";
  if (tone === "good") {
    return level === "high" ? "green" : "red";
  }
  // tone === "bad"
  return level === "high" ? "red" : "green";
}

/** Tailwind class set for a colored score badge. */
export function scoreBadgeClasses(
  value: number,
  tone: ScoreTone = "good",
): string {
  const color = scoreColor(value, tone);
  switch (color) {
    case "green":
      return "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30";
    case "amber":
      return "bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30";
    case "red":
      return "bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30";
  }
}
