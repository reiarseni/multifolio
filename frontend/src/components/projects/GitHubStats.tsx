import type { GitHubRepo } from "@/lib/api/github";

interface GitHubStatsProps {
  repo: GitHubRepo;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function GitHubStats({ repo }: GitHubStatsProps) {
  const languages = repo.languages ?? {};
  const langEntries = Object.entries(languages).sort((a, b) => b[1] - a[1]);

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <a
          href={repo.repo_url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium hover:underline"
        >
          {repo.full_name}
        </a>
        {repo.is_archived && (
          <span className="text-xs bg-muted px-2 py-0.5 rounded">Archivado</span>
        )}
      </div>

      {repo.description && (
        <p className="text-sm text-muted-foreground">{repo.description}</p>
      )}

      <div className="flex gap-4 text-sm">
        <span>⭐ {repo.stars}</span>
        <span>🍴 {repo.forks}</span>
        {repo.language && <span>📝 {repo.language}</span>}
      </div>

      {langEntries.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Lenguajes</p>
          <div className="flex gap-1 h-2 rounded-full overflow-hidden">
            {langEntries.slice(0, 5).map(([lang, pct]) => (
              <div
                key={lang}
                className="bg-primary"
                style={{ width: `${pct}%` }}
                title={`${lang}: ${pct}%`}
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            {langEntries.slice(0, 5).map(([lang, pct]) => (
              <span key={lang}>{lang} {pct}%</span>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-muted-foreground">
        Último commit: {formatDate(repo.last_commit)}
      </div>
    </div>
  );
}
