import type { PublicProject } from "@/lib/api/public";

export function CVProjects({ items }: { items: PublicProject[] }) {
  if (items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2
        className="text-lg font-semibold border-b pb-1 mb-3"
        style={{
          color: "var(--color-text-heading, inherit)",
          borderColor: "var(--color-border, currentColor)",
          fontFamily: "var(--font-heading, inherit)",
        }}
      >
        Proyectos
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((project) => (
          <div
            key={project.id}
            className="border rounded-md p-4 space-y-2"
            style={{
              borderColor: "var(--color-border, currentColor)",
              backgroundColor: "var(--color-surface, transparent)",
              borderRadius: "var(--radius-md, 0.375rem)",
            }}
          >
            {project.cover_image_url && (
              <img
                src={project.cover_image_url}
                alt={project.title}
                className="w-full rounded object-cover aspect-video"
              />
            )}
            <p className="font-medium" style={{ color: "var(--color-text-heading, inherit)" }}>
              {project.title}
            </p>
            {project.description && (
              <p className="text-sm line-clamp-2" style={{ color: "var(--color-text-muted, inherit)" }}>
                {project.description}
              </p>
            )}
            <div className="flex gap-3 text-sm">
              {project.github_url && (
                <a
                  href={project.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                  style={{ color: "var(--color-accent, var(--color-primary, inherit))" }}
                >
                  Repositorio →
                </a>
              )}
              {project.live_url && (
                <a
                  href={project.live_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                  style={{ color: "var(--color-accent, var(--color-primary, inherit))" }}
                >
                  Demo →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
