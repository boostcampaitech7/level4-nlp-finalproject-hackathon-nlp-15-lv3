from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from transformers import AutoTokenizer, AutoModel
import torch

# FastAPI 앱 생성
app = FastAPI()

# kakaobank/kf-deberta-base 모델 초기화
deberta_model_name = "kakaobank/kf-deberta-base"
tokenizer = AutoTokenizer.from_pretrained(deberta_model_name)
model = AutoModel.from_pretrained(deberta_model_name)

# ChromaDB 저장 경로
CHROMA_DB_DIR = "/data/ephemeral/VectorDB/kffDB"

# 검색 요청 데이터 모델
class SearchRequest(BaseModel):
    query: str
    collection_name: str = "pdf_text_collection"
    top_k: int = 3

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

# 검색 함수
def search_in_chromadb(query: str, collection_name: str, top_k: int = 3):
    """저장된 ChromaDB에서 검색하여 상위 K개 결과 반환"""
    print("🔄 ChromaDB 연결 중...")

    # ChromaDB 로드
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DB_DIR,
    )

    # 저장된 데이터 개수 확인
    num_docs = vectorstore._collection.count()
    print(f"✅ 현재 저장된 문서 개수: {num_docs}")

    if num_docs == 0:
        return {"error": "ChromaDB에 저장된 데이터가 없습니다."}

    # 쿼리 임베딩 생성
    query_embedding = generate_text_embeddings([query])[0]

    # 유사한 문서 검색 수행
    results_with_scores = vectorstore._collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 검색된 문서 반환
    documents = results_with_scores["documents"][0]
    return {"query": query, "results": documents[:top_k]}

# API 엔드포인트 정의
@app.post("/retrieval")
def retrieval(request: SearchRequest):
    """검색 API 엔드포인트"""
    results = search_in_chromadb(request.query, request.collection_name, request.top_k)
    return results
