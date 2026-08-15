"use client";

import { useActionState, useEffect } from "react";
import type { Theme } from "@/lib/api";
import { updateTheme } from "../actions";
import { initialFormState } from "../form-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function EditThemeForm({
  theme,
  onDone,
}: {
  theme: Theme;
  onDone: () => void;
}) {
  const [state, formAction, pending] = useActionState(
    updateTheme.bind(null, theme.id),
    initialFormState,
  );

  // 更新が成功したら表示モードに戻す
  useEffect(() => {
    if (state.status === "success") onDone();
  }, [state, onDone]);

  return (
    <form action={formAction} className="space-y-2">
      <div className="flex gap-2">
        <Input
          name="title"
          defaultValue={theme.title}
          required
          maxLength={100}
          disabled={pending}
          aria-label="テーマ名"
        />
        <Input
          name="description"
          defaultValue={theme.description ?? ""}
          disabled={pending}
          aria-label="説明"
        />
        <Button type="submit" disabled={pending}>
          {pending ? "保存中..." : "保存"}
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={onDone}
          disabled={pending}
        >
          キャンセル
        </Button>
      </div>
      {state.status === "error" && (
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      )}
    </form>
  );
}
