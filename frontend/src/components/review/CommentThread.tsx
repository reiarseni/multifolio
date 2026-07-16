"use client";

import { useState } from "react";
import { CommentForm } from "./CommentForm";
import type { Comment } from "@/lib/api/comments";

interface CommentThreadProps {
  comment: Comment;
  onReply: (parentId: string, data: { content: string; author_name?: string; author_email?: string }) => void;
  onResolve?: (commentId: string) => void;
  showActions?: boolean;
}

export function CommentThread({ comment, onReply, onResolve, showActions }: CommentThreadProps) {
  const [showReply, setShowReply] = useState(false);

  return (
    <div className="border rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{comment.author_name || "Anónimo"}</span>
        <span>{new Date(comment.created_at).toLocaleDateString("es-ES")}</span>
      </div>
      <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
      {comment.section_ref && (
        <span className="text-xs bg-muted px-1.5 py-0.5 rounded">
          Sección: {comment.section_ref}
        </span>
      )}
      <div className="flex gap-2 text-xs">
        {showActions && (
          <>
            <button onClick={() => setShowReply(!showReply)} className="text-primary hover:underline">
              {showReply ? "Cancelar" : "Responder"}
            </button>
            {onResolve && comment.status === "pending" && (
              <button onClick={() => onResolve(comment.id)} className="text-green-600 hover:underline">
                Resolver
              </button>
            )}
          </>
        )}
      </div>

      {showReply && (
        <div className="ml-4 mt-2">
          <CommentForm
            parentId={comment.id}
            placeholder="Escribe tu respuesta..."
            onSubmit={(data) => {
              onReply(comment.id, data);
              setShowReply(false);
            }}
          />
        </div>
      )}

      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-4 space-y-2 mt-2 border-l-2 pl-3">
          {comment.replies.map((reply) => (
            <CommentThread
              key={reply.id}
              comment={reply}
              onReply={onReply}
              showActions={showActions}
            />
          ))}
        </div>
      )}
    </div>
  );
}
