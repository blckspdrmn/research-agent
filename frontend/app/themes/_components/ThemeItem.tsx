"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import type { Theme } from "@/lib/types";
import { EditThemeForm } from "./EditThemeForm";
import { DeleteThemeButton } from "./DeleteThemeButton";
import { RunResearchButton } from "./RunResearchButton";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function ThemeItem({ theme }: { theme: Theme }) {
  const [isEditing, setIsEditing] = useState(false);
  const handleDone = useCallback(() => setIsEditing(false), []);

  return (
    <Card className="flex flex-col">
      {isEditing ? (
        <CardContent className="flex flex-1 flex-col px-5 pb-5 pt-4">
          <EditThemeForm theme={theme} onDone={handleDone} />
        </CardContent>
      ) : (
        <>
          <div className="flex items-start justify-between gap-2 px-5 pt-4">
            <Link
              href={`/themes/${theme.id}`}
              className="font-semibold hover:underline"
            >
              {theme.title}
            </Link>
          </div>
          <CardContent className="flex flex-1 flex-col gap-3 px-5 pb-5 pt-3">
            <p className="min-h-[2.6em] text-sm text-muted-foreground">
              {theme.description ?? ""}
            </p>
            <p className="text-xs text-muted-foreground">
              更新{" "}
              {new Date(theme.updated_at).toLocaleDateString("ja-JP", {
                timeZone: "Asia/Tokyo",
              })}
            </p>
            <div className="mt-auto flex gap-2">
              <Link href={`/themes/${theme.id}`}>
                <Button size="sm">詳細</Button>
              </Link>
              <RunResearchButton id={theme.id} />
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                編集
              </Button>
              <DeleteThemeButton id={theme.id} />
            </div>
          </CardContent>
        </>
      )}
    </Card>
  );
}
