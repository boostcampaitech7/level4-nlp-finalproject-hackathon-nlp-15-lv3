import os
import re
import torch
import numpy as np
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from transformers import AutoTokenizer, AutoModel
from typing import List

# ✅ 모델 불러오기
MODEL_NAME = "kakaobank/kf-deberta-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# ✅ ChromaDB 저장 경로 설정
CHROMA_DB_DIR = "/data/ephemeral/VectorDB/kffDB"

# ✅ 텍스트 전처리 함수
def clean_text(text):
    """불필요한 공백 및 특수문자 제거"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ✅ Mean Pooling 적용하여 문장 임베딩 생성
def mean_pooling(model_output, attention_mask):
    """Mean Pooling을 적용하여 문장 임베딩 생성"""
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

# ✅ DeBERTa를 사용하여 텍스트 임베딩 생성
def generate_text_embeddings(texts):
    """DeBERTa를 사용하여 문장 임베딩을 생성"""
    if isinstance(texts, str):
        texts = [texts]

    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        model_output = model(**inputs)
    
    embeddings = mean_pooling(model_output, inputs['attention_mask'])
    return embeddings.cpu().numpy().tolist()

# ✅ Chroma에서 사용할 커스텀 임베딩 함수 정의
class DeBERTaEmbeddingFunction(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return generate_text_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        return generate_text_embeddings(text)

# ✅ PDF에서 텍스트를 추출하고 ChromaDB에 저장하는 함수
def process_pdf_to_chromadb(pdf_path, collection_name):
    """PDF에서 텍스트를 추출하고 임베딩 생성 후 ChromaDB에 저장."""
    print(f"\n🔄 PDF 처리 시작: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    pdf_docs = loader.load()
    print(f"✅ PDF에서 {len(pdf_docs)}개의 페이지를 로드함.")

    text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=100)
    split_docs = []
    
    for doc in pdf_docs:
        cleaned_text = clean_text(doc.page_content)
        chunks = text_splitter.split_text(cleaned_text)
        for chunk in chunks:
            split_docs.append(Document(page_content=chunk, metadata=doc.metadata))

    print(f"✅ 총 {len(split_docs)}개의 텍스트 청크 생성됨.")

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=DeBERTaEmbeddingFunction(),
        persist_directory=CHROMA_DB_DIR,
    )

    texts = [doc.page_content for doc in split_docs]
    metadatas = [doc.metadata for doc in split_docs]

    if not texts:
        print("❌ 저장할 텍스트 데이터가 없습니다. PDF를 확인하세요.")
        return

    print("✅ 문서 임베딩 생성 중...")
    embeddings = generate_text_embeddings(texts)
    
    if not embeddings or np.all(np.array(embeddings) == 0):
        print("❌ 임베딩이 제대로 생성되지 않았습니다. 모델 또는 입력을 확인하세요.")
        return

    print(f"✅ 임베딩 생성 완료 (총 {len(embeddings)}개)")
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    vectorstore.persist()

    num_docs = vectorstore._collection.count()
    print(f"✅ 현재 ChromaDB에 저장된 문서 개수: {num_docs}")

    saved_data = vectorstore._collection.get(limit=3)
    print("✅ 저장된 데이터 샘플 (최대 3개):", saved_data.get("documents", []))

    print(f"✅ PDF {os.path.basename(pdf_path)} 처리 완료 및 저장됨.")

# ✅ 디렉토리 내 모든 PDF 파일 처리
def process_all_pdfs_in_directory(directory, collection_name):
    """지정된 디렉토리 내 모든 PDF 파일을 처리."""
    print(f"\n📂 디렉토리 내 PDF 처리 시작: {directory}")

    pdf_files = [os.path.join(root, file)
                 for root, _, files in os.walk(directory)
                 for file in files if file.endswith(".pdf")]

    if not pdf_files:
        print("❌ 처리할 PDF 파일이 없습니다.")
        return

    print(f"✅ 총 {len(pdf_files)}개의 PDF 파일 발견됨.")

    for pdf_path in pdf_files:
        process_pdf_to_chromadb(pdf_path, collection_name)
