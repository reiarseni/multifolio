interface LinkExpiredProps {
  reason?: string;
}

export function LinkExpired({ reason }: LinkExpiredProps) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="w-full max-w-md p-8 space-y-6 bg-card rounded-lg shadow-lg text-center">
        <div className="text-6xl">🔒</div>
        <h1 className="text-2xl font-bold text-foreground">
          Link No Disponible
        </h1>
        <p className="text-sm text-muted-foreground">
          {reason || "Este link ha expirado o ya fue utilizado."}
        </p>
        <p className="text-xs text-muted-foreground">
          Contacta al propietario del portfolio para obtener un nuevo link.
        </p>
      </div>
    </div>
  );
}
