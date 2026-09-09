from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_current_tenant
from src.core.embeddings import embedding_service
from src.core.vector_store import vector_store
from src.models.query import SearchRequest, SearchResponse
from src.models.tenant import TenantContext

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic vector retrieval without LLM synthesis (for catalogs & search bars)",
)
async def semantic_search(
    payload: SearchRequest,
    tenant: TenantContext = Depends(get_current_tenant),
):
    """Retrieve ranked chunks matching user query within the authenticated tenant's space."""
    query_vector = embedding_service.embed_query(payload.query)
    
    results = vector_store.search_tenant(
        tenant_id=tenant.tenant_id,
        query_vector=query_vector,
        limit=payload.limit,
        category_filter=payload.category_filter,
        min_score=payload.min_score,
    )
    
    return SearchResponse(
        tenant_id=tenant.tenant_id,
        query=payload.query,
        total_found=len(results),
        results=results,
    )
