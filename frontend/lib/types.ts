export type Theme = {
  id: string;
  title: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type ReportStatus = "pending" | "running" | "completed" | "failed";

export type Report = {
  id: string;
  theme_id: string;
  content_md: string;
  status: ReportStatus;
  error_message: string | null;
  created_at: string;
  total_input_tokens: number | null;
  total_output_tokens: number | null;
  llm_call_count: number | null;
};
