import type { Theme } from "@/lib/types";
import { authenticatedFetch } from "./client";

export async function fetchThemes(): Promise<Theme[]> {
  const res = await authenticatedFetch("/themes");
  return res.json();
}

export async function fetchTheme(id: string): Promise<Theme> {
  const res = await authenticatedFetch(`/themes/${id}`);
  return res.json();
}

export async function createThemeRequest(input: {
  title: string;
  description: string | null;
}): Promise<void> {
  await authenticatedFetch("/themes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function updateThemeRequest(
  id: string,
  input: { title?: string; description?: string | null },
): Promise<void> {
  await authenticatedFetch(`/themes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteThemeRequest(id: string): Promise<void> {
  await authenticatedFetch(`/themes/${id}`, { method: "DELETE" });
}
