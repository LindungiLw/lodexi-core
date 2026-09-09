from pydantic import BaseModel, Field


class TenantContext(BaseModel):
    """Context of the authenticated tenant resolved from API Key."""
    
    tenant_id: str = Field(..., description="Unique identifier for the tenant (e.g., jiulibrary, staff_portal)")
    api_key_prefix: str = Field(..., description="Obfuscated key prefix for auditing")
    is_active: bool = Field(default=True, description="Tenant operational status")
