export const dynamic = "force-dynamic";

import { fetchThemes } from "@/lib/api/themes";
import { CreateThemeForm } from "./_components/CreateThemeForm";
import { ThemeList } from "./_components/ThemeList";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default async function ThemesPage() {
  const themes = await fetchThemes();

  return (
    <main className="mx-auto max-w-5xl space-y-8 p-6">
      <h1 className="text-2xl font-bold">リサーチテーマ</h1>

      <Card>
        <CardHeader>
          <CardTitle>テーマを登録</CardTitle>
          <CardDescription>
            エージェントに調べさせたいテーマを入力してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CreateThemeForm />
        </CardContent>
      </Card>

      <ThemeList themes={themes} />
    </main>
  );
}
