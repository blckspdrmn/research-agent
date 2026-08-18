"use client";

import { useActionState } from "react";
import { runResearch } from "../actions";
import { initialFormState } from "../form-state";
import { Button } from "@/components/ui/button";

export function RunResearchButton({ id }: { id: string }) {
  const [state, formAction, pending] = useActionState(
    runResearch.bind(null, id),
    initialFormState,
  );

  return (
    <form action={formAction}>
      <Button type="submit" size="sm" disabled={pending} variant="outline">
        {pending ? "実行中..." : "今すぐリサーチ"}
      </Button>
      {state.status === "error" && (
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      )}
    </form>
  );
}
