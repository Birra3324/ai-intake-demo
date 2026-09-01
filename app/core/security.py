"""API key auth for mutating (and list) endpoints. Health stays public."""

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    expected = get_settings().api_key
    if not expected:
        # Local demo with no key configured — allow, but callers should set one.
        return ""
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key
