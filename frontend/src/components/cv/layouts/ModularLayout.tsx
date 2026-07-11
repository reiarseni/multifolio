import type { PublicFacetResponse } from "@/lib/api/public";
import { CVHeader } from "@/components/cv/CVHeader";
import { CVSkills } from "@/components/cv/CVSkills";
import { OpenToRoleBadge } from "@/components/profile/OpenToRoleBadge";

export function ModularLayout({ data }: { data: PublicFacetResponse }) {
  return (
    <div
      className="max-w-4xl mx-auto p-6 space-y-6"
      style={{ backgroundColor: "var(--color-background, white)", fontFamily: "var(--font-body, inherit)" }}
    >
      <CVHeader data={data} />

      {data.open_to_role && data.open_to_role.status !== "not_available" && (
        <div className="mt-4">
          <OpenToRoleBadge
            status={data.open_to_role.status}
            role_type={data.open_to_role.role_type}
            modality={data.open_to_role.modality}
            location={data.open_to_role.location}
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.experiences.length > 0 && (
          <section
            className="border rounded-lg p-4"
            style={{ borderColor: "var(--color-border, currentColor)", borderRadius: "var(--radius-md, 0.5rem)", backgroundColor: "var(--color-surface, transparent)" }}
          >
            <h2 className="text-base font-semibold mb-3" style={{ color: "var(--color-text-heading, inherit)", fontFamily: "var(--font-heading, inherit)" }}>
              Experiencia
            </h2>
            <div className="space-y-3">
              {data.experiences.map((exp) => (
                <div key={exp.id}>
                  <p className="font-medium text-sm" style={{ color: "var(--color-text-heading, inherit)" }}>
                    {exp.position}
                  </p>
                  <p className="text-xs" style={{ color: "var(--color-text-muted, inherit)" }}>
                    {exp.company} · {exp.start_date}–{exp.is_current ? "Presente" : exp.end_date}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {data.educations.length > 0 && (
          <section
            className="border rounded-lg p-4"
            style={{ borderColor: "var(--color-border, currentColor)", borderRadius: "var(--radius-md, 0.5rem)", backgroundColor: "var(--color-surface, transparent)" }}
          >
            <h2 className="text-base font-semibold mb-3" style={{ color: "var(--color-text-heading, inherit)", fontFamily: "var(--font-heading, inherit)" }}>
              Educación
            </h2>
            <div className="space-y-3">
              {data.educations.map((edu) => (
                <div key={edu.id}>
                  <p className="font-medium text-sm" style={{ color: "var(--color-text-heading, inherit)" }}>
                    {edu.degree}
                  </p>
                  <p className="text-xs" style={{ color: "var(--color-text-muted, inherit)" }}>
                    {edu.institution} · {edu.start_date}–{edu.is_current ? "Presente" : edu.end_date}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      <CVSkills items={data.skills} />

      {data.projects.length > 0 && (
        <section>
          <h2 className="text-base font-semibold mb-3" style={{ color: "var(--color-text-heading, inherit)", fontFamily: "var(--font-heading, inherit)" }}>
            Proyectos
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {data.projects.map((p) => (
              <div
                key={p.id}
                className="border rounded-lg p-3"
                style={{ borderColor: "var(--color-border, currentColor)", borderRadius: "var(--radius-md, 0.5rem)", backgroundColor: "var(--color-surface, transparent)" }}
              >
                {p.cover_image_url && (
                  <img src={p.cover_image_url} alt={p.title} className="w-full aspect-video object-cover rounded mb-2" />
                )}
                <p className="font-medium text-sm" style={{ color: "var(--color-text-heading, inherit)" }}>
                  {p.title}
                </p>
                {p.description && (
                  <p className="text-xs line-clamp-2 mt-1" style={{ color: "var(--color-text-muted, inherit)" }}>
                    {p.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
