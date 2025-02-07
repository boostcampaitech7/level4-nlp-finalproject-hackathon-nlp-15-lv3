from typing import List, Dict, Any

from pydantic import BaseModel


class Utterance(BaseModel):
    role: str
    content: str

class Document(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float = 0.0

class Identification(BaseModel):
    id: str
    name: str
    group_id: str

class IndexingItem(Identification):
    documents: List[Document] = []
    max_chunk_size: int = 1024
    num_chunk_overlap: int = 256

class IndexingOutput(Identification):
    is_success: bool

class RetrievalItem(Identification):
    query: str
    max_query_size: int = 1024
    top_k: int = 3

class RetrievalOutput(Identification):
    related_documents: List[Document] = []

class ChatItem(Identification):
    messages: List[Utterance] = []
    max_query_size: int = 1024
    max_response_size: int = 4096
    top_k: int = 3
    stream: bool = False
# ChatOutput is not defined here, but it is defined in the API server code directly.

"""
class GenItem(ChatItem):
    query: str

class GenOutput(Identification):
    answer: str
    context: str
"""

class WebItem():
    query: str

class WebOutput(Identification):
    context: List

class RagItem(ChatItem):
    query: str

class RagOutput(Identification):
    answer: str
    context: str
   