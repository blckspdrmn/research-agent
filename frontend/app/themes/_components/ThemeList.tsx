import type { Theme } from "@/lib/api";
import { ThemeItem } from "./ThemeItem";

export function ThemeList({ themes }: { themes: Theme[] }) {
  if (themes.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        まだテーマがありません。上のフォームから登録してください。
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {themes.map((theme) => (
        <li key={theme.id}>
          <ThemeItem theme={theme} />
        </li>
      ))}
    </ul>
  );
}
