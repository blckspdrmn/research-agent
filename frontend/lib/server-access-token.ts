import { redirect } from "next/navigation";

import { auth } from "@/auth";

export async function requireApiAccessToken(): Promise<string> {
  // https://authjs.dev/getting-started/migrating-to-v5#details
  const session = await auth();
  if (
    !session?.accessToken ||
    !session.expiresAt ||
    // APIリクエストを投げる時間を鑑みて期限まで30秒を切っている場合にはsigninへ
    session.expiresAt <= Date.now() / 1000 + 30
  ) {
    redirect("/api/auth/signin");
  }
  return session.accessToken;
}
