import type { Theme } from "@/lib/types";
import { getApiUrl, ApiError } from "./client";

export async function fetchThemes(): Promise<Theme[]> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes`, { cache: "no-store" });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function fetchTheme(id: string): Promise<Theme> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes/${id}`, { cache: "no-store" });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function createThemeRequest(input: {
  title: string;
  description: string | null;
}): Promise<void> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new ApiError(res.status);
}

export async function updateThemeRequest(
  id: string,
  input: { title?: string; description?: string | null },
): Promise<void> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new ApiError(res.status);
}

export async function deleteThemeRequest(id: string): Promise<void> {
  const baseUrl = getApiUrl();
  const res = await fetch(`${baseUrl}/themes/${id}`, { method: "DELETE" });
  if (!res.ok) throw new ApiError(res.status);
}
