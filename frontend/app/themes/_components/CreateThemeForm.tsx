"use client";

import { useActionState } from "react";
import { createTheme } from "../actions";
import { initialFormState } from "../form-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function CreateThemeForm() {
  const [state, formAction, pending] = useActionState(
    createTheme,
    initialFormState,
  );

  return (
    <form action={formAction} className="space-y-2">
      <div className="flex gap-2">
        <Input
          name="title"
          placeholder="テーマ名"
          required
          maxLength={100}
          disabled={pending}
          aria-label="テーマ名"
        />
        <Input
          name="description"
          placeholder="説明(任意)"
          disabled={pending}
          aria-label="説明"
        />
        <Button type="submit" disabled={pending}>
          {pending ? "登録中..." : "登録"}
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
