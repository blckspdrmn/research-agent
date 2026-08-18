if (!process.env.API_URL_INTERNAL) {
  throw new Error("API_URL_INTERNAL is not set");
}
export const API_URL = process.env.API_URL_INTERNAL;

// APIエラーを定義し、呼び出し側でstatusごとに分岐できるように
export class ApiError extends Error {
  constructor(public status: number) {
    super(`API error: ${status}`);
    this.name = "ApiError";
  }
}
