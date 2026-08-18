import ReactMarkdown from "react-markdown";
import type { Report } from "@/lib/types";

export function ReportContent({ report }: { report: Report }) {
  if (report.status === "failed") {
    return (
      <p className="text-sm text-destructive">
        {report.error_message ?? "エラーが発生しました"}
      </p>
    );
  }

  if (report.status !== "completed") {
    return (
      <p className="text-sm text-muted-foreground">
        リサーチを実行中です。完了すると自動的に表示されます。
      </p>
    );
  }

  return (
    <div>
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <ReactMarkdown
          components={{
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
          }}
        >
          {report.content_md}
        </ReactMarkdown>
      </div>
      {process.env.NODE_ENV === "development" &&
        report.llm_call_count != null && (
          <p className="mt-4 text-xs text-muted-foreground">
            [DEV環境でのみ表示] LLM呼び出し: {report.llm_call_count}回 / 入力:{" "}
            {report.total_input_tokens?.toLocaleString()} tokens / 出力:{" "}
            {report.total_output_tokens?.toLocaleString()} tokens
          </p>
        )}
    </div>
  );
}
