import Link from "next/link";
import { fetchTheme } from "@/lib/api/themes";
import { fetchReports } from "@/lib/api/reports";
import { ReportDetail } from "./_components/ReportDetail";

export default async function ThemeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [theme, reports] = await Promise.all([
    fetchTheme(id),
    fetchReports(id),
  ]);

  return (
    <main className="mx-auto max-w-4xl space-y-6 p-6">
      <Link
        href="/themes"
        className="text-sm text-muted-foreground hover:underline"
      >
        &larr; テーマ一覧に戻る
      </Link>

      <div>
        <h1 className="text-2xl font-bold">{theme.title}</h1>
        {theme.description && (
          <p className="mt-1 text-muted-foreground">{theme.description}</p>
        )}
      </div>

      <ReportDetail reports={reports} />
    </main>
  );
}
