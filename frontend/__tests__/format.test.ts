import { describe, expect, it } from "vitest";
import { formatCurrency, formatPercent, titleize } from "../lib/format";

describe("formatCurrency", () => {
  it("formats whole-dollar USD", () => {
    expect(formatCurrency(4200)).toBe("$4,200");
  });
  it("renders an em dash for nullish values", () => {
    expect(formatCurrency(null)).toBe("—");
    expect(formatCurrency(undefined)).toBe("—");
  });
});

describe("formatPercent", () => {
  it("adds a + sign for positive growth", () => {
    expect(formatPercent(18.5)).toBe("+18.5%");
  });
  it("keeps the - sign for negative growth", () => {
    expect(formatPercent(-3.1)).toBe("-3.1%");
  });
});

describe("titleize", () => {
  it("turns snake_case into Title Case", () => {
    expect(titleize("b2b_saas_micro")).toBe("B2b Saas Micro");
    expect(titleize("source_control")).toBe("Source Control");
  });
});
