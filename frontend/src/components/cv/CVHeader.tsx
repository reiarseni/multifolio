import type { PublicFacetResponse } from "@/lib/api/public";

const PHOTO_SHAPE_CLASS: Record<string, string> = {
  circle: "rounded-full",
  rounded: "rounded-xl",
  square: "rounded-none",
};

export function CVHeader({ data }: { data: PublicFacetResponse }) {
  const shapeClass = PHOTO_SHAPE_CLASS[data.photo_shape ?? "circle"] ?? "rounded-full";

  return (
    <header className="flex items-start gap-6 mb-8">
      {data.show_photo_web !== false && data.photo_url && (
        <img
          src={data.photo_url}
          alt={data.full_name}
          className={`w-24 h-24 object-cover shrink-0 ${shapeClass}`}
        />
      )}
      <div className="flex-1">
        <h1
          className="text-2xl font-bold"
          style={{ fontFamily: "var(--font-heading, inherit)", color: "var(--color-text-heading, inherit)" }}
        >
          {data.full_name}
        </h1>
        {data.title && (
          <p className="text-lg" style={{ color: "var(--color-primary, inherit)" }}>
            {data.title}
          </p>
        )}
        {data.bio && (
          <p className="text-sm mt-2" style={{ color: "var(--color-text-body, inherit)", fontFamily: "var(--font-body, inherit)" }}>
            {data.bio}
          </p>
        )}
        <div className="flex flex-wrap gap-4 mt-3 text-sm" style={{ color: "var(--color-text-muted, inherit)" }}>
          {data.email && <span>{data.email}</span>}
          {data.phone && <span>{data.phone}</span>}
          {data.website && (
            <a
              href={data.website}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
              style={{ color: "var(--color-accent, var(--color-primary, inherit))" }}
            >
              {data.website}
            </a>
          )}
          {data.linkedin_url && (
            <a
              href={data.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
              style={{ color: "var(--color-accent, var(--color-primary, inherit))" }}
            >
              LinkedIn
            </a>
          )}
          {data.github_url && (
            <a
              href={data.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
              style={{ color: "var(--color-accent, var(--color-primary, inherit))" }}
            >
              GitHub
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
