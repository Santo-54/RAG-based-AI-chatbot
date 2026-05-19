from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user query or message to send to the assistant.")

class ContextSource(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str = Field(..., description="The generated response from the Mistral AI model.")
    context: List[ContextSource] = Field(default=[], description="The list of retrieved documents used as context.")

class DocumentCreate(BaseModel):
    text: str = Field(..., description="The text content of the document to embed and store.")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata to store with the document.")

class DocumentCreateResponse(BaseModel):
    id: str = Field(..., description="The unique database ID of the inserted document.")
    message: str = Field(default="Document successfully ingested.")

class DocumentListResponse(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
