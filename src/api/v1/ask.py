from typing import List
from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_current_tenant
from src.core.embeddings import embedding_service
from src.core.llm import llm_service
from src.core.vector_store import vector_store
from src.models.query import AskRequest, AskResponse, Citation
from src.models.tenant import TenantContext

router = APIRouter(prefix="/ask", tags=["Conversational Q&A"])


@router.post(
    "",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Grounded question-answering with verifiable citations (for assistants & SOP Q&A)",
)
async def ask_question(
    payload: AskRequest,
    tenant: TenantContext = Depends(get_current_tenant),
):
    """Retrieve relevant contexts and synthesize a grounded answer."""
    query_vector = embedding_service.embed_query(payload.question)
    
    contexts = vector_store.search_tenant(
        tenant_id=tenant.tenant_id,
        query_vector=query_vector,
        limit=payload.limit,
        category_filter=payload.category_filter,
    )
    
    answer = llm_service.synthesize_answer(payload.question, contexts)
    
    citations: List[Citation] = [
        Citation(
            external_id=c.external_id,
            title=c.title,
            snippet=c.snippet,
            score=c.score,
            source_url=c.source_url,
        )
        for c in contexts
    ]
    
    return AskResponse(
        tenant_id=tenant.tenant_id,
        question=payload.question,
        answer=answer,
        citations=citations,
        grounded=len(contexts) > 0,
        model_used=llm_service.model,
    )
