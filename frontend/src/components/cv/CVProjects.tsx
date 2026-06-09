import Link from "next/link";
import type { PublicProject } from "@/lib/api/public";

export function CVProjects({ items }: { items: PublicProject[] }) {
  if (items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold border-b pb-1 mb-3">Proyectos</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((project) => (
          <div key={project.id} className="border rounded-md p-4 space-y-2">
            {project.cover_image_url && (
              <img
                src={project.cover_image_url}
                alt={project.title}
                className="w-full rounded object-cover aspect-video"
              />
            )}
            <p className="font-medium">{project.title}</p>
            {project.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">{project.description}</p>
            )}
            <Link
              href={`/projects/${project.id}`}
              className="text-sm text-primary hover:underline inline-block"
            >
              Ver detalle →
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}
