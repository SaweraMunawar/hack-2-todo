"""JWT validation using JWKS from Better Auth."""

from dataclasses import dataclass
from functools import lru_cache

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings

security = HTTPBearer()


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    """Lazily create JWKS client on first use."""
    return PyJWKClient(
        f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
        cache_keys=True,
        lifespan=3600,
    )


@dataclass
class CurrentUser:
    """Authenticated user from JWT."""

    id: str
    email: str


def decode_jwt(token: str) -> dict:
    """
    Decode and validate JWT using JWKS from Better Auth.

    Raises:
        HTTPException(401): If token is invalid
    """
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "ES256", "RS256"],
            audience=settings.BETTER_AUTH_URL,
            issuer=settings.BETTER_AUTH_URL,
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {e}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> CurrentUser:
    """
    FastAPI dependency to extract and validate JWT.

    Usage:
        @app.get("/tasks")
        async def list_tasks(user: CurrentUser = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    payload = decode_jwt(token)

    return CurrentUser(
        id=payload["sub"],
        email=payload.get("email", ""),
    )
