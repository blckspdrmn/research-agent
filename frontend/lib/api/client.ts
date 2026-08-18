export function getApiUrl(): string {
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
