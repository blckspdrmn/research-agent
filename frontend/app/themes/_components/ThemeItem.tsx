"use client";

import { useCallback, useState } from "react";
import type { Theme } from "@/lib/api";
import { EditThemeForm } from "./EditThemeForm";
import { DeleteThemeButton } from "./DeleteThemeButton";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function ThemeItem({ theme }: { theme: Theme }) {
  const [isEditing, setIsEditing] = useState(false);
  const handleDone = useCallback(() => setIsEditing(false), []);

  return (
    <Card>
      <CardContent className="p-4">
        {isEditing ? (
          <EditThemeForm theme={theme} onDone={handleDone} />
        ) : (
          <div className="flex items-center justify-between gap-4">
            <div>
              <span className="font-medium">{theme.title}</span>
              {theme.description && (
                <span className="ml-2 text-sm text-muted-foreground">
                  {theme.description}
                </span>
              )}
            </div>
            <div className="flex shrink-0 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                編集
              </Button>
              <DeleteThemeButton id={theme.id} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
