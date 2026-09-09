from fastapi import Security
from fastapi.security import APIKeyHeader
from src.core.security import authenticate_api_key
from src.models.tenant import TenantContext

# Extracts 'X-API-Key' from HTTP request headers
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_tenant(
    api_key: str = Security(api_key_header),
) -> TenantContext:
    """Dependency that extracts and validates the tenant from the API key."""
    return authenticate_api_key(api_key)
