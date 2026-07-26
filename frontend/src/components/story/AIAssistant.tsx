"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { AISuggestionPanel } from "./AISuggestion";
import { aiApi } from "@/lib/api/ai";
import type { AISuggestion } from "@/lib/api/ai";

interface AIAssistantProps {
  sectionId: string;
  onApply: (content: string) => void;
}

type LoadingState = "idle" | "improve" | "expand";

export function AIAssistant({ sectionId, onApply }: AIAssistantProps) {
  const [loading, setLoading] = useState<LoadingState>("idle");
  const [suggestion, setSuggestion] = useState<AISuggestion | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImprove = async () => {
    setLoading("improve");
    setError(null);
    try {
      const result = await aiApi.improveSection(sectionId);
      setSuggestion(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al obtener sugerencia");
    } finally {
      setLoading("idle");
    }
  };

  const handleExpand = async () => {
    setLoading("expand");
    setError(null);
    try {
      const result = await aiApi.expandSection(sectionId);
      setSuggestion(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al expandir narrativa");
    } finally {
      setLoading("idle");
    }
  };

  const handleAccept = async (suggested: string) => {
    try {
      await aiApi.applySuggestion(sectionId, suggested);
      onApply(suggested);
      setSuggestion(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al aplicar sugerencia");
    }
  };

  const handleReject = () => {
    setSuggestion(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleImprove}
          disabled={loading !== "idle"}
        >
          {loading === "improve" ? "Mejorando..." : "Mejorar con IA"}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleExpand}
          disabled={loading !== "idle"}
        >
          {loading === "expand" ? "Expandiendo..." : "Expandir narrativa"}
        </Button>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {suggestion && (
        <AISuggestionPanel
          suggestion={suggestion}
          onAccept={handleAccept}
          onReject={handleReject}
        />
      )}
    </div>
  );
}
