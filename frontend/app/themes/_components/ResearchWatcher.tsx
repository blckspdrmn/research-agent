"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import type { ThemeListItem } from "@/lib/types";
import { usePolling } from "@/lib/hooks/usePolling";

const POLL_INTERVAL_MS = 5000;

// 実行中のテーマがある間は一覧を取り直し、実行が終わったテーマを通知する
export function ResearchWatcher({ themes }: { themes: ThemeListItem[] }) {
  const router = useRouter();
  const wasResearching = useRef(new Map<string, boolean>());

  usePolling(
    themes.some((t) => t.is_researching),
    POLL_INTERVAL_MS,
  );

  useEffect(() => {
    for (const theme of themes) {
      const finished =
        wasResearching.current.get(theme.id) && !theme.is_researching;
      const openReport = {
        label: "レポートを見る",
        onClick: () => router.push(`/themes/${theme.id}`),
      };
      if (finished && theme.latest_report_status === "completed") {
        toast.success(`「${theme.title}」のリサーチが完了しました`, {
          action: openReport,
        });
      }
      if (finished && theme.latest_report_status === "failed") {
        toast.error(`「${theme.title}」のリサーチに失敗しました`, {
          action: { ...openReport, label: "詳細を見る" },
        });
      }
      wasResearching.current.set(theme.id, theme.is_researching);
    }
  }, [themes, router]);

  return null;
}
