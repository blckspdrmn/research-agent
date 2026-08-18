import type { ReportStatus } from "@/lib/types";
import { Badge } from "@/components/ui/badge";

const STATUS_CONFIG: Record<
  ReportStatus,
  { text: string; variant: "default" | "secondary" | "destructive" }
> = {
  pending: { text: "待機中", variant: "secondary" },
  running: { text: "実行中...", variant: "secondary" },
  completed: { text: "完了", variant: "default" },
  failed: { text: "失敗", variant: "destructive" },
};

export function ReportStatusBadge({ status }: { status: ReportStatus }) {
  const config = STATUS_CONFIG[status];
  return <Badge variant={config.variant}>{config.text}</Badge>;
}
