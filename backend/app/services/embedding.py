import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmbeddingService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Lazy initialization of the model
        if self._model is None:
            logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
            # This downloads and loads the model into memory
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer model loaded successfully.")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generate a 384-dimensional vector embedding for the input text.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")
        
        # Encode the text and return as a flat float list
        embedding_vector = self._model.encode(text).tolist()
        return embedding_vector

# Singleton instance to be imported across services
embedding_service = EmbeddingService()
