import type { Report } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ReportListItem } from "./ReportListItem";

export function ReportList({
  reports,
  selectedId,
  onSelect,
}: {
  reports: Report[];
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">レポート一覧</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {reports.map((report) => (
          <ReportListItem
            key={report.id}
            report={report}
            selected={report.id === selectedId}
            onClick={() => onSelect(report.id)}
          />
        ))}
      </CardContent>
    </Card>
  );
}
