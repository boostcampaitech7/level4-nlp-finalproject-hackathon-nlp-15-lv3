from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class Utterance(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

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
    message: List[Utterance] = []
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

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat API Request Body"""
    uid: str
    conversation_id: str
    message: Utterance
    stream: bool = False  # 스트리밍 여부 (기본값: False)
    top_k: int = 3       # RAG 검색 결과 개수 (기본값: 3)
    option: Optional[Dict[str, Any]] = None # 추가 옵션

class ChatResponse(BaseModel):
    """Chat API Response Body"""
    answer: str
    context: str = ""
    conversation_id: str  # 대화 식별을 위한 ID
    uid: str             # 사용자 식별을 위한 ID

class ApiResponse(BaseModel):
    context: List[str]
    answer: str

class ApiRequest(BaseModel):
    """Simple API request with just a query"""
    query: str
    stream: bool = False
    top_k: int = 3