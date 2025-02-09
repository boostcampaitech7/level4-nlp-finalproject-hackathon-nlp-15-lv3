from langchain.vectorstores import Chroma
from chromadb.config import Settings
from transformers import AutoTokenizer, AutoModel
import torch
from langchain.embeddings.base import Embeddings
from typing import List

# kakaobank/kf-deberta-base 모델 초기화
deberta_model_name = "kakaobank/kf-deberta-base"
tokenizer = AutoTokenizer.from_pretrained(deberta_model_name)
model = AutoModel.from_pretrained(deberta_model_name)

# ChromaDB 저장 경로
CHROMA_DB_DIR = "/data/ephemeral/VectorDB/kffDB"

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

# ChromaDB에서 검색 수행
def search_in_chromadb(query: str, collection_name: str, top_k: int = 3):
    """저장된 ChromaDB에서 검색하며, 유사도 필터 없이 상위 K개 결과 반환."""
    print("🔄 ChromaDB 연결 중...")

    # ChromaDB 로드
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=DeBERTaEmbeddingFunction(),
        persist_directory=CHROMA_DB_DIR,
    )

    # ✅ ChromaDB에 저장된 데이터 개수 확인
    num_docs = vectorstore._collection.count()
    print(f"✅ 현재 저장된 문서 개수: {num_docs}")

    if num_docs == 0:
        print("❌ ChromaDB에 저장된 데이터가 없습니다. 먼저 데이터를 추가하세요.")
        return []

    # ✅ 쿼리 임베딩 생성
    query_embedding = generate_text_embeddings([query])[0]
    print("✅ 생성된 쿼리 임베딩 길이:", len(query_embedding))

    # 🔍 유사한 문서 검색 수행
    results_with_scores = vectorstore._collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # ✅ 검색된 문서와 거리 값 확인
    documents = results_with_scores["documents"][0]

    print(f"✅ 검색된 문서 (최대 {top_k}개):", documents[:top_k])

    # ✅ 검색 결과 변환
    detailed_results = []
    for result in documents:
        answer = f"""
        🔍 검색된 문서:
        ----------------------------
        📜 **내용:** {result}  
        ----------------------------
        """
        detailed_results.append(answer)

    return detailed_results
