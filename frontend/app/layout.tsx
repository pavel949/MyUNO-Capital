import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "MyUNO Capital — Founder Console",
  description:
    "The full virtual team for solo entrepreneurs: validate ideas, build, grow, and exit your business from one AI-powered platform.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
