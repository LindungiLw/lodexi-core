from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    """Payload sent by tenant to ingest a document into CoreRAG."""
    
    external_id: str = Field(..., description="Unique ID from the client's own database (e.g., book_id or sop_number)")
    title: str = Field(..., description="Title of the document")
    content: str = Field(..., description="Full text or markdown content of the document")
    category: Optional[str] = Field(default=None, description="Optional category (e.g., 'buku-sejarah', 'sop-hrd')")
    source_url: Optional[str] = Field(default=None, description="Web link to original document or catalog page")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary custom client metadata")


class DocumentIngestResponse(BaseModel):
    """Response returned after processing and indexing document."""
    
    status: str = "indexed"
    tenant_id: str
    external_id: str
    title: str
    chunks_created: int
    point_ids: List[str]


class ChunkPayload(BaseModel):
    """Metadata payload stored alongside each vector point in Qdrant."""
    
    tenant_id: str
    external_id: str
    title: str
    chunk_index: int
    text: str
    category: Optional[str] = None
    source_url: Optional[str] = None
    client_metadata: Dict[str, Any] = Field(default_factory=dict)
