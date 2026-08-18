import type { Theme } from "@/lib/types";
import { API_URL, ApiError } from "./client";

export async function fetchThemes(): Promise<Theme[]> {
  const res = await fetch(`${API_URL}/themes`, { cache: "no-store" });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function fetchTheme(id: string): Promise<Theme> {
  const res = await fetch(`${API_URL}/themes/${id}`, { cache: "no-store" });
  if (!res.ok) throw new ApiError(res.status);
  return res.json();
}

export async function createThemeRequest(input: {
  title: string;
  description: string | null;
}): Promise<void> {
  const res = await fetch(`${API_URL}/themes`, {
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
  const res = await fetch(`${API_URL}/themes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new ApiError(res.status);
}

export async function deleteThemeRequest(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/themes/${id}`, { method: "DELETE" });
  if (!res.ok) throw new ApiError(res.status);
}
