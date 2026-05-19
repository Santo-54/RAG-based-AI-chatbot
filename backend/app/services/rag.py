import os
import logging
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
try:
    from app.services.embedding import embedding_service
except ModuleNotFoundError:
    from services.embedding import embedding_service

load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "rag_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "documents")

        try:
            logger.info(f"Connecting to MongoDB at {self.mongo_uri}...")
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            # Test connection immediately
            self.client.server_info()
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.collection = None

    def add_document(self, text: str, metadata: dict = None) -> str:
        """
        Embeds a text fragment and stores it with its embedding in MongoDB.
        """
        if not self.collection:
            raise ConnectionError("MongoDB is not connected. Check your MONGO_URI configuration.")

        if not text or not text.strip():
            raise ValueError("Document text cannot be empty.")

        embedding = embedding_service.get_embedding(text)
        
        doc = {
            "text": text.strip(),
            "embedding": embedding,
            "metadata": metadata or {}
        }
        
        result = self.collection.insert_one(doc)
        logger.info(f"Successfully stored document {result.inserted_id} in MongoDB.")
        return str(result.inserted_id)

    def retrieve_documents(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Retrieves top_k documents most similar to the query.
        """
        if not self.collection:
            logger.warning("MongoDB not connected. Returning empty context.")
            return []

        # Step 1: Embed the query
        query_embedding = np.array(embedding_service.get_embedding(query))

        # Step 2: Fetch all stored documents
        # Note: In production with millions of documents, you would use Atlas Vector Search.
        # For standard MongoDB/local environments, we fetch and calculate in Python.
        cursor = self.collection.find({}, {"text": 1, "embedding": 1, "metadata": 1})
        documents = list(cursor)

        if not documents:
            logger.warning("No documents found in the database. Vector search skipped.")
            return []

        # Step 3: Compute Cosine Similarity
        scored_documents = []
        for doc in documents:
            doc_embedding = doc.get("embedding")
            if not doc_embedding:
                continue

            doc_emb_arr = np.array(doc_embedding)
            
            # Math formula: dot(A, B) / (norm(A) * norm(B))
            dot_product = np.dot(query_embedding, doc_emb_arr)
            norm_q = np.linalg.norm(query_embedding)
            norm_d = np.linalg.norm(doc_emb_arr)
            
            if norm_q == 0 or norm_d == 0:
                similarity = 0.0
            else:
                similarity = float(dot_product / (norm_q * norm_d))

            scored_documents.append({
                "id": str(doc["_id"]),
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
                "score": similarity
            })

        # Step 4: Sort by score descending and return top_k
        scored_documents.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_documents[:top_k]

        logger.info(f"Retrieved top {len(top_results)} documents for query.")
        return top_results

    def get_all_documents(self) -> list[dict]:
        """
        Retrieve all documents without embeddings for list/management view.
        """
        if not self.collection:
            return []
        cursor = self.collection.find({}, {"text": 1, "metadata": 1})
        return [{"id": str(doc["_id"]), "text": doc["text"], "metadata": doc.get("metadata", {})} for doc in cursor]

    def delete_document(self, doc_id: str) -> bool:
        """
        Deletes a document by its ID.
        """
        if not self.collection:
            return False
        from bson import ObjectId
        try:
            result = self.collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

rag_service = RAGService()
