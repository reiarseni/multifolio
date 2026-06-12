import type { PublicEducation } from "@/lib/api/public";

export function CVEducation({ items }: { items: PublicEducation[] }) {
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
        Educación
      </h2>
      <div className="space-y-4">
        {items.map((edu) => (
          <div key={edu.id}>
            <p className="font-medium" style={{ color: "var(--color-text-heading, inherit)" }}>
              {edu.degree}
            </p>
            <p className="text-sm" style={{ color: "var(--color-text-muted, inherit)" }}>
              {edu.institution}
            </p>
            {edu.field && (
              <p className="text-sm" style={{ color: "var(--color-text-body, inherit)" }}>
                {edu.field}
              </p>
            )}
            <p className="text-xs" style={{ color: "var(--color-text-muted, inherit)" }}>
              {edu.start_date} - {edu.is_current ? "Presente" : edu.end_date}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
