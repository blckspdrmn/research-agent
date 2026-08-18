"use client";

import { useState } from "react";
import type { Report } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { ReportList } from "./ReportList";
import { ReportContent } from "./ReportContent";
import { usePolling } from "@/lib/hooks/usePolling";

const POLL_INTERVAL_MS = 5000;

export function ReportDetail({ reports }: { reports: Report[] }) {
  const [selectedId, setSelectedId] = useState<string>(reports[0]?.id ?? "");
  const selected = reports.find((r) => r.id === selectedId);

  // リサーチ中のレポートがある間はリサーチ完了をカスタムフック経由でPollingする
  const hasActiveReport = reports.some(
    (r) => r.status === "pending" || r.status === "running",
  );
  usePolling(hasActiveReport, POLL_INTERVAL_MS);

  if (reports.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        まだレポートがありません。テーマ一覧から「リサーチ実行」してください。
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-[260px_1fr]">
      <ReportList
        reports={reports}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <Card>
        <CardContent className="pt-6">
          {selected && <ReportContent report={selected} />}
        </CardContent>
      </Card>
    </div>
  );
}
