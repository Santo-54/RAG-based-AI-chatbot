import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("app.main")

# Preload local model during startup to ensure no latency on first query
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Starting RAG Chatbot Backend ===")
    try:
        try:
            from app.services.embedding import embedding_service
        except ModuleNotFoundError:
            from services.embedding import embedding_service
        logger.info("Initializing Local Embeddings Model on startup...")
        # Accessing embedding_service triggers singleton initialization
        _ = embedding_service
        logger.info("Embeddings model loaded and ready.")
    except Exception as e:
        logger.error(f"Failed to load embeddings model at startup: {e}", exc_info=True)
    
    yield
    logger.info("=== Shutting Down RAG Chatbot Backend ===")

app = FastAPI(
    title="RAG Chatbot Backend",
    description="Vector-based Retrieval Augmented Generation Chatbot using local sentence-transformers, MongoDB, and Mistral AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
# React default ports are usually 5173 (Vite) or 3000 (Create React App)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain e.g., ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and mount routers
try:
    from app.routes.chat import router as chat_router
    from app.routes.documents import router as doc_router
except ModuleNotFoundError:
    from routes.chat import router as chat_router
    from routes.documents import router as doc_router

app.include_router(chat_router)
app.include_router(doc_router)

@app.get("/", tags=["Health"])
async def root_health_check():
    """
    General service health check endpoint displaying status of dependencies.
    """
    try:
        from app.services.rag import rag_service
        from app.services.mistral import mistral_service
    except ModuleNotFoundError:
        from services.rag import rag_service
        from services.mistral import mistral_service

    # Check MongoDB connectivity
    mongo_connected = False
    db_error = None
    if rag_service.collection is not None:
        try:
            rag_service.client.server_info()
            mongo_connected = True
        except Exception as e:
            db_error = str(e)
    
    # Check if Mistral API key is set
    mistral_configured = (
        mistral_service.api_key is not None 
        and mistral_service.api_key != "your_mistral_api_key" 
        and len(mistral_service.api_key) > 5
    )

    return {
        "status": "healthy" if mongo_connected else "degraded",
        "services": {
            "embeddings": {
                "model": "all-MiniLM-L6-v2",
                "dimensions": 384,
                "status": "loaded"
            },
            "database": {
                "connected": mongo_connected,
                "db_name": rag_service.db_name,
                "collection": rag_service.collection_name,
                "error": db_error
            },
            "mistral_llm": {
                "configured": mistral_configured,
                "model": "mistral-small"
            }
        }
    }
