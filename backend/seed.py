import sys
import os

# Add parent directory to sys.path so we can import app services
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging
try:
    from app.services.rag import rag_service
except ModuleNotFoundError:
    from services.rag import rag_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

SAMPLE_DOCUMENTS = [
    {
        "text": "Mistral AI is a prominent French artificial intelligence company founded in April 2023 by former researchers from Meta and Google DeepMind. It is renowned for creating highly efficient, open-weight language models such as Mistral 7B, Mixtral 8x7B, and commercial systems like Mistral Large and Mistral Small.",
        "metadata": {"category": "AI Company", "source": "mistral_wiki"}
    },
    {
        "text": "FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. Built on top of Starlette and Pydantic, FastAPI is extremely fast, reduces code duplication, and automatically generates interactive Swagger UI documentation.",
        "metadata": {"category": "Web Framework", "source": "fastapi_docs"}
    },
    {
        "text": "The sentence-transformers Python library provides state-of-the-art methods for generating dense vector embeddings for sentences, paragraphs, and images. The pre-trained model 'all-MiniLM-L6-v2' embeds text into a 384-dimensional space, making it highly optimized for local semantic search and clustering.",
        "metadata": {"category": "Machine Learning", "source": "sbert_home"}
    },
    {
        "text": "MongoDB is a leading document-oriented, NoSQL database designed for high scalability and flexibility. It stores data in flexible, JSON-like BSON documents. Standard MongoDB is widely used to store text elements along with dense vectors, allowing custom applications to perform extremely rapid cosine similarity searches.",
        "metadata": {"category": "Database", "source": "mongodb_manual"}
    },
    {
        "text": "Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by retrieving relevant documents from an external custom database (e.g. vector search) based on the user's query, appending this context to the prompt, and feeding it to the LLM to prevent hallucinations.",
        "metadata": {"category": "AI Architecture", "source": "rag_primer"}
    }
]

def seed_database():
    logger.info("Starting database seeding process...")
    
    if not rag_service.collection:
        logger.error("Could not establish a database connection. Please check that MongoDB is running and MONGO_URI is configured correctly in .env.")
        sys.exit(1)

    try:
        # Check existing documents count
        existing_count = rag_service.collection.count_documents({})
        logger.info(f"Database currently contains {existing_count} documents.")
        
        # We can ask to clear first or just insert if empty
        if existing_count > 0:
            logger.info("Clearing existing documents in collection for a clean seed...")
            rag_service.collection.delete_many({})
            logger.info("Collection cleared.")

        logger.info("Embedding and inserting sample documents...")
        for i, doc in enumerate(SAMPLE_DOCUMENTS):
            logger.info(f"Embedding document {i+1}/{len(SAMPLE_DOCUMENTS)}...")
            doc_id = rag_service.add_document(text=doc["text"], metadata=doc["metadata"])
            logger.info(f"Inserted document with ID: {doc_id}")

        logger.info("Seeding process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error occurred during database seeding: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    seed_database()
