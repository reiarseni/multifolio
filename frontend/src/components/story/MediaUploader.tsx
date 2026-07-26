"use client";

import { useRef, useState } from "react";
import { storiesApi } from "@/lib/api/stories";

interface MediaUploaderProps {
  sectionId: string;
  onUpload: (url: string) => void;
}

export function MediaUploader({ sectionId, onUpload }: MediaUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const result = await storiesApi.uploadMedia(sectionId, file);
      onUpload(result.url);
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleUpload}
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="border rounded-md px-3 py-1 text-xs hover:bg-muted disabled:opacity-50"
      >
        {uploading ? "Subiendo..." : "Agregar imagen"}
      </button>
    </div>
  );
}
