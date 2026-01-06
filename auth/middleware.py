from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware


class AuthPlaceholderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Placeholder para autenticação futura.
        return await call_next(request)
