import type { Report } from "@/lib/types";
import { ReportStatusBadge } from "./ReportStatusBadge";
import { cn } from "@/lib/utils";

export function ReportListItem({
  report,
  selected,
  onClick,
}: {
  report: Report;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left px-3 py-2 rounded-md transition-colors",
        selected
          ? "bg-muted shadow-[inset_2px_0_0] shadow-foreground"
          : "hover:bg-muted/50",
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium truncate">
          {new Date(report.created_at).toLocaleDateString("ja-JP", {
            timeZone: "Asia/Tokyo",
          })}
        </span>
        <ReportStatusBadge status={report.status} />
      </div>
    </button>
  );
}
