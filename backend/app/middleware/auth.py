from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    - Authorization: Bearer <JWT> があれば decode して request.state.user_id に入れる
    - protected_paths に一致する場合、未認証なら 401
    """

    def __init__(self, app, protected_paths: set[str] | None = None):
        super().__init__(app)
        self.protected_paths = protected_paths or set()

    async def dispatch(self, request: Request, call_next):
        user_id = None
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                user_id = decode_access_token(token)
            except Exception:
                user_id = None

        request.state.user_id = user_id

        if request.url.path in self.protected_paths and user_id is None:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        return await call_next(request)

