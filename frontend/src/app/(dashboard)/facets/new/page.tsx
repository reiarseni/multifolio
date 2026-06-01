"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { FacetForm } from "@/components/forms/FacetForm";
import { facetsApi } from "@/lib/api/facets";

export default function NewFacetPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);

  const handleSave = async (data: Parameters<typeof facetsApi.create>[0]) => {
    setSaving(true);
    await facetsApi.create(data);
    router.push("/facets");
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Nueva faceta</h1>
      <FacetForm onSave={handleSave} saving={saving} />
    </div>
  );
}
