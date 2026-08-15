"use client";

import { Button } from "@/components/ui/button";

export default function Error({
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <h1 className="text-xl font-bold">テーマ一覧を表示できませんでした</h1>
      <p className="text-sm text-muted-foreground">
        時間をおいて再度お試しください。
      </p>
      <Button onClick={retry}>再試行</Button>
    </main>
  );
}
