import type { Report } from "@/lib/types";
import { API_URL, ApiError } from "./client";

export async function fetchReports(themeId: string): Promise<Report[]> {
  const res = await fetch(`${API_URL}/themes/${themeId}/reports`, {
    cache: "no-store",
  });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function runResearchRequest(themeId: string): Promise<void> {
  const res = await fetch(`${API_URL}/themes/${themeId}/research`, {
    method: "POST",
  });
  if (!res.ok) throw new ApiError(res.status);
}
