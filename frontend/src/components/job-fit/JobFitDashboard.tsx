"use client";

import { useState } from "react";
import { jobFitApi, type JobFitResponse, type JobFitHistoryItem } from "@/lib/api/job-fit";
import { ScoreRadar } from "./ScoreRadar";
import { GapList } from "./GapList";

interface JobFitDashboardProps {
  facetId: string;
}

export function JobFitDashboard({ facetId }: JobFitDashboardProps) {
  const [jobPosting, setJobPosting] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<JobFitResponse | null>(null);
  const [history, setHistory] = useState<JobFitHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!jobPosting.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await jobFitApi.analyze(facetId, jobPosting);
      setResult(res);
      loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al analizar");
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await jobFitApi.getHistory(facetId);
      setHistory(res.analyses);
    } catch {
      // silently fail
    }
  };

  const handleDeleteAnalysis = async (analysisId: string) => {
    try {
      await jobFitApi.delete(analysisId);
      loadHistory();
    } catch {
      // silently fail
    }
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      <div className="border rounded-lg p-4">
        <label htmlFor="job-posting" className="block text-sm font-medium mb-2">
          Job Posting
        </label>
        <textarea
          id="job-posting"
          value={jobPosting}
          onChange={(e) => setJobPosting(e.target.value)}
          placeholder="Pega la descripción del empleo aquí..."
          className="w-full border rounded-md p-3 text-sm min-h-[160px] resize-y"
          maxLength={10000}
        />
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-muted-foreground">{jobPosting.length}/10000 caracteres</span>
          <button
            onClick={handleAnalyze}
            disabled={loading || !jobPosting.trim()}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Analizando..." : "Analizar"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive rounded-md p-3 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-12 text-muted-foreground">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3" />
          Analizando compatibilidad con IA...
        </div>
      )}

      {result && !loading && (
        <>
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">
                {result.job_title}{result.job_company ? ` en ${result.job_company}` : ""}
              </h3>
              <span className={`text-2xl font-bold ${scoreColor(result.overall_score)}`}>
                {Math.round(result.overall_score)}%
              </span>
            </div>
            <p className="text-sm text-muted-foreground">Score general de compatibilidad</p>
          </div>

          <ScoreRadar
            skills={result.skills_score}
            experience={result.experience_score}
            stack={result.stack_score}
            tone={result.tone_score}
          />

          <GapList
            gaps={result.gaps}
            suggestions={result.suggestions}
            reorderSuggestion={result.reorder_suggestion}
          />
        </>
      )}

      <div className="border rounded-lg p-4">
        <button
          onClick={() => {
            setShowHistory(!showHistory);
            if (!showHistory && history.length === 0) loadHistory();
          }}
          className="text-sm font-medium flex items-center gap-2"
        >
          {showHistory ? "Ocultar" : "Mostrar"} historial de análisis
        </button>
        {showHistory && (
          <div className="mt-3 space-y-2">
            {history.length === 0 && (
              <p className="text-sm text-muted-foreground">No hay análisis previos</p>
            )}
            {history.map((item) => (
              <div key={item.id} className="flex items-center justify-between border rounded-md p-3 text-sm">
                <div>
                  <span className="font-medium">{item.job_title ?? "Sin título"}</span>
                  {item.job_company && <span className="text-muted-foreground"> — {item.job_company}</span>}
                  <span className={`ml-2 font-mono text-xs ${scoreColor(item.overall_score)}`}>
                    {Math.round(item.overall_score)}%
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={() => handleDeleteAnalysis(item.id)}
                    className="text-destructive text-xs hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
