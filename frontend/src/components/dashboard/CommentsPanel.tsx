"use client";

import { useEffect, useState } from "react";
import { commentsApi } from "@/lib/api/comments";
import type { Comment } from "@/lib/api/comments";

interface CommentsPanelProps {
  facetId: string;
}

export function CommentsPanel({ facetId }: CommentsPanelProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [commentsData, unreadData] = await Promise.all([
          commentsApi.listByFacet(facetId),
          commentsApi.getUnreadCount(),
        ]);
        setComments(commentsData);
        setUnreadCount(unreadData.count);
      } catch {
        // silently ignore
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [facetId]);

  const handleResolve = async (commentId: string) => {
    try {
      await commentsApi.resolve(commentId);
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId ? { ...c, status: "resolved" } : c
        )
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {
      // silently ignore
    }
  };

  const rootComments = comments.filter((c) => !c.parent_id);
  const pendingComments = comments.filter((c) => c.status === "pending");

  if (loading) {
    return <p className="text-sm text-muted-foreground">Cargando comentarios...</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Comentarios</h3>
        {unreadCount > 0 && (
          <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">
            {unreadCount} pendientes
          </span>
        )}
      </div>

      {comments.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No hay comentarios aún. Compartí tu link de revisión para recibir feedback.
        </p>
      ) : (
        <div className="space-y-2 text-sm">
          {pendingComments.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">
                Pendientes ({pendingComments.length})
              </p>
              {pendingComments.map((comment) => (
                <div key={comment.id} className="border rounded p-2 mb-2">
                  <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                    <span>{comment.author_name || "Anónimo"}</span>
                    <span>{new Date(comment.created_at).toLocaleDateString("es-ES")}</span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
                  {comment.section_ref && (
                    <span className="text-xs bg-muted px-1 py-0.5 rounded inline-block mt-1">
                      Sección: {comment.section_ref}
                    </span>
                  )}
                  <div className="flex gap-2 mt-1">
                    <button
                      onClick={() => handleResolve(comment.id)}
                      className="text-xs text-green-600 hover:underline"
                    >
                      Marcar resuelto
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {rootComments
            .filter((c) => c.status === "resolved")
            .slice(0, 5)
            .map((comment) => (
              <div key={comment.id} className="border rounded p-2 opacity-60">
                <div className="text-xs text-muted-foreground mb-1">
                  <span>{comment.author_name || "Anónimo"}</span>
                  <span className="ml-2">✓ Resuelto</span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

export function CommentsBadge({ facetId }: { facetId: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    commentsApi.getUnreadCount().then((data) => {
      setCount(data.count);
    }).catch(() => {});
  }, [facetId]);

  if (count === 0) return null;

  return (
    <span className="inline-flex items-center justify-center w-5 h-5 text-[10px] font-medium rounded-full bg-destructive text-destructive-foreground">
      {count}
    </span>
  );
}
