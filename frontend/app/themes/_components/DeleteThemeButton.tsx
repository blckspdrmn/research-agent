"use client";

import { useActionState } from "react";
import { deleteTheme } from "../actions";
import { initialFormState } from "../form-state";
import { Button } from "@/components/ui/button";

export function DeleteThemeButton({ id }: { id: string }) {
  const [state, formAction, pending] = useActionState(
    deleteTheme.bind(null, id),
    initialFormState,
  );

  return (
    <form action={formAction}>
      <Button type="submit" variant="destructive" size="sm" disabled={pending}>
        {pending ? "削除中..." : "削除"}
      </Button>
      {state.status === "error" && (
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      )}
    </form>
  );
}
