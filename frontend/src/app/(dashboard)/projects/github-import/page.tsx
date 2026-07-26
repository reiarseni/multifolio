"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { githubApi, type GitHubRepo } from "@/lib/api/github";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { githubImportApi, type AIGeneratedProject } from "@/lib/api/github-import";

export default function GitHubImportPage() {
  const router = useRouter();
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [facets, setFacets] = useState<Facet[]>([]);
  const [selectedRepoIds, setSelectedRepoIds] = useState<Set<string>>(new Set());
  const [selectedFacetId, setSelectedFacetId] = useState("");
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [generated, setGenerated] = useState<AIGeneratedProject[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      githubApi.listRepos().catch(() => [] as GitHubRepo[]),
      facetsApi.list().catch(() => [] as Facet[]),
    ]).then(([reposData, facetsData]) => {
      setRepos(reposData.filter((r) => !r.is_archived));
      setFacets(facetsData);
      setLoading(false);
    });
  }, []);

  const toggleRepo = (id: string) => {
    setSelectedRepoIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleAnalyze = async () => {
    if (selectedRepoIds.size === 0 || !selectedFacetId) return;
    setError("");
    setAnalyzing(true);
    try {
      const result = await githubImportApi.analyze(Array.from(selectedRepoIds), selectedFacetId);
      setGenerated(result.projects);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al analizar repositorios");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleConfirm = async () => {
    if (!generated || generated.length === 0) return;
    setError("");
    setConfirming(true);
    try {
      await githubImportApi.confirm(selectedFacetId, generated);
      router.push("/projects");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al importar proyectos");
      setConfirming(false);
    }
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Importar repositorios de GitHub</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Selecciona repositorios para importarlos como proyectos usando IA.
        </p>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive text-sm px-4 py-2 rounded-md">
          {error}
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">Faceta destino</label>
        <select
          value={selectedFacetId}
          onChange={(e) => setSelectedFacetId(e.target.value)}
          className="w-full border rounded-md px-3 py-2 text-sm bg-background"
        >
          <option value="">Seleccionar faceta...</option>
          {facets.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.slug})
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Repositorios vinculados</label>
        {repos.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No hay repositorios vinculados.{" "}
            <a href="/settings" className="text-primary hover:underline">Vincula repositorios</a>
          </p>
        ) : (
          <div className="border rounded-md divide-y">
            {repos.map((repo) => (
              <label
                key={repo.id}
                className="flex items-center gap-3 px-4 py-3 hover:bg-muted/50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedRepoIds.has(repo.id)}
                  onChange={() => toggleRepo(repo.id)}
                  className="shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{repo.full_name}</p>
                  {repo.description && (
                    <p className="text-xs text-muted-foreground truncate">{repo.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0">
                  <span>{repo.language}</span>
                  <span>★ {repo.stars}</span>
                </div>
              </label>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={handleAnalyze}
        disabled={selectedRepoIds.size === 0 || !selectedFacetId || analyzing}
        className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
      >
        {analyzing ? "Analizando..." : "Analizar con IA"}
      </button>

      {generated && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Vista previa</h2>
          {generated.map((project) => (
            <div key={project.repo_id} className="border rounded-md p-4 space-y-2">
              <h3 className="font-medium">{project.title}</h3>
              {project.description && (
                <p className="text-sm text-muted-foreground">{project.description}</p>
              )}
              <a
                href={project.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline block"
              >
                {project.github_url}
              </a>
              {project.markdown_content && (
                <details className="text-xs text-muted-foreground">
                  <summary className="cursor-pointer hover:text-foreground">
                    Ver contenido detallado
                  </summary>
                  <pre className="mt-2 whitespace-pre-wrap font-mono text-xs bg-muted p-3 rounded-md max-h-60 overflow-y-auto">
                    {project.markdown_content}
                  </pre>
                </details>
              )}
            </div>
          ))}

          <div className="flex gap-3">
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
            >
              {confirming ? "Importando..." : `Importar ${generated.length} proyecto(s)`}
            </button>
            <button
              onClick={() => setGenerated(null)}
              className="border px-4 py-2 rounded-md text-sm hover:bg-muted"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
