import logging
from fastapi import APIRouter, HTTPException, status
try:
    from app.models.schemas import ChatRequest, ChatResponse, ContextSource
    from app.services.rag import rag_service
    from app.services.mistral import mistral_service
except ModuleNotFoundError:
    from models.schemas import ChatRequest, ChatResponse, ContextSource
    from services.rag import rag_service
    from services.mistral import mistral_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Core RAG Chat endpoint. Runs query through the RAG pipeline, constructs the 
    contextualized prompt, calls the Mistral AI model, and returns the response with sources.
    """
    query = payload.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Query content cannot be empty."
        )

    try:
        logger.info(f"Received chat request: '{query}'")
        
        # Step 1 & 2: Search MongoDB vector space for top 3 documents
        retrieved_docs = rag_service.retrieve_documents(query, top_k=3)
        
        # Step 3: Prompt Construction
        if retrieved_docs:
            context_text = "\n\n".join([f"Context document {i+1}:\n{doc['text']}" for i, doc in enumerate(retrieved_docs)])
        else:
            context_text = "No context documents are currently stored in the vector database."
            
        final_prompt = f"""You are a helpful AI assistant.

Use the following context to answer:

{context_text}

User:
{query}

Answer clearly and naturally."""

        logger.debug(f"Constructed RAG prompt:\n{final_prompt}")

        # Step 4: Call Mistral API
        llm_response = mistral_service.generate_response(final_prompt)
        
        # Map source documents to response schema
        sources = [
            ContextSource(
                id=doc["id"], 
                text=doc["text"], 
                score=doc["score"],
                metadata=doc.get("metadata")
            ) for doc in retrieved_docs
        ]

        return ChatResponse(response=llm_response, context=sources)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while executing the RAG pipeline: {str(e)}"
        )
