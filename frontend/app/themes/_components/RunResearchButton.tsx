"use client";

import { useActionState, useEffect } from "react";
import { toast } from "sonner";
import { runResearch } from "../actions";
import { initialFormState } from "../form-state";
import { Button } from "@/components/ui/button";

export function RunResearchButton({
  id,
  isResearching,
}: {
  id: string;
  isResearching: boolean;
}) {
  const [state, formAction, pending] = useActionState(
    runResearch.bind(null, id),
    initialFormState,
  );
  const running = pending || isResearching;

  useEffect(() => {
    if (state.status !== "error") return;
    const contactUrl = state.contactUrl;
    toast.error(state.message, {
      action: contactUrl && {
        label: "GitHub Issuesで連絡する",
        onClick: () => window.open(contactUrl, "_blank", "noopener,noreferrer"),
      },
    });
  }, [state]);

  return (
    <form action={formAction}>
      <Button type="submit" size="sm" disabled={running} variant="outline">
        {running ? "リサーチ実行中" : "今すぐリサーチ"}
      </Button>
    </form>
  );
}
