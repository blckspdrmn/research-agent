import type { Report } from "@/lib/types";
import { authenticatedFetch } from "./client";

export async function fetchReports(themeId: string): Promise<Report[]> {
  const res = await authenticatedFetch(`/themes/${themeId}/reports`);
  return res.json();
}

export async function runResearchRequest(themeId: string): Promise<void> {
  await authenticatedFetch(`/themes/${themeId}/research`, { method: "POST" });
}
