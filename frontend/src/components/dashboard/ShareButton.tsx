"use client";

import { useState } from "react";

export function ShareButton({ url, label = "Copiar link" }: { url: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="text-sm text-primary hover:underline"
    >
      {copied ? "¡Copiado!" : label}
    </button>
  );
}
