"""JWT validation using shared secret from Better Auth."""

from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings

security = HTTPBearer()


@dataclass
class CurrentUser:
    """Authenticated user from JWT."""

    id: str
    email: str


def decode_jwt(token: str) -> dict:
    """
    Decode and validate JWT using shared secret (HS256).

    Raises:
        HTTPException(401): If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
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
