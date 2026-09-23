import { signIn } from "@/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
  return (
    <main className="mx-auto w-full max-w-md p-6 pt-24">
      <Card>
        <CardHeader>
          <CardTitle>Research Agentへログイン</CardTitle>
          <CardDescription>
            セッションの期限が切れた場合も、ここからログインし直せます。
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* https://authjs.dev/getting-started/session-management/login */}
          <form
            action={async () => {
              "use server";
              await signIn("microsoft-entra-id", { redirectTo: "/themes" });
            }}
          >
            <Button type="submit" className="w-full">
              ログイン／新規登録
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
