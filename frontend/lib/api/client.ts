import "server-only";
import { redirect } from "next/navigation";

import { requireApiAccessToken } from "@/lib/server-access-token";

function getApiUrl(): string {
  const url = process.env.API_URL_INTERNAL;
  if (!url) throw new Error("API_URL_INTERNAL is not set");
  return url;
}

// APIエラーを定義し、呼び出し側でstatusごとに分岐できるように
export class ApiError extends Error {
  constructor(public status: number) {
    super(`API error: ${status}`);
    this.name = "ApiError";
  }
}

export async function authenticatedFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const accessToken = await requireApiAccessToken();
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${accessToken}`);
  const res = await fetch(`${getApiUrl()}${path}`, { ...init, headers });
  if (res.status === 401) redirect("/login");
  if (!res.ok) throw new ApiError(res.status);
  return res;
}
