"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface CommentFormProps {
  onSubmit: (data: { content: string; author_name?: string; author_email?: string; parent_id?: string }) => void;
  parentId?: string;
  placeholder?: string;
}

export function CommentForm({ onSubmit, parentId, placeholder = "Escribe un comentario..." }: CommentFormProps) {
  const [content, setContent] = useState("");
  const [authorName, setAuthorName] = useState("");
  const [authorEmail, setAuthorEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit({
      content: content.trim(),
      author_name: authorName.trim() || undefined,
      author_email: authorEmail.trim() || undefined,
      parent_id: parentId,
    });
    setContent("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={placeholder}
        className="w-full p-2 rounded bg-background border min-h-[80px] resize-y text-sm"
      />
      <div className="flex gap-2">
        <input
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
          placeholder="Tu nombre (opcional)"
          className="flex-1 p-1.5 rounded bg-background border text-sm"
        />
        <input
          value={authorEmail}
          onChange={(e) => setAuthorEmail(e.target.value)}
          placeholder="Tu email (opcional)"
          className="flex-1 p-1.5 rounded bg-background border text-sm"
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit" size="sm" disabled={!content.trim()}>
          {parentId ? "Responder" : "Comentar"}
        </Button>
      </div>
    </form>
  );
}
