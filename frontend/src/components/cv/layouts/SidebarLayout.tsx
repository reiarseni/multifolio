import type { PublicFacetResponse } from "@/lib/api/public";
import { CVExperience } from "@/components/cv/CVExperience";
import { CVEducation } from "@/components/cv/CVEducation";
import { CVProjects } from "@/components/cv/CVProjects";
import { OpenToRoleBadge } from "@/components/profile/OpenToRoleBadge";

const PHOTO_SHAPE_CLASS: Record<string, string> = {
  circle: "rounded-full",
  rounded: "rounded-xl",
  square: "rounded-none",
};

export function SidebarLayout({ data }: { data: PublicFacetResponse }) {
  const shapeClass = PHOTO_SHAPE_CLASS[data.photo_shape ?? "circle"] ?? "rounded-full";

  return (
    <div
      className="max-w-4xl mx-auto p-6 flex gap-8"
      style={{ backgroundColor: "var(--color-background, white)", fontFamily: "var(--font-body, inherit)" }}
    >
      {/* Sidebar */}
      <aside
        className="w-64 shrink-0 space-y-6"
        style={{ backgroundColor: "var(--color-surface, transparent)", borderRadius: "var(--radius-md, 0.25rem)", padding: "1rem" }}
      >
        {data.show_photo_web !== false && data.photo_url && (
          <img
            src={data.photo_url}
            alt={data.full_name}
            className={`w-32 h-32 object-cover mx-auto ${shapeClass}`}
          />
        )}
        <div>
          <h1
            className="text-xl font-bold text-center"
            style={{ color: "var(--color-text-heading, inherit)", fontFamily: "var(--font-heading, inherit)" }}
          >
            {data.full_name}
          </h1>
          {data.title && (
            <p className="text-sm text-center mt-1" style={{ color: "var(--color-primary, inherit)" }}>
              {data.title}
            </p>
          )}
        </div>

        <div className="space-y-1 text-sm" style={{ color: "var(--color-text-muted, inherit)" }}>
          {data.email && <p>{data.email}</p>}
          {data.phone && <p>{data.phone}</p>}
          {data.website && (
            <a href={data.website} target="_blank" rel="noopener noreferrer" className="hover:underline block" style={{ color: "var(--color-accent, inherit)" }}>
              {data.website}
            </a>
          )}
        </div>

        {data.skills.length > 0 && (
          <div>
            <h2
              className="text-sm font-semibold mb-2 border-b pb-1"
              style={{ color: "var(--color-text-heading, inherit)", borderColor: "var(--color-border, currentColor)" }}
            >
              Habilidades
            </h2>
            <div className="flex flex-col gap-1">
              {data.skills.map((s) => (
                <span key={s.id} className="text-sm" style={{ color: "var(--color-text-body, inherit)" }}>
                  {s.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.open_to_role && data.open_to_role.status !== "not_available" && (
          <div>
            <h2
              className="text-sm font-semibold mb-2 border-b pb-1"
              style={{ color: "var(--color-text-heading, inherit)", borderColor: "var(--color-border, currentColor)" }}
            >
              Disponibilidad
            </h2>
            <OpenToRoleBadge
              status={data.open_to_role.status}
              role_type={data.open_to_role.role_type}
              modality={data.open_to_role.modality}
              location={data.open_to_role.location}
            />
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1">
        {data.bio && (
          <p className="text-sm mb-6" style={{ color: "var(--color-text-body, inherit)" }}>
            {data.bio}
          </p>
        )}
        <CVExperience items={data.experiences} />
        <CVEducation items={data.educations} />
        <CVProjects items={data.projects} />
      </main>
    </div>
  );
}
