"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { AISuggestion } from "@/lib/api/ai";

interface AISuggestionProps {
  suggestion: AISuggestion;
  onAccept: (suggestion: string) => void;
  onReject: () => void;
}

export function AISuggestionPanel({ suggestion, onAccept, onReject }: AISuggestionProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedSuggestion, setEditedSuggestion] = useState(suggestion.suggested);

  return (
    <div className="border rounded-lg p-4 space-y-3 bg-muted/30">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Sugerencia de IA</h4>
        <span className="text-xs text-muted-foreground">{suggestion.changes_summary}</span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">Original</p>
          <div className="p-2 rounded bg-background border whitespace-pre-wrap">
            {suggestion.original}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">Sugerido</p>
          {isEditing ? (
            <textarea
              value={editedSuggestion}
              onChange={(e) => setEditedSuggestion(e.target.value)}
              className="w-full p-2 rounded bg-background border min-h-[100px] resize-y"
            />
          ) : (
            <div className="p-2 rounded bg-background border whitespace-pre-wrap">
              {suggestion.suggested}
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-2 justify-end">
        <Button variant="outline" size="sm" onClick={onReject}>
          Rechazar
        </Button>
        <Button variant="outline" size="sm" onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? "Cancelar edición" : "Editar"}
        </Button>
        <Button
          size="sm"
          onClick={() => onAccept(isEditing ? editedSuggestion : suggestion.suggested)}
        >
          Aceptar
        </Button>
      </div>
    </div>
  );
}
