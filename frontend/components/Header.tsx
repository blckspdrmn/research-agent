import Link from "next/link";

import { auth, signOut } from "@/auth";
import { Button } from "@/components/ui/button";

export async function Header() {
  const session = await auth();
  return (
    <header className="border-b">
      <div className="mx-auto flex max-w-5xl items-center justify-between p-4">
        <Link href="/themes" className="font-semibold">
          Research Agent
        </Link>
        {session?.user ? (
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground">
              {session.user.email ?? "ログイン中"}
            </span>
            {/* https://authjs.dev/getting-started/session-management/login#signout */}
            <form
              action={async () => {
                "use server";
                await signOut({ redirectTo: "/login" });
              }}
            >
              <Button type="submit" variant="outline" size="sm">
                ログアウト
              </Button>
            </form>
          </div>
        ) : (
          <Link href="/login" className="text-sm">
            ログインしてください
          </Link>
        )}
      </div>
    </header>
  );
}
