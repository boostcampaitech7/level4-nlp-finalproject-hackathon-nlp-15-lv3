from langchain_community.vectorstores import Chroma
from transformers import AutoTokenizer, AutoModel
import torch
from langchain.embeddings.base import Embeddings
from typing import List, Dict, Any
import logging
import numpy as np

from core.config import settings
from models import Document, RetrievalOutput  # Add this import
logger = logging.getLogger(__name__)


# kakaobank/kf-deberta-base 모델 초기화
deberta_model_name = "kakaobank/kf-deberta-base"
tokenizer = AutoTokenizer.from_pretrained(deberta_model_name)
model = AutoModel.from_pretrained(deberta_model_name)

# ChromaDB 저장 경로
CHROMA_DB_DIR = settings.vector_db["chroma_db_dir"]

class DeBERTaEmbeddingFunction(Embeddings):
    """DeBERTa를 이용한 ChromaDB 임베딩 함수"""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """문서 리스트를 입력받아 임베딩 벡터 리스트를 반환"""
        return generate_text_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        """검색 쿼리를 입력받아 임베딩 벡터를 반환"""
        return generate_text_embeddings([text])[0]

# DeBERTa를 사용하여 텍스트 임베딩 생성
def generate_text_embeddings(texts: List[str]) -> List[List[float]]:
    """DeBERTa를 사용하여 텍스트 임베딩 생성"""
    embeddings = []
    for text in texts:
        if not text.strip():
            embeddings.append([0] * 768)  # DeBERTa 임베딩 크기
            continue
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state[:, 0, :].squeeze().tolist())
    return embeddings

#FIXME 지나치게 높은 거리값
def l2_to_similarity(l2_distance: float) -> float:
    return 1 / (1 + l2_distance)

# ChromaDB에서 검색 수행
def search_in_chromadb(
    query: str, 
    collection_name: str = settings.collection_name, 
    top_k: int = 3
) -> RetrievalOutput:
    """저장된 ChromaDB에서 검색하며, 유사도 필터 없이 상위 K개 결과 반환."""
    try:
        logger.info("🔄 ChromaDB 연결 중...")
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=DeBERTaEmbeddingFunction(),
            persist_directory=CHROMA_DB_DIR,
        )

        num_docs = vectorstore._collection.count()
        logger.info(f"✅ {collection_name} 현재 저장된 문서 개수: {num_docs}")

        if num_docs == 0:
            logger.warning("❌ ChromaDB에 저장된 데이터가 없습니다.")
            return RetrievalOutput(
                id="empty",
                name="empty",
                group_id="empty",
                related_documents=[Document(
                    id="empty_doc",
                    text="현재 데이터베이스에 저장된 문서가 없습니다. 관리자에게 문의해주세요.",
                    metadata={},
                    score=0.0
                )]
            )

        # ✅ 쿼리 임베딩 생성
        query_embedding = generate_text_embeddings([query])[0]
        logger.info(f"✅ 생성된 쿼리 임베딩 길이: {len(query_embedding)}")

        # 유사한 문서 검색 수행
        results = vectorstore._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # 결과 변환
        documents = []
        for idx, (doc, distance) in enumerate(zip(results["documents"][0], results["distances"][0])):
            similarity = l2_to_similarity(distance)
            logger.info(f"Document {idx}: L2 distance = {distance:.4f}, Similarity = {similarity:.4f}")
            documents.append(Document(
                id=f"doc_{idx}",
                text=doc,
                metadata={},
                score=similarity  # 변환된 유사도 점수 사용
            ))

        return RetrievalOutput(
            id="search_result",
            name="search",
            group_id="search",
            related_documents=documents
        )

    except Exception as e:
        logger.error(f"ChromaDB 검색 중 오류 발생: {str(e)}")
        return RetrievalOutput(
            id="error",
            name="error",
            group_id="error",
            related_documents=[Document(
                id="error_doc",
                text="검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                metadata={},
                score=0.0
            )]
        )
