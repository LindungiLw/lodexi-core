from typing import List
from fastapi import APIRouter, Depends, status
from src.api.dependencies import get_current_tenant
from src.core.embeddings import embedding_service
from src.core.vector_store import vector_store
from src.models.document import DocumentIngestRequest, DocumentIngestResponse
from src.models.tenant import TenantContext

router = APIRouter(prefix="/documents", tags=["Documents Ingestion"])


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into manageable, overlapping paragraphs/chunks."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
            
    if current_chunk:
        chunks.append(current_chunk)
        
    # Fallback if no paragraph breaks existed
    if not chunks and text.strip():
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
                
    return chunks or [text.strip()]


@router.post(
    "",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a document into the tenant's isolated knowledge base",
)
async def ingest_document(
    payload: DocumentIngestRequest,
    tenant: TenantContext = Depends(get_current_tenant),
):
    """Chunk, embed, and store document under the authenticated tenant's namespace."""
    chunks = chunk_text(payload.content)
    embeddings = embedding_service.embed_texts(chunks)
    
    point_ids = vector_store.upsert_chunks(
        tenant_id=tenant.tenant_id,
        external_id=payload.external_id,
        title=payload.title,
        chunks=chunks,
        embeddings=embeddings,
        category=payload.category,
        source_url=payload.source_url,
        client_metadata=payload.metadata,
    )
    
    return DocumentIngestResponse(
        status="indexed",
        tenant_id=tenant.tenant_id,
        external_id=payload.external_id,
        title=payload.title,
        chunks_created=len(chunks),
        point_ids=point_ids,
    )


@router.delete(
    "/{external_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document from the tenant's partition",
)
async def delete_document(
    external_id: str,
    tenant: TenantContext = Depends(get_current_tenant),
):
    """Remove all vectors belonging to this external_id inside the tenant's partition."""
    vector_store.delete_document(tenant_id=tenant.tenant_id, external_id=external_id)
    return {
        "status": "deleted",
        "tenant_id": tenant.tenant_id,
        "external_id": external_id,
    }
