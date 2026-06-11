import type { PublicExperience } from "@/lib/api/public";

export function CVExperience({ items }: { items: PublicExperience[] }) {
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
        Experiencia
      </h2>
      <div className="space-y-4">
        {items.map((exp) => (
          <div key={exp.id}>
            <div className="flex justify-between items-start">
              <div>
                <p className="font-medium" style={{ color: "var(--color-text-heading, inherit)" }}>
                  {exp.position}
                </p>
                <p className="text-sm" style={{ color: "var(--color-text-muted, inherit)" }}>
                  {exp.company}
                </p>
              </div>
              <p className="text-xs shrink-0 ml-4" style={{ color: "var(--color-text-muted, inherit)" }}>
                {exp.start_date} - {exp.is_current ? "Presente" : exp.end_date}
              </p>
            </div>
            {exp.description && (
              <p className="text-sm mt-1" style={{ color: "var(--color-text-body, inherit)", fontFamily: "var(--font-body, inherit)" }}>
                {exp.description}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
