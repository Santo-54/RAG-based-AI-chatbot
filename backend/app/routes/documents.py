import logging
from fastapi import APIRouter, HTTPException, status
from typing import List
try:
    from app.models.schemas import DocumentCreate, DocumentCreateResponse, DocumentListResponse
    from app.services.rag import rag_service
except ModuleNotFoundError:
    from models.schemas import DocumentCreate, DocumentCreateResponse, DocumentListResponse
    from services.rag import rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("", response_model=DocumentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_document_endpoint(payload: DocumentCreate):
    """
    Ingest a text document. Generates local sentence embedding, and stores it in MongoDB.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text cannot be empty."
        )
        
    try:
        doc_id = rag_service.add_document(text=text, metadata=payload.metadata)
        return DocumentCreateResponse(id=doc_id, message="Document embedded and stored successfully.")
    except ConnectionError as ce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ce)
        )
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and store document: {str(e)}"
        )

@router.get("", response_model=List[DocumentListResponse])
async def list_documents_endpoint():
    """
    Fetch all stored document summaries (texts and metadata, excluding dense vector embeddings).
    """
    try:
        return rag_service.get_all_documents()
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document collection."
        )

@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_document_endpoint(doc_id: str):
    """
    Remove a document by its MongoDB ID.
    """
    try:
        success = rag_service.delete_document(doc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {doc_id} not found."
            )
        return {"message": f"Document {doc_id} deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the document: {str(e)}"
        )
