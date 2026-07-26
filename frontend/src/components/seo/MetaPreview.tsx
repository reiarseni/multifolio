"use client";

interface MetaPreviewProps {
  title: string;
  description: string;
  url?: string;
}

export function MetaPreview({ title, description, url = "micv.com/backend-developer" }: MetaPreviewProps) {
  return (
    <div className="border rounded-lg p-4 bg-white max-w-lg">
      <p className="text-xs text-gray-600 mb-1">Vista previa de resultado de búsqueda:</p>
      <div className="space-y-1">
        <p className="text-[#1a0dab] text-lg leading-snug hover:underline cursor-pointer truncate">
          {title || "Meta Título"}
        </p>
        <p className="text-[#006621] text-sm truncate">
          {url}
        </p>
        <p className="text-[#545454] text-sm leading-snug line-clamp-2">
          {description || "Meta descripción"}
        </p>
      </div>
    </div>
  );
}
