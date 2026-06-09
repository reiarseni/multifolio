import type { PublicFacetResponse } from "@/lib/api/public";

export function CVHeader({ data }: { data: PublicFacetResponse }) {
  return (
    <header className="flex items-start gap-6 mb-8">
      {data.photo_url && (
        <img
          src={data.photo_url}
          alt={data.full_name}
          className="w-24 h-24 rounded-full object-cover"
        />
      )}
      <div className="flex-1">
        <h1 className="text-2xl font-bold">{data.full_name}</h1>
        {data.title && <p className="text-lg text-muted-foreground">{data.title}</p>}
        {data.bio && <p className="text-sm mt-2">{data.bio}</p>}
        <div className="flex gap-4 mt-3 text-sm text-muted-foreground">
          {data.email && <span>{data.email}</span>}
          {data.phone && <span>{data.phone}</span>}
          {data.website && (
            <a href={data.website} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              {data.website}
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
