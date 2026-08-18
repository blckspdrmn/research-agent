"use client";

import { useActionState, useEffect } from "react";
import type { Theme } from "@/lib/types";
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

  useEffect(() => {
    if (state.status === "success") onDone();
  }, [state, onDone]);

  return (
    <form action={formAction} className="flex flex-1 flex-col gap-3">
      <Input
        name="title"
        defaultValue={theme.title}
        required
        maxLength={100}
        disabled={pending}
        aria-label="テーマ名"
        className="font-semibold"
      />
      <Input
        name="description"
        defaultValue={theme.description ?? ""}
        disabled={pending}
        aria-label="説明"
        className="text-sm"
      />
      {state.status === "error" && (
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      )}
      <div className="mt-auto flex gap-2">
        <Button type="submit" size="sm" disabled={pending}>
          {pending ? "保存中..." : "保存"}
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onDone}
          disabled={pending}
        >
          キャンセル
        </Button>
      </div>
    </form>
  );
}
