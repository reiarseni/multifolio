from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.deps import get_redis


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(
        self,
        request: Request,
        redis: Redis = Depends(get_redis),
    ) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{client_ip}"

        current = await redis.get(key)
        count = int(current) if current else 0

        if count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Intenta de nuevo en breve.",
                headers={"Retry-After": str(self.window_seconds)},
            )

        await redis.incr(key)
        await redis.expire(key, self.window_seconds)
