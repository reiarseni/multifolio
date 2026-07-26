"use client";

import { useEffect, useState } from "react";
import { CommentForm } from "@/components/review/CommentForm";
import { CommentThread } from "@/components/review/CommentThread";
import { reviewLinksApi, commentsApi } from "@/lib/api/comments";
import type { Comment, ReviewLink } from "@/lib/api/comments";

export default function ReviewPage({ params }: { params: Promise<{ token: string }> }) {
  const [token, setToken] = useState<string | null>(null);
  const [link, setLink] = useState<ReviewLink | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setToken(p.token));
  }, [params]);

  useEffect(() => {
    if (!token) return;
    const fetchData = async () => {
      try {
        const linkData = await reviewLinksApi.validate(token);
        setLink(linkData);
        const commentsData = await commentsApi.listByToken(token);
        setComments(commentsData);
      } catch {
        setError("Link inválido o expirado");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  const handleNewComment = async (data: { content: string; author_name?: string; author_email?: string }) => {
    if (!token) return;
    try {
      const newComment = await commentsApi.createByToken(token, data);
      setComments((prev) => [...prev, newComment]);
    } catch {
      setError("Error al crear comentario");
    }
  };

  const handleReply = async (parentId: string, data: { content: string; author_name?: string; author_email?: string }) => {
    if (!token) return;
    try {
      const reply = await commentsApi.createByToken(token, { ...data, parent_id: parentId });
      setComments((prev) => [...prev, reply]);
    } catch {
      setError("Error al responder");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Cargando...</p>
      </div>
    );
  }

  if (error || !link) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-2">
          <h1 className="text-xl font-bold">Link inválido</h1>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  const rootComments = comments.filter((c) => !c.parent_id);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-6">
        <header className="mb-6">
          <h1 className="text-lg font-semibold">Modo Revisión</h1>
          <p className="text-sm text-muted-foreground">
            Deja tus comentarios sobre esta faceta
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="border rounded-lg p-6">
              <p className="text-muted-foreground">
                Contenido de la faceta disponible próximamente.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <h2 className="text-sm font-medium mb-3">Deja tu comentario</h2>
              <CommentForm onSubmit={handleNewComment} />
            </div>

            <div className="space-y-3">
              <h2 className="text-sm font-medium">
                Comentarios ({comments.length})
              </h2>
              {rootComments.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No hay comentarios aún. Sé el primero en dejar feedback.
                </p>
              ) : (
                rootComments.map((comment) => (
                  <CommentThread
                    key={comment.id}
                    comment={comment}
                    onReply={handleReply}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
