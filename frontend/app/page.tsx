"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";
import Spinner from "@/components/Spinner";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(isLoggedIn() ? "/dashboard" : "/login");
  }, [router]);

  return (
    <main className="flex h-screen items-center justify-center">
      <Spinner label="Loading MyUNO Capital…" />
    </main>
  );
}
