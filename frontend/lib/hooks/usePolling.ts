import { useEffect } from "react";
import { useRouter } from "next/navigation";

export function usePolling(isActive: boolean, intervalMs: number) {
  const router = useRouter();

  useEffect(() => {
    if (!isActive) return;
    const id = setInterval(() => router.refresh(), intervalMs);
    return () => clearInterval(id);
  }, [isActive, intervalMs, router]);
}
