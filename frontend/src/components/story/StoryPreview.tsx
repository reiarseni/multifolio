import type { StorySection } from "@/lib/api/stories";

interface StoryPreviewProps {
  sections: StorySection[];
}

export function StoryPreview({ sections }: StoryPreviewProps) {
  const visibleSections = sections
    .filter((s) => s.is_visible)
    .sort((a, b) => a.order - b.order);

  if (visibleSections.length === 0) {
    return (
      <div className="text-muted-foreground text-sm">
        No hay secciones visibles en la historia.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {visibleSections.map((section) => (
        <section key={section.id} className="space-y-3">
          <h3
            className="text-lg font-semibold"
            style={{ color: "var(--color-text-heading, inherit)" }}
          >
            {section.title}
          </h3>
          {section.content && (
            <div
              className="prose prose-sm max-w-none"
              style={{ color: "var(--color-text-body, inherit)" }}
            >
              {section.content.split("\n").map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          )}
          {section.media_urls && section.media_urls.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {section.media_urls.map((url, idx) => (
                <div key={idx}>
                  {url.includes("youtube.com") || url.includes("vimeo.com") ? (
                    <div className="aspect-video w-full max-w-md">
                      <iframe
                        src={url}
                        className="w-full h-full rounded-lg"
                        allowFullScreen
                      />
                    </div>
                  ) : (
                    <img
                      src={url}
                      alt={`${section.title} - ${idx + 1}`}
                      className="rounded-lg max-w-md"
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
