"""
Idempotent superadmin seeder.

Crea el superadmin si no existe; actualiza su contraseña si ya está.
Credenciales vía env:
  SUPERADMIN_EMAIL     (default: admin@multifolio.dev)
  SUPERADMIN_PASSWORD  (default: admin1234)

Uso:
  docker compose exec api seed-admin
  uv run seed-admin          # local, con .env cargado
"""
import asyncio
import os

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.user import User

_EMAIL = os.getenv("SUPERADMIN_EMAIL", "admin@multifolio.dev")
_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "admin1234")


async def _seed() -> None:
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == _EMAIL))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = hash_password(_PASSWORD)
            await db.commit()
            print(f"[seed-admin] contraseña actualizada → {_EMAIL}")
        else:
            db.add(User(email=_EMAIL, hashed_password=hash_password(_PASSWORD)))
            await db.commit()
            print(f"[seed-admin] superadmin creado → {_EMAIL}")


def main() -> None:
    asyncio.run(_seed())


if __name__ == "__main__":
    main()
