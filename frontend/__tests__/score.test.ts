import { describe, expect, it } from "vitest";
import {
  clampScore,
  scoreBadgeClasses,
  scoreColor,
  scoreLevel,
} from "../lib/score";

describe("clampScore", () => {
  it("clamps below 0 to 0", () => {
    expect(clampScore(-20)).toBe(0);
  });
  it("clamps above 100 to 100", () => {
    expect(clampScore(150)).toBe(100);
  });
  it("passes values within range unchanged", () => {
    expect(clampScore(42)).toBe(42);
  });
  it("treats NaN as 0", () => {
    expect(clampScore(Number.NaN)).toBe(0);
  });
});

describe("scoreLevel", () => {
  it("buckets low/medium/high", () => {
    expect(scoreLevel(10)).toBe("low");
    expect(scoreLevel(50)).toBe("medium");
    expect(scoreLevel(90)).toBe("high");
  });
});

describe("scoreColor", () => {
  it("good tone: high is green, low is red", () => {
    expect(scoreColor(90, "good")).toBe("green");
    expect(scoreColor(10, "good")).toBe("red");
    expect(scoreColor(50, "good")).toBe("amber");
  });

  it("bad tone: high is red, low is green (inverted)", () => {
    expect(scoreColor(90, "bad")).toBe("red");
    expect(scoreColor(10, "bad")).toBe("green");
    expect(scoreColor(50, "bad")).toBe("amber");
  });
});

describe("scoreBadgeClasses", () => {
  it("returns emerald classes for a strong potential score", () => {
    expect(scoreBadgeClasses(82, "good")).toContain("emerald");
  });
  it("returns rose classes for a high risk score", () => {
    expect(scoreBadgeClasses(70, "bad")).toContain("rose");
  });
  it("returns amber classes for a mid score", () => {
    expect(scoreBadgeClasses(50, "good")).toContain("amber");
  });
});
