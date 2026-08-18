import type { Report } from "@/lib/types";
import { getApiUrl, ApiError } from "./client";

export async function fetchReports(themeId: string): Promise<Report[]> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes/${themeId}/reports`, {
    cache: "no-store",
  });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function runResearchRequest(themeId: string): Promise<void> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes/${themeId}/research`, {
    method: "POST",
  });
  if (!res.ok) throw new ApiError(res.status);
}
